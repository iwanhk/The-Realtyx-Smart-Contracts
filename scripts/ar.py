import arseeding
import everpay
import os


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
# ar account
# signer = everpay.ARSigner('your ar wallet file')


# eth account
signer = everpay.ETHSigner(os.getenv('CONSUMER_PRIVATE_KEY'))

data = str_to_bytes('13911024683')

# send data to default arseeding service: https://arseed.web3infra.dev
# you could set your own arseeding:
# order = arseeding.send_and_pay(signer, 'usdc', data, arseed_url="your arseeding service url")
# pay usdc in your everpay account
order = arseeding.send_and_pay(signer, 'cfx', data)

# order['itemId'] is your file item id.
# you could view your file in https://arseed.web3infra.dev/o['itemId'] or http://arweave.net/o['itemId']
print(order)
