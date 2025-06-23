from brownie import chain, project, accounts, Factory, DDS, Proxy, \
    Deployer, Admin, Empty, \
    DateTime, \
    eTicket, manghe, eCupon, eCard, ePointCard, ISOTOP1017, DIDAsset721, \
    testABI, ISOTOP1053, XinYuan

ZERO = "0x0000000000000000000000000000000000000000"

# Conflux internal
Admin_address = "0x0888000000000000000000000000000000000000"
Sponsor_address = "0x0888000000000000000000000000000000000001"
Staking_address = "0x0888000000000000000000000000000000000002"

dan = '0x805a53F94Dfb3a381560b9c577f7d7F4b5f924A2'
dan1 = '0xb8b3440D39d827A685377629962867dA1E9E172c'
jie = '0xc419bC9718C090C4f666dc4c9d6587a9b4B0ab2D'
tracy1 = '0xbb44a15462C5c5042A74b4Adc770793A7E57210a'
tracy = '0x2BC344895094575cb363DdBCa7FDC8DE66Ad2dD7'
bai = '0xBEE21B3DbEe246Fc67C955beEb6a76549a12E951'
rick = '0x9da32F03cc23F9156DaA7442cADbE8366ddAc123'
rick1 = '0x01389c1B27bbb0ff8D3493110b83572A465dadAB'
rick2 = '0xdB9C66785f3c464179a0982EEdF1E96C18b25300'
alex = '0x075De1FEe1E437504Dd3F47CE2C36eF52b0f1CD8'
fei='0x8eb045f280CAdb651dF9BBBeA86fF46a28161e18'


new_youth_ipfs = 'ipfs://bafybeihpcbsjqybsxydwsdim2u5p6ravk72ws36yidskjgo3gbfnozleeu/'
tianzi_ipfs = 'isotop.4everland.link/ipfs/bafkreicomhc6uztlak27ytugmvyz5uusucn5ztbg4uxd5lm4leool7gjmm'
teacher_ipfs = 'isotop.4everland.link/ipfs/bafkreieg2x3pqrl536b2xqdwnpyrwayy5wmz4dcojadwro7g2k5nqjfneq'
tickets_ipfs = 'ipfs://bafybeigywrcaqskpp37a6owfgvfkfk72a6woyabdociy7vfrllebk7zgrm/'
tickets_gif = 'ipfs://bafybeiawzx7w7c2pfainwwzgsfpjzqme5lvm3uqu4hpoxar47fxjbddcsm/'

iwan_gif = 'isotop.4everland.link/ipfs/bafybeihfcaykwt7ho5vbxo37gyoiqiew26s7riscastz3h7rmtraod7dc4'
ovip = 'https://bafybeigtb3tt4a2eyurd4vk7jrjuiwnetufyfy7evmf4e2nwljatrcsdhq.ipfs.nftstorage.link/'

wenbo_meta = 'isotop.4everland.link/ipfs/bafybeidzpludvu6oqjwo4zpywfouowdyhcgvxgkfqecokqmup33rvqu45a/'
feng_meta = 'isotop.4everland.link/ipfs/bafybeihsmit2fuxymznneolhis7g5ac3q5mdd3t3yyauesl5pwtzvtsyd4/'
wenbo_meta = 'isotop.4everland.link/ipfs/bafybeid2xwn7vqkqnq2kfc55bfn6zy4hpdf7bjrribrpuc2q63sj54iop4/'
guangxi_meta = 'isotop.4everland.link/ipfs/bafybeigidoylwqozdgm2at4vfklirj2et4qyfgv6b5cxc2bde4rhphbef4/'

IWAN = 13911024683
CAO = 13121189506

default_nft_cover = 'ipfs://bafkreigjisx3govdki64bfuwgegllg3qagi7aqp6w3jkrf3bjfkcol6j2a'
blockchain_ticket = 'https://wallet-1300777907.cos.ap-hongkong.myqcloud.com/ticket/20230412/'
chengdu_ticket = 'https://wallet-1300777907.cos.ap-hongkong.myqcloud.com/ticket/20230411/'

