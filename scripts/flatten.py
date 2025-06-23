
from scripts.functions import *


def main():
    active_network = network.show_active()
    print("Current Network:" + active_network)
    acl = Accounts(active_network)
    admin, creator, consumer, iwan, newbie, newbie1, dep, alice, zhao, one = acl.getAccounts()

    try:
        ISOTOP1010.deploy(addr(admin))
        flat_contract('ISOTOP1010', ISOTOP1010.get_verification_info())

        ISOTOP1011.deploy(addr(admin))
        flat_contract('ISOTOP1010', ISOTOP1011.get_verification_info())

        ISOTOP1012.deploy(addr(admin))
        flat_contract('ISOTOP1010', ISOTOP1012.get_verification_info())

        ISOTOP1013.deploy(addr(admin))
        flat_contract('ISOTOP1010', ISOTOP1013.get_verification_info())

        ISOTOP1014.deploy(addr(admin))
        flat_contract('ISOTOP1010', ISOTOP1014.get_verification_info())

        ISOTOP1015.deploy(addr(admin))
        flat_contract('ISOTOP1010', ISOTOP1015.get_verification_info())

    except Exception:
        console.print_exception()
        # Test net contract address


if __name__ == "__main__":
    main()
