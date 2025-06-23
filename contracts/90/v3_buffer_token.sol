// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title AutoBufferPoolSellerV3MultiOracle
 * @notice 基于Uniswap V3多预言机，自动缓冲池，防价格操纵，多跳交易，丰富事件监控
 */

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

// address quoters0 = 0xb27308f9F90D607463bb33eA1BeBb41C27CE5AB6; // Uniswap V3 Mainnet Quoter
// address quoters1 = 0x61fFE014bA17989E743c5F6cB21bF9697530B21e; // Uniswap V3 Goerli Quoter (示例，主网不适用)

// AutoBufferPoolSellerV3MultiOracle contractInstance = new AutoBufferPoolSellerV3MultiOracle(
//     [quoters0, quoters1], // 多预言机地址列表
//     swapRouterAddress,
//     tokenAddress,
//     stableTokenAddress,
//     500,       // lockRate 5%
//     5000,      // releaseRate 50%
//     7000,      // priceDropThreshold 70% (跌30%)
//     2000       // priceJumpThreshold 20%价格跳变报警阈值
// );

interface IUniswapV3Quoter {
    function quoteExactInput(
        bytes memory path,
        uint256 amountIn
    ) external returns (uint256 amountOut);
    function quoteExactInputSingle(
        address tokenIn,
        address tokenOut,
        uint24 fee,
        uint256 amountIn,
        uint160 sqrtPriceLimitX96
    ) external returns (uint256 amountOut);
}

interface IUniswapV3SwapRouter {
    struct ExactInputParams {
        bytes path;
        address recipient;
        uint256 deadline;
        uint256 amountIn;
        uint256 amountOutMinimum;
    }

    function exactInput(
        ExactInputParams calldata params
    ) external payable returns (uint256 amountOut);
}

interface IBurnableToken is IERC20 {
    function burn(uint256 amount) external;
}