ensRegistryProxyAddress = "0xDdd1c542C4FDc127740B93Fb837CCcC3b2295998"
reverseRegistrarProxyAddress = "0xE348c84a6b89B746F6C85974DB53835F4BD70514"
metaServiceProxyAddress = "0x5b5231f1D3c9b65d3A862863E0D151387dBb30bB"
bytesUtilsAddress = "0x3C1e62661FAf2e9f7C28cA95d2B4e5A4fFbC0FCA"

# GENERAL_ADDRESS = {
#     "Factory": "0xCE0Fcafb4da817636F118c77a7CFcee3d1adF000",
#     "DDS": "0x1E68f6Aee73e3A8e4Cb09B035b9736Ad193c1001",
#     "DID": "0x02E9c23e26FCc2489F9f64EAdfd6E2288B06D002",
#     "Forwarder": "0x76Fd98C9EDc5dA98D8B0dF5fE303Ca0d765D9003",
#     "Deployer": "0xb1eFE38b2A51035652631ec27cD634A144B605CC",
#     "Admin": "0x5A8e3f8d68678D18C5d0451315e8F0e878434263",
#     "Empty": "0x767D064a075Dc76b781Bd84349ff56519de8aed8"
# }

salts = [889, 1815, 1035, 7911, 3163, 3831, 2324]


GENERAL_ADDRESS = {
    # "Factory": "0x768e7C8A24e5a7c2fe78f42F3bF2323edA196000",  # salt[0]
    # "Factory": "0x5067CE4dC9a2fb2c3E1898fc24B067cd8d92A000", 6866
    # "Factory": "0xd15D09B8ab9f60bd062b768EB974C43fdE04f000", #889
    "Factory": "0xf70f5CaB1390276A1be309A818c03475c1B26C11", # 临时测试用工厂，不要用于生产环境
    "DDS": "0x9E4eE1Cb21DfAA91d513B2BE088338C834DEf001",  # salt[1]
    "DID": "0x7D5D9e9033dF0939c0fc2CD5CE42667Bc2B31002",  # salt[2]
    "DID2": "0x067eA3ebD341ac7E4F363865805d75409e748004",  # 3163
    "Forwarder": "0x0a5d59B18feEd1ef5feB16b302c92AfAc9cbA003",  # salt[3]
    "CheckCoder": "0x4D318BA5C70d70Bc2821Cdcf75C55552Cd153005",  # 3831
    "exchangeCode": "0x1feD0A7e078E89088a9F91c615a9a121013fa006",  # salt[6] 2324
    "ERC6551Registry": "0xF6bcf03C6487D1F34e1327263405044BA227C8f4",
    "ERC6551Account": "0x1Fb2690a088B6eE0d4B1646689d46D8afE9a4c8A",
    "ERC6551AccountProxy": "0xFe4f8682D3300D1E5e580a91eaF1BCc7F6B385Ff",
    "DateTime": "0xA352587d1D43d4F7193839d9f5F04773b9D248aE",
    "List": "0xDBe0b154776c5CEbCdAA399CaF2B89F8649a5e05",
    "BytesUtils": "0xdc5721B288a03f3405f2893E79f87B927C199bDe",
    "Tools": "0x83fB290Bba50BaC4DB1Db93861102c923181AFda",
    'Reset': "0xeeE4AfbfEE0809a356aBd2a03dA734CAA121047b", # salt 1

    "Deployer": "0xb1eFE38b2A51035652631ec27cD634A144B605CC",  # salt 1
    "Admin": "0x82846E3ffEc9f329FCFdE053E29428f3B0CFe20a",  # salt 1
    "Empty": "0x9A62607A54c38b7F672e5Dd41a0B1f7D0a983A21"  # salt 1
}

CONFLUX_ADDRESS = {
    "Deployer": "0x87C45B3d8eDDCF8e59db14fF124Db348D838691C"
}


def getAddress(contractInfo):
    if chain.id == 1 or chain.id == 1029:
        if contractInfo in CONFLUX_ADDRESS:
            return CONFLUX_ADDRESS[contractInfo]
        return ""
    if contractInfo in GENERAL_ADDRESS:
        return GENERAL_ADDRESS[contractInfo]
    return ""

def getProjectContracts():
    return list(filter(lambda x: not x.startswith('OpenZeppelin'), dict(project.Nft2Project).keys()))