import json
import sys
sys.path.append('scripts')
from functions import *
from eth_account.messages import encode_defunct
# from sdk import abi_encode

SLICE = 15000

def deployContracts():
    for c in [ISOTOP1017,  eTicket]:
        register(c)

def contractInfo(Con: network.contract.ContractContainer):
    return Con.get_verification_info()['contract_name']


def main():
    active_network = network.show_active()
    print("Current Network:" + active_network)
    acl = Accounts(active_network)
    admin, creator, consumer, iwan, newbie, newbie1, dep, alice, zhao, one = acl.getAccounts()

    def initDID():
        did = load(DID2)
        registry = load(ERC6551Registry)
        erc6551AccountProxy = load(ERC6551AccountProxy)
        did.init(registry, erc6551AccountProxy, addr(load_account('admin')))
        # did.create('iwantest', '', iwan, 365*24*60*60, addr(admin))

    def deployDID():
        empty = load(Empty)
        proxy_admin = load('Admin')
        coder = load('Tools')
        arg = coder.encode(empty, proxy_admin, bytes(0))
        deployer = Deployer.at(getAddress('Deployer'))
        did = create2Deploy(deployer, Proxy, arg,
                            load_account('admin'), '002', salts[2])
        initDID()

    def getFixedAddress():
        coder = load(Tools)
        empty = load(Empty)
        proxy_admin = load(Admin)
        arg = coder.encode(empty, proxy_admin, bytes(0))
        for i in range(11):
            create2Deploy(deployer, Proxy, arg, admin, str(i).zfill(3), 0)

    def deployFixedAddress(salts):
        ret = []

        coder = load(Tools)
        empty = load(Empty)
        proxy_admin = load(Admin)
        arg = coder.encode(empty, proxy_admin, bytes(0))
        deployer= load(Deployer)

        create2Deploy(deployer, Proxy, arg, admin, '000', salts[0])
        create2Deploy(deployer, Proxy, arg, admin, '004', salts[4])

        proxy = Proxy.at(getAddress("Factory"))
        factory = Factory.deploy(addr(admin))
        proxy_admin.upgrade(proxy, factory, addr(admin))
        ret.append(Contract.from_abi('Factory', proxy, Factory.abi))

        proxy = Proxy.at(getAddress("DID2"))
        f = DID2.deploy(addr(admin))
        proxy_admin.upgrade(proxy, f, addr(admin))
        ret.append(Contract.from_abi('DID2', proxy, DID2.abi))

        return ret

    try:
        if active_network in LOCAL_NETWORKS:
            deployer = Deployer.deploy(addr(one))
            deployer = Deployer.at(getAddress("Deployer"))
            create2Deploy(deployer, DateTime, bytes(0), admin, '', 1)
            coder = create2Deploy(deployer, Tools, bytes(0), admin, '', 1)
            empty = create2Deploy(deployer, Empty, bytes(0), admin, '', 1)
            resetObj= create2Deploy(deployer, Reset, bytes(0), admin, '', 1)

            proxy_admin = create2Deploy(
                deployer, Admin, bytes(0), admin, '', 1)
            deployer.transferOwnership(proxy_admin, admin, addr(admin))
            registry = create2Deploy(deployer, ERC6551Registry,
                                     bytes(0), admin, '', 1)
            account6551 = create2Deploy(
                deployer, ERC6551Account, bytes(0), admin, '', 1)
            arg = coder.encode(account6551)
            # arg = abi_encodeHex(['address'], [account6551.address])
            erc6551AccountProxy = create2Deploy(
                deployer, ERC6551AccountProxy, arg, admin, '', 1)

            [factory, did2] = deployFixedAddress(salts)
            initDID()
            deployContracts()

        if active_network in TEST_NETWORKS:
            deployer = load(Deployer)
            create2Deploy(deployer, DateTime, bytes(0), admin, '', 1)
            coder = create2Deploy(deployer, Tools, bytes(0), admin, '', 1)
            empty = create2Deploy(deployer, Empty, bytes(0), admin, '', 1)
            resetObj= create2Deploy(deployer, Reset, bytes(0), admin, '', 1)
            proxy_admin = create2Deploy(
                deployer, Admin, bytes(0), admin, '', 1)
            deployer.transferOwnership(proxy_admin, admin, addr(admin))
            registry = create2Deploy(deployer, ERC6551Registry,
                                     bytes(0), admin, '', 1)
            account6551 = create2Deploy(
                deployer, ERC6551Account, bytes(0), admin, '', 1)
            arg = coder.encode(account6551)
            erc6551AccountProxy = create2Deploy(
                deployer, ERC6551AccountProxy, arg, admin, '', 1)

            [factory, did2] = deployFixedAddress(salts)
            initDID()
            deployContracts()

        if active_network in REAL_NETWORKS:
            deployer = load(Deployer)
            # coder = create2Deploy(deployer, Tools, bytes(0), admin, '', 1)
            # create2Deploy(deployer, DateTime, bytes(0), admin, '', 1)
            # empty = create2Deploy(deployer, Empty, bytes(0), admin, '', 1)
            # registry = create2Deploy(deployer, ERC6551Registry,
            #                          bytes(0), admin, '', 1)
            # reset= create2Deploy(deployer, Reset, bytes(0), admin, '', 1)
            # proxy_admin = create2Deploy(
            #     deployer, Admin, bytes(0), admin, '', 1)
            # deployer.transferOwnership(proxy_admin, admin, addr(admin))

            # account6551 = create2Deploy(
            #     deployer, ERC6551Account, bytes(0), admin, '', 1)
            # arg = coder.encode(account6551)
            # # arg = abi_encodeHex(['address'], [account6551.address])
            # erc6551AccountProxy = create2Deploy(
            #     deployer, ERC6551AccountProxy, arg, admin, '', 1)

            # [factory, did2] = deployFixedAddress(salts)
            # initDID()
            # deployContracts()

    except Exception:
        console.print_exception()
        # Test net contract address

if __name__ == "__main__":
    main()