contract AutoBufferPoolSellerV3MultiOracle is Ownable {
    // 多预言机接口地址列表，支持多源查询
    IUniswapV3Quoter[] public quoters;

    IUniswapV3SwapRouter public immutable swapRouter;
    IBurnableToken public immutable token;
    IERC20 public immutable stableToken;

    // 缓冲池余额，单位稳定币
    uint public bufferPool;

    // 买入锁定比例，10000=100%
    uint public lockRate;

    // 缓冲池释放比例，10000=100%
    uint public releaseRate;

    // 触发价格跌幅阈值，10000=100%
    uint public priceDropThreshold;

    // 当天最高价（稳定币/Token）
    uint public dailyHighPrice;

    // 上次更新时间（UTC天数）
    uint public lastPriceUpdateDay;

    // 价格异常阈值，判断价格突变报警，单位10000
    uint public priceJumpThreshold;

    // 事件
    event BufferPoolReleased(
        uint amountStableUsed,
        uint tokensBurned,
        uint timestamp
    );
    event DailyHighPriceUpdated(uint day, uint newHighPrice);
    event Buy(
        address indexed user,
        uint paidStable,
        uint lockedAmount,
        uint tokensReceived
    );
    event Sell(address indexed user, uint tokensSold, uint stableReceived);
    event PriceAnomalyDetected(uint oldPrice, uint newPrice, uint timestamp);
    event BufferPoolChanged(uint oldBalance, uint newBalance, uint timestamp);

    /**
     * @param _quoters 多个Uniswap V3 Quoter合约地址数组，建议2个及以上，防单点风险
     * @param _swapRouter Uniswap V3 SwapRouter合约地址
     * @param _token 目标Token地址
     * @param _stableToken 稳定币地址
     * @param _lockRate 买入锁定比例
     * @param _releaseRate 缓冲池释放比例
     * @param _priceDropThreshold 价格跌幅触发阈值
     * @param _priceJumpThreshold 价格跳变报警阈值，用于检测价格异常
     */
    constructor(
        address[] memory _quoters,
        address _swapRouter,
        address _token,
        address _stableToken,
        uint _lockRate,
        uint _releaseRate,
        uint _priceDropThreshold,
        uint _priceJumpThreshold
    ) Ownable(msg.sender) {
        require(_quoters.length >= 1, "At least one quoter required");
        for (uint i = 0; i < _quoters.length; i++) {
            quoters.push(IUniswapV3Quoter(_quoters[i]));
        }

        swapRouter = IUniswapV3SwapRouter(_swapRouter);
        token = IBurnableToken(_token);
        stableToken = IERC20(_stableToken);

        require(
            _lockRate <= 10000 &&
                _releaseRate <= 10000 &&
                _priceDropThreshold <= 10000 &&
                _priceJumpThreshold <= 10000,
            "Params max 10000"
        );
        lockRate = _lockRate;
        releaseRate = _releaseRate;
        priceDropThreshold = _priceDropThreshold;
        priceJumpThreshold = _priceJumpThreshold;

        lastPriceUpdateDay = block.timestamp / 1 days;
        dailyHighPrice = _getSafePrice();
    }

    /**
     * @notice 获取安全价格，轮询所有预言机，取最小值防止价格被高估
     * @dev 路径固定为单跳：token->stable，fee 0.3% (3000)
     * @return 价格 单位稳定币/Token 18 decimals
     */
    function _getSafePrice() internal returns (uint) {
        uint price = type(uint).max; // 初始化为最大
        address tokenAddr = address(token);
        address stableAddr = address(stableToken);
        uint24 fee = 3000;

        for (uint i = 0; i < quoters.length; i++) {
            uint quotedPrice;
            try
                quoters[i].quoteExactInputSingle(
                    tokenAddr,
                    stableAddr,
                    fee,
                    1e18,
                    0
                )
            returns (uint amountOut) {
                quotedPrice = amountOut;
            } catch {
                // 某个预言机调用失败忽略
                continue;
            }
            if (quotedPrice < price && quotedPrice != 0) {
                price = quotedPrice;
            }
        }
        require(price != type(uint).max, "No valid price from oracles");
        return price;
    }

    /// @notice 更新每日最高价，监测价格异常
    function _updateDailyHighPrice() internal {
        uint currentDay = block.timestamp / 1 days;
        uint currentPrice = _getSafePrice();

        // 价格异常检测：当天最高价和新价格跳变比例超过阈值触发事件
        if (dailyHighPrice > 0) {
            uint changeRatio = currentPrice > dailyHighPrice
                ? (currentPrice * 10000) / dailyHighPrice
                : (dailyHighPrice * 10000) / currentPrice;
            if (changeRatio > priceJumpThreshold) {
                emit PriceAnomalyDetected(
                    dailyHighPrice,
                    currentPrice,
                    block.timestamp
                );
            }
        }

        if (currentDay > lastPriceUpdateDay) {
            dailyHighPrice = currentPrice;
            lastPriceUpdateDay = currentDay;
            emit DailyHighPriceUpdated(currentDay, currentPrice);
        } else if (currentPrice > dailyHighPrice) {
            dailyHighPrice = currentPrice;
            emit DailyHighPriceUpdated(currentDay, currentPrice);
        }
    }

    /// @notice 获取当前安全价格，外部调用接口
    function getCurrentPrice() external returns (uint) {
        return _getSafePrice();
    }

    /**
     * @notice 买入token，锁定部分资金入缓冲池，使用多跳路径交易
     * @param stableAmount 用户支付稳定币数量
     * @param amountOutMin 用户期望最小token数量
     * @param path 多跳交易路径编码，需以稳定币开头、Token结尾
     */
    function buyToken(
        uint stableAmount,
        uint amountOutMin,
        bytes calldata path
    ) external {
        require(stableAmount > 0, "Amount must > 0");

        _updateDailyHighPrice();

        uint lockedAmount = (stableAmount * lockRate) / 10000;
        uint usableAmount = stableAmount - lockedAmount;

        require(
            stableToken.transferFrom(msg.sender, address(this), stableAmount),
            "Stable transfer failed"
        );

        uint oldBufferPool = bufferPool;
        bufferPool += lockedAmount;
        emit BufferPoolChanged(oldBufferPool, bufferPool, block.timestamp);

        require(
            stableToken.approve(address(swapRouter), usableAmount),
            "Approve failed"
        );

        IUniswapV3SwapRouter.ExactInputParams
            memory params = IUniswapV3SwapRouter.ExactInputParams({
                path: path,
                recipient: msg.sender,
                deadline: block.timestamp + 300,
                amountIn: usableAmount,
                amountOutMinimum: amountOutMin
            });

        uint amountOut = swapRouter.exactInput(params);
        emit Buy(msg.sender, stableAmount, lockedAmount, amountOut);
    }

    /**
     * @notice 卖出Token，兑换稳定币，多跳路径
     * @param tokenAmount 卖出Token数量
     * @param amountOutMin 最小接受稳定币数量
     * @param path 多跳路径编码，需以Token开头、稳定币结尾
     */
    function sellToken(
        uint tokenAmount,
        uint amountOutMin,
        bytes calldata path
    ) external {
        require(tokenAmount > 0, "Amount must > 0");

        _updateDailyHighPrice();

        require(
            token.transferFrom(msg.sender, address(this), tokenAmount),
            "Token transfer failed"
        );

        require(
            token.approve(address(swapRouter), tokenAmount),
            "Approve failed"
        );

        IUniswapV3SwapRouter.ExactInputParams
            memory params = IUniswapV3SwapRouter.ExactInputParams({
                path: path,
                recipient: msg.sender,
                deadline: block.timestamp + 300,
                amountIn: tokenAmount,
                amountOutMinimum: amountOutMin
            });

        uint amountOut = swapRouter.exactInput(params);
        emit Sell(msg.sender, tokenAmount, amountOut);

        tryAutoRelease();
    }

    /// @notice 自动释放缓冲池资金，回购销毁token
    function tryAutoRelease() public {
        uint currentPrice = _getSafePrice();

        if (
            currentPrice * 10000 < dailyHighPrice * priceDropThreshold &&
            bufferPool > 0
        ) {
            uint releaseAmount = (bufferPool * releaseRate) / 10000;
            uint oldBufferPool = bufferPool;
            bufferPool -= releaseAmount;
            emit BufferPoolChanged(oldBufferPool, bufferPool, block.timestamp);

            require(
                stableToken.approve(address(swapRouter), releaseAmount),
                "Approve failed"
            );

            // 构造单跳路径：稳定币->Token，手续费0.3%
            bytes memory singleHopPath = abi.encodePacked(
                address(stableToken),
                uint24(3000),
                address(token)
            );

            IUniswapV3SwapRouter.ExactInputParams
                memory params = IUniswapV3SwapRouter.ExactInputParams({
                    path: singleHopPath,
                    recipient: address(this),
                    deadline: block.timestamp + 300,
                    amountIn: releaseAmount,
                    amountOutMinimum: 0
                });

            uint amountOut = swapRouter.exactInput(params);
            token.burn(amountOut);

            emit BufferPoolReleased(releaseAmount, amountOut, block.timestamp);
        }
    }

    // --- 管理员接口 ---

    function addQuoter(address quoterAddr) external onlyOwner {
        quoters.push(IUniswapV3Quoter(quoterAddr));
    }

    function removeQuoter(uint index) external onlyOwner {
        require(index < quoters.length, "Index out of range");
        quoters[index] = quoters[quoters.length - 1];
        quoters.pop();
    }

    function setLockRate(uint newRate) external onlyOwner {
        require(newRate <= 10000, "LockRate max 100%");
        lockRate = newRate;
    }

    function setReleaseRate(uint newRate) external onlyOwner {
        require(newRate <= 10000, "ReleaseRate max 100%");
        releaseRate = newRate;
    }

    function setPriceDropThreshold(uint newThreshold) external onlyOwner {
        require(newThreshold <= 10000, "Threshold max 100%");
        priceDropThreshold = newThreshold;
    }

    function setPriceJumpThreshold(uint newThreshold) external onlyOwner {
        require(newThreshold <= 10000, "Threshold max 100%");
        priceJumpThreshold = newThreshold;
    }

    function emergencyWithdrawStable(
        uint amount,
        address to
    ) external onlyOwner {
        require(amount <= bufferPool, "Amount too big");
        uint oldBalance = bufferPool;
        bufferPool -= amount;
        emit BufferPoolChanged(oldBalance, bufferPool, block.timestamp);
        require(stableToken.transfer(to, amount), "Transfer failed");
    }
}
