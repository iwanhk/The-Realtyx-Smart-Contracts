// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.22;

import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {OFTAdapter} from "@layerzerolabs/lz-evm-oapp-v2/contracts/oft/OFTAdapter.sol";

contract wRstBridge is OFTAdapter {
    constructor(
        address _token,
        address _lzEndpoint,
        address _delegate
    ) OFTAdapter(_token, _lzEndpoint, _delegate) Ownable() {}

    function retrieve(address _token, uint256 _amount) external onlyOwner {
        IERC20 token = IERC20(_token);
        require(
            token.balanceOf(address(this)) >= _amount,
            "Insufficient balance in contract"
        );
        bool success = token.transfer(owner(), _amount);
        require(success, "Transfer failed");
    }
}
