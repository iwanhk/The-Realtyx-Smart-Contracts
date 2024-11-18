// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts-upgradeable/token/ERC20/ERC20Upgradeable.sol";
import "@openzeppelin/contracts-upgradeable/token/ERC20/extensions/ERC20BurnableUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/security/PausableUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/access/AccessControlUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/UUPSUpgradeable.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";


contract plumeARst is
    Initializable,
    ERC20Upgradeable,
    ERC20BurnableUpgradeable,
    PausableUpgradeable,
    AccessControlUpgradeable,
    UUPSUpgradeable
{
    using SafeERC20 for IERC20;

    bytes32 public constant PAUSER_ROLE = keccak256("PAUSER_ROLE");
    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");
    bytes32 public constant UPGRADER_ROLE = keccak256("UPGRADER_ROLE");
    address public ASSETADDRESS;
    address public PLUMEADDRESS;
    /// @custom:oz-upgrades-unsafe-allow constructor
    event mintARst(address indexed sender, uint256 rstAmount ,uint256 timestamp);
    // constructor() {
    //     _disableInitializers();
    // }

    function initialize(
        string memory name,
        string memory symbol,
        address owner,
        address assetAddress,
        address plumeAddress
    ) public initializer {
        __ERC20_init(name, symbol);
        __ERC20Burnable_init();
        __AccessControl_init();
        __UUPSUpgradeable_init();
        _grantRole(PAUSER_ROLE, owner);
        _grantRole(MINTER_ROLE, owner);
        _grantRole(DEFAULT_ADMIN_ROLE, owner);
        _grantRole(UPGRADER_ROLE, owner);
        ASSETADDRESS = assetAddress;
        PLUMEADDRESS = plumeAddress;
    }

    function pause() external onlyRole(PAUSER_ROLE) {
        _pause();
    }

    function unpause() external onlyRole(PAUSER_ROLE) {
        _unpause();
    }

    function mint(uint256 amount) public whenNotPaused {
        require(
            IERC20(ASSETADDRESS).balanceOf(msg.sender) >= amount,
            "Not enough assets"
        );

        require(
            IERC20(ASSETADDRESS).allowance(msg.sender, address(this)) >= amount,
            "Not enough allowance"
        );

        IERC20(ASSETADDRESS).safeTransferFrom(
            msg.sender,
            address(this),
            amount
        );

        _mint(msg.sender, amount);

        emit mintARst(msg.sender, amount, block.timestamp);

    }

    function burn(uint256 amount) public override whenNotPaused {

        uint256 _amount = balanceOf(msg.sender);

        require(_amount >= amount, "Not enough assets");

        _burn(msg.sender, amount);

        IERC20(ASSETADDRESS).safeTransfer(msg.sender, amount);
    }

    function burnFrom(address account, uint256 amount) public override whenNotPaused {

    }

    
    function _authorizeUpgrade(
        address newImplementation
    ) internal override onlyRole(UPGRADER_ROLE) {}

    function getCurrentTime() internal view virtual returns (uint256) {
        return block.timestamp;
    }
}
