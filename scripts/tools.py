from config import *
from rich.console import Console
from brownie import network, interface, alert, chain, accounts, Contract, web3
from hexbytes import HexBytes
from brownie.convert.datatypes import HexString
from eth_account import Account
from eth_account.messages import encode_structured_data
import eth_utils
# from cfx_address import Base32Address
import json
import time
from hashlib import sha256
from rich import print
from rich import pretty
pretty.install()
# from pprint import pprint
console = Console(style="white on blue", stderr=True)


def get_gas_price():
    return min(web3.eth.gas_price+1e9, 3000*1e9)


def addr(account):
    if network.show_active()[:-2] == 'conflux' or network.show_active() == 'bsc-test':
        return {
            "from": account,
            "gas_price": get_gas_price(),
            "gas_limit": 15000000
        }
    if network.show_active() == 'cctv2024':
        return {
            "from": account,
            "gas_price": 1,
            "gas_limit": 15000000
        }
    return {
        "from": account,
        "gas_price": get_gas_price(),
        "gas_limit": 8000000
    }


def addr2(account, eth):
    return {'from': account, 'value': eth}


def addr4(account):
    return {
        "from": account,
        "gas_limit": 8000000,
        "allow_revert": True
    }


def addr5(account):
    return {
        "from": account,
        "gas_price": 1,
        "gas_limit": 8000000
    }


def b(amnt):
    return network.web3.fromWei(amnt, 'ether')


def addr_to_bytes(account) -> bytes:
    return bytes.fromhex(account.address[2:])


def int_to_bytes(x: int) -> bytes:
    return x.to_bytes((x.bit_length() + 7) // 8, 'big')


def int_from_bytes(xbytes: bytes) -> int:
    return int.from_bytes(xbytes, 'big')


def str_to_bytes(string: str) -> bytes:
    return string.encode('utf-8')


def str_to_hex(string: str) -> str:
    return "0x"+string.encode('utf-8').hex()


def hex_to_str(x: bytes) -> str:
    return bytes.fromhex(x).decode('utf-8')


def bytes_to_str(x: str) -> str:
    return hex_to_str(x[2:])  # remove 0x


def show3():
    return "admin=" + str(b(accounts[0].balance())) + " creator=" + str(b(accounts[1].balance())) + " consumer=" + str(b(accounts[2].balance()))


def balance_alert(account, name):
    alert.new(account.balance, msg=name +
              " Balance change from {} to {}", repeat=True)


def loadContractFromString(name, address, abi):
    abi = json.loads(abi)
    return Contract.from_abi(name, address, abi)


def loadContractFromFile(name, address, fp):
    with open(fp, 'r') as f:
        abi = json.load(f)
    return Contract.from_abi(name, address, abi)


def hash(content):
    return sha256(content.encode('utf-8')).hexdigest()


def sign_ownerken_permit(
    token,
    owner: Account,  # NOTE: Must be a eth_key account, not Brownie
    spender: str,
    allowance: int = 2 ** 256 - 1,  # Allowance to set with `permit`
    deadline: int = 0,  # 0 means no time limit
    override_nonce: int = None,


):
    # ganache bug https://github.com/trufflesuite/ganache/issues/1643
    chain_id = network.chain.id
    if override_nonce:
        nonce = override_nonce
    else:
        nonce = token.nonces(owner.address)
    data = {
        "types": {
            "EIP712Domain": [
                {"name": "name", "type": "string"},
                {"name": "version", "type": "string"},
                {"name": "chainId", "type": "uint256"},
                {"name": "verifyingContract", "type": "address"},
            ],
            "Permit": [
                {"name": "owner", "type": "address"},
                {"name": "spender", "type": "address"},
                {"name": "value", "type": "uint256"},
                {"name": "nonce", "type": "uint256"},
                {"name": "deadline", "type": "uint256"},
            ],
        },
        "domain": {
            "name": token.name(),
            "version": "1",
            "chainId": chain_id,
            "verifyingContract": str(token),
        },
        "primaryType": "Permit",
        "message": {
            "owner": owner.address,
            "spender": spender,
            "value": allowance,
            "nonce": nonce,
            "deadline": deadline,
        },
    }
    permit = encode_structured_data(data)
    return owner.sign_message(permit)


def tokenApprove(token, owner, spender, amount):
    if (token.allowance(owner, spender) < amount):
        tx = token.approve(spender, amount, addr(owner))
        # tx.wait(1)
        return tx
    return None


def addressApprove(token_address, owner, spender, amount):
    token = interface.IERC20(token_address)
    return tokenApprove(token, owner, spender, amount)


def getWeth(weth_address, _from, amount=0.01 * 10 ** 18):
    """Mints WETH by depositing ETH."""
    weth = interface.IWETH(weth_address)
    tx = weth.deposit(addr2(_from, amount))
    # tx.wait(1)
    return tx


def withdrawETH(weth_address, _from, amount=0.01 * 10 ** 18):
    weth = interface.IWETH(weth_address)
    tx = weth.withdraw(amount, addr(_from))
    # tx.wait(1)
    return tx


def loadLocalConfig(config_file):
    try:
        with open(config_file, 'r') as file:
            return json.load(file)
    except:
        return None


def encode_function_data(func=None, *args):
    """Encodes the function call so we can work with an initializer.

    Args:
        initializer ([brownie.network.contract.ContractTx], optional):
        The initializer function we want to call. Example: `box.store`.
        Defaults to None.

        args (Any, optional):
        The arguments to pass to the initializer function

    Returns:
        [bytes]: Return the encoded bytes.
    """
    if len(args) == 0 or not func:
        return eth_utils.to_bytes(hexstr="0x")
    else:
        return func.encode_input(*args)


def move_blocks(amount):
    for _ in range(amount):
        accounts[0].transfer(accounts[0], "0 ether")
    print(chain.height)


def Base32AddressToConfluxTest(addr):
    return Base32Address(addr, 1)


def Base32AddressToConflux(addr):
    return Base32Address(addr, 1029)


def Base32AddressToHex(addr):
    return Base32Address(addr).hex_address


def hhex(x):
    if len(hex(x)[2:]) == 1:
        return '0'+hex(x)[2:]
    return hex(x)[2:]


def b2s(data):
    return ''.join(list(map(lambda x: hhex(x), data)))
    # return str(HexBytes(data))


def s2b(data):
    return bytes(HexBytes(data))


def abi_encode(func, args):
    return "0x" + b2s(encode(func, args))


def abi_encodeHex(func, args):
    return HexString(abi_encode(func, args), 'bytes')
