// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

// 引入Ownable，用于权限控制，只有合约拥有者可以调用某些函数
import "@openzeppelin/contracts/access/Ownable.sol";
// ERC20接口
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

// Uniswap V2 路由器接口，主要用于获取价格和执行兑换交易
interface IUniswapV2Router {
    // 查询给定输入金额对应的输出金额，path是兑换路径
    function getAmountsOut(
        uint amountIn,
        address[] calldata path
    ) external view returns (uint[] memory amounts);

    // 以准确输入金额兑换代币，支持多跳交易
    function swapExactTokensForTokens(
        uint amountIn,
        uint amountOutMin, // 最小输出，防止滑点
        address[] calldata path,
        address to,
        uint deadline // 交易截止时间戳
    ) external returns (uint[] memory amounts);
}

// 扩展ERC20接口，增加burn方法，用于销毁代币
interface IBurnableToken is IERC20 {
    function burn(uint256 amount) external;
}

contract AutoBufferPoolSeller is Ownable {
    // Uniswap路由合约地址
    IUniswapV2Router public router;
    // 目标交易的Token，要求支持burn销毁
    IBurnableToken public token;
    // 稳定币地址（如USDT、USDC或WETH），用于计价和锁定资金
    address public stableToken;

    // 兑换路径，稳定币 -> Token
    address[] public path;
    // 兑换路径反转，Token -> 稳定币
    address[] public reversePath;

    // 缓冲池余额，单位是稳定币
    uint public bufferPool;
    // 买入时锁定比例，10000 = 100%，例如500 = 5%
    uint public lockRate;
    // 缓冲池释放比例，10000 = 100%，比如5000 = 50%
    uint public releaseRate;
    // 触发释放的价格跌幅阈值，单位10000，如7000代表跌30%
    uint public priceDropThreshold;

    // 记录当天最高价，单位为稳定币/Token（18位精度）
    uint public dailyHighPrice;
    // 上次更新最高价的“天数”，通过区块时间/86400计算
    uint public lastPriceUpdateDay;

    // 事件，缓冲池释放时触发，记录释放金额和买回销毁代币数量
    event BufferPoolReleased(
        uint amountStableUsed,
        uint tokensBurned,
        uint timestamp
    );
    // 事件，记录当天最高价更新
    event DailyHighPriceUpdated(uint day, uint newHighPrice);
    // 买入事件
    event Buy(
        address indexed user,
        uint paidStable,
        uint lockedAmount,
        uint tokensReceived
    );
    // 卖出事件
    event Sell(address indexed user, uint tokensSold, uint stableReceived);

    /**
     * @param _router Uniswap V2 路由合约地址
     * @param _token 目标Token地址，需支持burn
     * @param _stableToken 稳定币地址
     * @param _lockRate 买入时锁定资金比例 (10000为100%)
     * @param _releaseRate 缓冲池释放比例 (10000为100%)
     * @param _priceDropThreshold 触发释放的价格跌幅阈值 (10000为100%)
     */
    constructor(
        address _router,
        address _token,
        address _stableToken,
        uint _lockRate,
        uint _releaseRate,
        uint _priceDropThreshold
    ) Ownable(msg.sender) {
        require(
            _lockRate <= 10000 &&
                _releaseRate <= 10000 &&
                _priceDropThreshold <= 10000,
            "Invalid params"
        );

        router = IUniswapV2Router(_router);
        token = IBurnableToken(_token);
        stableToken = _stableToken;

        lockRate = _lockRate;
        releaseRate = _releaseRate;
        priceDropThreshold = _priceDropThreshold;

        // 设置兑换路径，稳定币兑换Token
        path = new address[](2);
        path[0] = stableToken;
        path[1] = _token;

        // 反转兑换路径，Token兑换稳定币
        reversePath = new address[](2);
        reversePath[0] = _token;
        reversePath[1] = stableToken;

        // 初始化当天价格及时间标记
        lastPriceUpdateDay = block.timestamp / 1 days;
        dailyHighPrice = getCurrentPrice();
    }

    /**
     * @notice 获取当前Token价格，单位为稳定币/Token，精度18位
     * @return 当前价格（1 Token对应多少稳定币）
     */
    function getCurrentPrice() public view returns (uint) {
        // 通过Uniswap路由获取兑换价格
        uint[] memory amounts = router.getAmountsOut(1e18, reversePath);
        return amounts[amounts.length - 1];
    }

    /**
     * @dev 内部方法，自动更新当天最高价
     * 根据区块时间判断是否新的一天
     * 若是新的一天，重置最高价
     * 否则若当前价高于最高价，则更新最高价
     */
    function _updateDailyHighPrice() internal {
        uint currentDay = block.timestamp / 1 days;
        uint currentPrice = getCurrentPrice();

        if (currentDay > lastPriceUpdateDay) {
            // 新的一天，重置最高价为当前价格
            dailyHighPrice = currentPrice;
            lastPriceUpdateDay = currentDay;
            emit DailyHighPriceUpdated(currentDay, currentPrice);
        } else if (currentPrice > dailyHighPrice) {
            // 当天更新最高价
            dailyHighPrice = currentPrice;
            emit DailyHighPriceUpdated(currentDay, currentPrice);
        }
    }

    /**
     * @notice 用户买入Token接口
     * @param stableAmount 用户支付的稳定币数量
     * @param amountOutMin 用户期望最小获得Token数量（防止滑点）
     */
    function buyToken(uint stableAmount, uint amountOutMin) external {
        require(stableAmount > 0, "Amount must > 0");

        // 更新当天最高价
        _updateDailyHighPrice();

        // 计算锁定金额和可用买币金额
        uint lockedAmount = (stableAmount * lockRate) / 10000;
        uint usableAmount = stableAmount - lockedAmount;

        // 从用户转入稳定币
        require(
            IERC20(stableToken).transferFrom(
                msg.sender,
                address(this),
                stableAmount
            ),
            "Transfer stable failed"
        );

        // 增加缓冲池余额
        bufferPool += lockedAmount;

        // 授权Uniswap路由花费稳定币进行兑换
        require(
            IERC20(stableToken).approve(address(router), usableAmount),
            "Approve failed"
        );

        // 兑换稳定币买Token，发给用户
        uint[] memory amounts = router.swapExactTokensForTokens(
            usableAmount,
            amountOutMin,
            path,
            msg.sender,
            block.timestamp + 300
        );

        emit Buy(
            msg.sender,
            stableAmount,
            lockedAmount,
            amounts[amounts.length - 1]
        );
    }

    /**
     * @notice 用户卖出Token接口
     * @param tokenAmount 用户卖出的Token数量
     * @param amountOutMin 用户期望最小获得稳定币数量（防止滑点）
     */
    function sellToken(uint tokenAmount, uint amountOutMin) external {
        require(tokenAmount > 0, "Amount must > 0");

        // 更新当天最高价
        _updateDailyHighPrice();

        // 从用户转入Token
        require(
            token.transferFrom(msg.sender, address(this), tokenAmount),
            "Transfer failed"
        );

        // 授权Uniswap路由花费Token进行兑换
        require(token.approve(address(router), tokenAmount), "Approve failed");

        // 兑换Token换稳定币，发给用户
        uint[] memory amounts = router.swapExactTokensForTokens(
            tokenAmount,
            amountOutMin,
            reversePath,
            msg.sender,
            block.timestamp + 300
        );

        emit Sell(msg.sender, tokenAmount, amounts[amounts.length - 1]);

        // 卖出后尝试自动释放缓冲池资金，稳定价格
        tryAutoRelease();
    }

    /**
     * @notice 自动释放缓冲池资金
     * 满足价格跌幅超过阈值时，释放一定比例资金回购Token并销毁
     * 可由任何人调用，保证及时释放
     */
    function tryAutoRelease() public {
        uint currentPrice = getCurrentPrice();

        // 判断当前价格是否低于阈值（如跌30%），且缓冲池有资金
        if (
            currentPrice * 10000 < dailyHighPrice * priceDropThreshold &&
            bufferPool > 0
        ) {
            // 计算释放金额，比如释放缓冲池50%
            uint releaseAmount = (bufferPool * releaseRate) / 10000;
            bufferPool -= releaseAmount;

            // 授权Uniswap路由使用释放的稳定币进行买Token
            require(
                IERC20(stableToken).approve(address(router), releaseAmount),
                "Approve failed"
            );

            // 用释放的稳定币买Token，买到的Token留在合约中
            uint[] memory amounts = router.swapExactTokensForTokens(
                releaseAmount,
                0, // 不设最小，适应滑点（可根据实际需求调整）
                path,
                address(this),
                block.timestamp + 300
            );

            uint tokensBought = amounts[amounts.length - 1];

            // 调用token合约销毁买回的Token，减少流通量支撑价格
            token.burn(tokensBought);

            emit BufferPoolReleased(
                releaseAmount,
                tokensBought,
                block.timestamp
            );
        }
    }

    // ----- 管理员权限函数 -----

    /// @notice 调整买入锁定资金比例
    function setLockRate(uint newRate) external onlyOwner {
        require(newRate <= 10000, "LockRate max 100%");
        lockRate = newRate;
    }

    /// @notice 调整缓冲池释放比例
    function setReleaseRate(uint newRate) external onlyOwner {
        require(newRate <= 10000, "ReleaseRate max 100%");
        releaseRate = newRate;
    }

    /// @notice 调整触发释放的价格跌幅阈值
    function setPriceDropThreshold(uint newThreshold) external onlyOwner {
        require(newThreshold <= 10000, "Threshold max 100%");
        priceDropThreshold = newThreshold;
    }

    /// @notice 紧急情况下管理员提取缓冲池稳定币资金
    function emergencyWithdrawStable(
        uint amount,
        address to
    ) external onlyOwner {
        require(amount <= bufferPool, "Amount too big");
        bufferPool -= amount;
        require(IERC20(stableToken).transfer(to, amount), "Transfer failed");
    }
}
