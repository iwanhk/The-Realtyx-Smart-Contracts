// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts-upgradeable/access/AccessControlUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

interface IUniswapV2Router {
    function getAmountsOut(
        uint amountIn,
        address[] calldata path
    ) external view returns (uint[] memory amounts);
    function swapExactTokensForTokens(
        uint amountIn,
        uint amountOutMin,
        address[] calldata path,
        address to,
        uint deadline
    ) external returns (uint[] memory amounts);
}

contract BufferedSellerUpgradeable is Initializable, AccessControlUpgradeable {
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    bytes32 public constant AUDITOR_ROLE = keccak256("AUDITOR_ROLE");

    IUniswapV2Router public router;
    uint public priceBuffer; // 价格缓冲，10000 = 100%
    uint public dailyDropLimit; // 日最大跌幅，单位10000，如9500=跌不超过5%
    uint public lastRecordedDay; // 最近记录价格的天数 (UTC0)
    uint public dailyFloorPrice; // 当天最低价格限制

    // EIP-712 域分隔符
    bytes32 public DOMAIN_SEPARATOR;
    bytes32 public constant SELL_TYPEHASH =
        keccak256("Sell(address seller,uint256 amount,uint256 deadline)");

    // token和交易路径
    address public token;
    address public stableToken;
    address[] public path;

    event Sold(
        address indexed seller,
        uint amountIn,
        uint amountOut,
        uint timestamp
    );
    event PriceBufferChanged(uint oldBuffer, uint newBuffer);
    event DailyDropLimitChanged(uint oldLimit, uint newLimit);
    event FloorPriceUpdated(uint day, uint newFloorPrice);

    function initialize(
        address _router,
        address _token,
        address _stableToken,
        uint _priceBuffer,
        uint _dailyDropLimit,
        address admin
    ) public initializer {
        __AccessControl_init();

        router = IUniswapV2Router(_router);
        token = _token;
        stableToken = _stableToken;
        priceBuffer = _priceBuffer;
        dailyDropLimit = _dailyDropLimit;

        path = new address[](2);
        path[0] = _token;
        path[1] = _stableToken;

        _setupRole(DEFAULT_ADMIN_ROLE, admin);
        _setupRole(ADMIN_ROLE, admin);

        // 计算DOMAIN_SEPARATOR
        DOMAIN_SEPARATOR = keccak256(
            abi.encode(
                keccak256(
                    "EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)"
                ),
                keccak256(bytes("BufferedSeller")),
                keccak256(bytes("1")),
                block.chainid,
                address(this)
            )
        );

        // 初始化当天价格
        lastRecordedDay = block.timestamp / 1 days;
        dailyFloorPrice = getCurrentPrice();
    }

    // 读取当前单token价格(稳定币计价)
    function getCurrentPrice() public view returns (uint) {
        uint[] memory amounts = router.getAmountsOut(1e18, path);
        return amounts[amounts.length - 1];
    }

    // 更新每日底价（只能ADMIN或AUDITOR调用）
    function updateDailyFloorPrice() external onlyRole(ADMIN_ROLE) {
        uint currentDay = block.timestamp / 1 days;
        require(currentDay > lastRecordedDay, "Already updated today");

        uint price = getCurrentPrice();
        // 计算当天底价 = max(昨天底价 * 日跌幅限制, 当前价格)
        uint newFloor = (dailyFloorPrice * dailyDropLimit) / 10000;
        if (price > newFloor) {
            newFloor = price;
        }

        dailyFloorPrice = newFloor;
        lastRecordedDay = currentDay;
        emit FloorPriceUpdated(currentDay, newFloor);
    }

    // 用户卖出（需签名验证）
    function sellToken(
        uint amountIn,
        uint amountOutMin,
        uint deadline,
        bytes calldata signature
    ) external {
        require(block.timestamp <= deadline, "Signature expired");

        // 验证签名是否由AUDITOR_ROLE授权
        bytes32 structHash = keccak256(
            abi.encode(SELL_TYPEHASH, msg.sender, amountIn, deadline)
        );
        bytes32 digest = keccak256(
            abi.encodePacked("\x19\x01", DOMAIN_SEPARATOR, structHash)
        );
        address signer = recoverSigner(digest, signature);

        require(hasRole(AUDITOR_ROLE, signer), "Invalid auditor signature");

        // 检查每日跌幅限制
        uint priceBefore = getCurrentPrice();
        uint priceAfter = estimatePriceAfterSell(amountIn);
        require(
            priceAfter * 10000 >= dailyFloorPrice * priceBuffer,
            "Price impact violates floor or buffer"
        );

        // 转账 & 授权
        require(
            IERC20(token).transferFrom(msg.sender, address(this), amountIn),
            "Transfer failed"
        );
        require(
            IERC20(token).approve(address(router), amountIn),
            "Approve failed"
        );

        // 执行swap
        router.swapExactTokensForTokens(
            amountIn,
            amountOutMin,
            path,
            msg.sender,
            block.timestamp + 300
        );

        emit Sold(msg.sender, amountIn, priceAfter, block.timestamp);
    }

    // 估算卖出后价格
    function estimatePriceAfterSell(
        uint amountIn
    ) internal view returns (uint) {
        uint[] memory amounts = router.getAmountsOut(amountIn, path);
        uint estimatedOut = amounts[amounts.length - 1];
        return (estimatedOut * 1e18) / amountIn;
    }

    // ECDSA签名恢复
    function recoverSigner(
        bytes32 digest,
        bytes memory signature
    ) internal pure returns (address) {
        require(signature.length == 65, "Invalid signature length");
        bytes32 r;
        bytes32 s;
        uint8 v;
        assembly {
            r := mload(add(signature, 32))
            s := mload(add(signature, 64))
            v := byte(0, mload(add(signature, 96)))
        }
        if (v < 27) {
            v += 27;
        }
        require(v == 27 || v == 28, "Invalid signature 'v' value");
        return ecrecover(digest, v, r, s);
    }

    // 管理员可调节价格缓冲
    function setPriceBuffer(uint newBuffer) external onlyRole(ADMIN_ROLE) {
        require(newBuffer <= 10000, "Buffer max 10000");
        emit PriceBufferChanged(priceBuffer, newBuffer);
        priceBuffer = newBuffer;
    }

    // 管理员可调节日跌幅限制
    function setDailyDropLimit(uint newLimit) external onlyRole(ADMIN_ROLE) {
        require(newLimit <= 10000, "Limit max 10000");
        emit DailyDropLimitChanged(dailyDropLimit, newLimit);
        dailyDropLimit = newLimit;
    }

    // 权限管理接口方便扩展
}
