// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.22;

import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";
import {OFT} from "@layerzerolabs/lz-evm-oapp-v2/contracts/oft/OFT.sol";

interface RealToken {
    function isKYCVerified(address param) external view returns (bool); 
}

contract wRstBridgeToken is OFT {

    address public kycStoreAddress;
    RealToken private kycStore;

    constructor(
        string memory _name,
        string memory _symbol,
        address _lzEndpoint,
        address _delegate,
        address _kycStoreAddress
    ) OFT(_name, _symbol, _lzEndpoint, _delegate) Ownable() {
        kycStoreAddress = _kycStoreAddress;
        kycStore = RealToken(_kycStoreAddress);
    }

    function _beforeTokenTransfer(
        address _from,
        address _to,
        uint256 _amount
    ) internal override {

        require(
            kycStoreAddress != address(0),
            "whitelistAddress not initialized"
        );
        require(kycStore.isKYCVerified(_to), "Recipient not allowed");

        super._beforeTokenTransfer(_from, _to, _amount);
    }


    function setWhitelistAddress(
        address newAddress
    ) external onlyOwner() {
        kycStoreAddress = newAddress;
        kycStore = RealToken(kycStoreAddress);
    }
}
