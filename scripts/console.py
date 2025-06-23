import json
import sys
sys.path.append('scripts')
from functions import *
from eth_account.messages import encode_defunct
# from scripts.s3 import *

def initDID():
    did = load(DID2)
    deployer = load(Deployer)
    admin = load_account('admin')
    # registry = create2Deploy(deployer, ERC6551Registry, bytes(0), admin, '', 1)
    registry= load(ERC6551Registry)
    erc6551AccountProxy = load(ERC6551AccountProxy)
    did.init(registry, erc6551AccountProxy, addr(load_account('admin')))


def deployDID():
    empty = Empty.at(getAddress('Empty'))
    proxy_admin = Admin.at(getAddress('Admin'))
    coder = Tools.at(getAddress('Tools'))
    arg = coder.encode(empty, proxy_admin, bytes(0))
    deployer = Deployer.at(getAddress('Deployer'))
    admin = load_account('admin')

    create2Deploy(deployer, Proxy, arg, admin, '002', salts[4])
    proxy = Proxy.at(getAddress('DID2'))
    d2 = DID2.deploy(addr(admin))
    proxy_admin.upgrade(proxy, d2, addr(admin))
    did = Contract.from_abi('DID2', proxy, DID2.abi)
    # deployer.transferOwnership(did, admin, addr(admin))

    registry = load(ERC6551Registry)
    account6551 = load(ERC6551Account)
    arg = coder.encode(account6551)
    erc6551AccountProxy = load(ERC6551AccountProxy)
    did.init(registry, erc6551AccountProxy, addr(load_account('admin')))

def deployContracts():
    for c in [ ISOTOP1017,  eTicket]:
        register(c)

def testForwarder2(caller, contractAddr, nonce, data):
    JSON_DATA = '''
{
  "types": {
    "EIP712Domain": [
      {"name": "name", "type": "string"},
      {"name": "version", "type": "string"},
      {"name": "chainId", "type": "uint256"},
      {"name": "verifyingContract", "type": "address"}
    ],
    "ForwardRequest": [
      {"name": "from", "type": "address"},
      {"name": "to", "type": "address"},
      {"name": "value", "type": "uint256"},
      {"name": "gas", "type": "uint256"},
      {"name": "nonce", "type": "uint256"},
      {"name": "data", "type": "bytes"}
    ]
  },
  "primaryType": "ForwardRequest",
  "domain": {
    "name": "MinimalForwarder",
    "version": "0.0.1",
    "chainId": "",
    "verifyingContract": "<forwarder_contract_address>"
  },
  "message": {
    "from": "<user_address>",
    "to": "<recipient_contract_address>",
    "value": 0,
    "gas": 210000,
    "nonce": "",
    "data": ""
  }
}'''

    forwardRequest = (caller.address, contractAddr, 0, 210000, nonce, data)
    requestDict = json.loads(s=JSON_DATA)
    requestDict['domain']["chainId"] = chain.id
    requestDict["message"]["from"] = caller.address
    requestDict["message"]["to"] = contractAddr.address
    requestDict["message"]["nonce"] = nonce
    requestDict["message"]["data"] = data

    signed = Account.sign_message(
        encode_defunct(text=json.dumps(requestDict)), caller.private_key)

    return signed.signature


def main():
    def deployFixedAddress(salts):
        ret = []

        arg = coder.encode(empty, proxy_admin, bytes(0))
        create2Deploy(deployer, Proxy, arg, admin, '000', salts[0])
        create2Deploy(deployer, Proxy, arg, admin, '001', salts[1])
        create2Deploy(deployer, Proxy, arg, admin, '002', salts[2])
        create2Deploy(deployer, Proxy, arg, admin, '003', salts[3])

        proxy = Proxy.at(getAddress("Factory"))
        factory = Factory.deploy(addr(admin))
        proxy_admin.upgrade(proxy, factory, addr(admin))
        ret.append(Contract.from_abi('Factory', proxy, Factory.abi))


        proxy = Proxy.at(getAddress("DID2"))
        did = DID2.deploy(addr(admin))
        proxy_admin.upgrade(proxy, did, addr(admin))
        ret.append(Contract.from_abi('DID', proxy, DID2.abi))


        return ret



    active_network = network.show_active()
    print("Current Network:" + active_network)
    acl = Accounts(active_network)
    nathan = accounts.add(
        '0x9da140920525b01dff587494a21a909c5f635112d518e9b69f85d5c8c5076ed5')
    zhong = accounts.add(
        "0x6a34b5b8c08711f18669dc6f27ed16f4a5f3e06fb884d882e186822fbfa4656")
    nathan2 = '0x44028da500c013dd54e1e0beedc839317799b174'
    fei= accounts.add('0x7fafff78f0875d5e5f5aee2da303fba76c0c961023a4d57bf96d836dae4b92ef')

    try:
        admin, creator, consumer, iwan, newbie, newbie1, dep, alice, zhao, one = acl.getAccounts()

        if active_network in LOCAL_NETWORKS:
            deployer = Deployer.deploy(addr(one))
            deployer = Deployer.at(getAddress("Deployer"))
            create2Deploy(deployer, DateTime, bytes(0), admin, '', 1)
            coder = create2Deploy(deployer, Tools, bytes(0), admin, '', 1)
            empty = create2Deploy(deployer, Empty, bytes(0), admin, '', 1)
            proxy_admin = create2Deploy(
                deployer, Admin, bytes(0), admin, '', 1)
            deployer.transferOwnership(proxy_admin, admin, addr(admin))
            account6551 = create2Deploy(
                deployer, ERC6551Account, bytes(0), admin, '', 1)
            arg = coder.encode(account6551)
            erc6551AccountProxy = create2Deploy(
                deployer, ERC6551AccountProxy, arg, admin, '', 1)

            # getFixedAddress()
            [factory, did] = deployFixedAddress(salts)
            initDID()

        if active_network in TEST_NETWORKS:
            date= load(DateTime)
            factory= load(Factory)
            did = load(DID2)
            deployer = load(Deployer)   

        if active_network in REAL_NETWORKS:
            date= load(DateTime)
            factory= load(Factory)
            # did = load(DID2)
            deployer = load(Deployer)  

    except Exception:
        console.print_exception()
        # Test net contract address


if __name__ == "__main__":
    main()
