import sys
sys.path.append('scripts')

from tools import *
from web3 import Web3
from brownie import accounts, network, config, web3, convert
import os
import zlib
# from import webdriver
import beepy
import binascii
import oss2
from oss2.credentials import EnvironmentVariableCredentialsProvider
from datetime import datetime
import segno
import zlib

D18 = 10**18
ZERO = '0x0000000000000000000000000000000000000000'
active_network = network.show_active()


LOCAL_NETWORKS = ['development', 'mainnet-fork', 'polygon-fork']
TEST_NETWORKS = ['rinkeby', 'bsc-test',
                 'mumbai', 'wentest', 'qa', 'confluxET', 'arbitest', 'bsc-test', 'goerli', 'cctv']
REAL_NETWORKS = ['mainnet', 'polygon', 'wuhan',
                 'wenchang', 'confluxEM', 'ctblock', 'arbione', 'bsc-main', 'cctv2024']
DEPLOYED_ADDR = {  # Deployed address
    'rinkeby': "",
    'mumbai': ""
}

def comp(a,b):
    print(f"Comparing strings {len(a)} and {len(b)}")
    size= min(len(a),len(b))
    for i in range(size):
        if not a[i]==b[i]:
            print(f"{i}: {a[i]} - {b[i]}")

def load_account(name):
    return accounts.add(config['wallets'][name])


def print_greenb(text):
    print('\x1b[6;30;42m' + str(text) + '\x1b[0m')


def print_yellow(text):
    print('\x1b[1;33;40m' + str(text) + '\x1b[0m')


def print_green(text):
    print('\x1b[1;32;40m' + str(text) + '\x1b[0m')


def print_red(text):
    print('\x1b[1;31;40m' + str(text) + '\x1b[0m')


def print_yank(text):
    print('\x1b[0;36;40m' + str(text) + '\x1b[0m')

def print_time(timestamp):
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

class Accounts:
    names = ['admin', 'creator', 'consumer',
             'iwan', 'newbie', 'newbie1', 'deployer', 'alice', 'zhao', 'one']

    def __init__(self, active_network):
        self.active_network = active_network

        self.admin = accounts.add(config['wallets']['admin'])
        self.creator = accounts.add(config['wallets']['creator'])
        self.consumer = accounts.add(config['wallets']['consumer'])
        self.iwan = accounts.add(config['wallets']['iwan'])
        self.newbie = accounts.add(config['wallets']['newbie'])
        self.newbie1 = accounts.add(config['wallets']['newbie1'])
        self.deployer = accounts.add(config['wallets']['deployer'])
        self.alice = accounts.add(config['wallets']['alice'])
        self.zhao = accounts.add(config['wallets']['zhao'])
        self.one = accounts.add(config['wallets']['one'])

        self.all = [self.admin, self.creator,
                    self.consumer, self.iwan, self.newbie, self.newbie1,
                    self.deployer, self.alice, self.zhao, self.one]

        if active_network in LOCAL_NETWORKS:
            accounts[0].transfer(self.admin, "10 ether")
            accounts[1].transfer(self.creator, "10 ether")
            accounts[2].transfer(self.consumer, "10 ether")
            accounts[3].transfer(self.iwan, "10 ether")
            accounts[4].transfer(self.newbie, "10 ether")
            accounts[5].transfer(self.newbie1, "10 ether")
            accounts[6].transfer(self.deployer, "10 ether")
            accounts[7].transfer(self.alice, "10 ether")
            accounts[8].transfer(self.zhao, "10 ether")
            accounts[9].transfer(self.one, "10 ether")

        balance_alert(self.admin, "admin")
        balance_alert(self.creator, "creator")
        balance_alert(self.consumer, "consumer")
        balance_alert(self.iwan, "iwan")
        balance_alert(self.newbie, "newbie")
        balance_alert(self.newbie1, "newbie1")
        balance_alert(self.deployer, "deployer")
        balance_alert(self.alice, "alice")
        balance_alert(self.zhao, "zhao")
        balance_alert(self.one, "one")

    def getAccounts(self, _from=0, _to=10):
        return self.all[_from:_to]

    def find(self, name):
        for i in self.all:
            if name in str(i):
                return i
        return 'NA'


def flat_contract(name: str, meta_data: dict) -> None:
    if not os.path.exists(name + '_flat'):
        os.mkdir(name + '_flat')

    with open(name + '_flat/settings.json', 'w') as f:
        json.dump(meta_data['standard_json_input']['settings'], f)

    for file in meta_data['standard_json_input']['sources'].keys():
        print(f"Flatten file {name+ '_flat/'+ file} ")
        with open(name + '_flat/' + file, 'w') as f:
            content = meta_data['standard_json_input']['sources'][file]['content'].split(
                '\n')

            for line in content:
                if 'import "' in line:
                    f.write(line.replace('import "', 'import "./')+'\n')
                    continue
                if '    IERC1820Registry internal constant _ERC1820_REGISTRY = IERC1820Registry(0x1820a4B7618BdE71Dce8cdc73aAB6C95905faD24);' in line:
                    f.write(
                        '    IERC1820Registry internal constant _ERC1820_REGISTRY = IERC1820Registry(0x88887eD889e776bCBe2f0f9932EcFaBcDfCd1820);//Conflux')
                    continue

                f.write(line+'\n')
            f.write(f'\n// Generated by {__file__} \n')


# def chrome():
#     options = webdriver.ChromeOptions()
#     options.add_argument("disable-gpu")
#     options.add_argument("disable-infobars")

#     driver = webdriver.Chrome(options=options)
#     return driver


def deflate(data, compresslevel=9):
    compress = zlib.compressobj(
        compresslevel,        # level: 0-9
        zlib.DEFLATED,        # method: must be DEFLATED
        -zlib.MAX_WBITS,      # window size in bits:
        #   -15..-8: negate, suppress header
        #   8..15: normal
        #   16..30: subtract 16, gzip header
        zlib.DEF_MEM_LEVEL,   # mem level: 1..8/9
        0                     # strategy:
        #   0 = Z_DEFAULT_STRATEGY
        #   1 = Z_FILTERED
        #   2 = Z_HUFFMAN_ONLY
        #   3 = Z_RLE
        #   4 = Z_FIXED
    )
    deflated = compress.compress(data)
    deflated += compress.flush()
    return deflated


def makeInt(x, y, width=100, height=100):
    return y + x*(2 << 63) + (height+y)*(2 << 127) + (width+x)*(2 << 191)


def loadComponentData(dir, template, user):
    files = os.listdir(dir)
    for file in files:  # 遍历文件夹
        # 判断是否是文件夹，不是文件夹才打开
        if not os.path.isdir(file) and file[-4:] == '.svg':
            with open(dir + "/" + file) as f:
                buffer = f.read()
                # remove the first line
                buffer = buffer[buffer.index('\n')+1:]
                compress_data = deflate(str.encode(buffer))
                file = file[:file.index('-svgrepo-com.svg')]
                template.upload(file, compress_data, len(buffer), addr(user))
                # tx.wait(1)
                print(
                    f"{file} {len(buffer)} compressed to {int(len(compress_data)*100/len(buffer))}%")


def abiEncode(contract):
    all_functions = ''
    web3_f = web3.eth.contract(address=contract.address, abi=contract.abi)
    for func in web3_f.all_functions():
        name = str(func)[10:-1]
        all_functions += name + " : "+Web3.keccak(text=name)[:4].hex() + "\n"
    all_functions += 'Type function with arguments to generate data. exit to quit:\n\n'

    while True:
        choice = input(all_functions)
        if choice == 'q' or choice == '':
            break
        # print("web3_f.functions."+choice+".buildTransaction()")
        print(eval("web3_f.functions."+choice+".buildTransaction()")['data'])
    # transaction= web3_f.functions.mint(Base32Address.encode(str(consumer), 1), 1, addr(admin)).buildTransaction() # 获得函数调用的transaction
    # print(transaction['data'])


def loadIndex():
    with open('./.index', 'r') as f:
        return int(f.readline().strip())


def writeIndex(index):
    with open('./.index', 'w') as f:
        return int(f.write(str(index)))


def computeAddress(deployer, target, argument, salt):
    return deployer.getAddress(target.bytecode, argument, salt)


def create2Address(deployer, target, argument, _from, salt):
    deployer.Deploy(target.bytecode, argument, salt, addr(_from))


def create2Deploy(deployer_add, target, argument=bytes(0), _from=0, tail='00', salt=0):
    deployer = Deployer.at(deployer_add)
    mark_len = len(tail)

    if salt > 0:
        target_address = deployer.getAddress(target.bytecode, argument, salt)
        if mark_len > 0 and target_address[-mark_len:].lower() != tail:
            input(str(target) + " address wrong salt given, press Ctrl-C to quit ")
            return 0
        deployer.Deploy(target.bytecode, argument, salt, addr(_from))
        return target.at(target_address)

    if os.path.exists('.save'):
        with open('.save', 'r') as f:
            salt = int(f.read())
    while salt < 1145141919810:
        target_address = deployer.getAddress(target.bytecode, argument, salt)
        mark = target_address[-mark_len:].lower()

        if mark_len == 0 or mark == tail:
            print(f"\n\nsalt {salt}: {target_address}")
            with open('.result', 'w+') as f:
                f.write(f"salt {salt}: {target_address}")
            with open('.save', 'w') as f:
                f.write(str(0))
            break
        salt += 1
        if salt % 100 == 0:
            sys.stdout.write('.')
            sys.stdout.flush()
            with open('.save', 'w') as f:
                f.write(str(salt))
    print('\a')
    beepy.beep(sound="ping")
    os.remove(".save")
    return salt


def create3Deploy(deployer_add, target, argument=bytes(0), _from=0, head='100', salt=0):
    deployer = Deployer.at(deployer_add)
    mark_len = len(head)

    if salt > 0:
        target_address = deployer.getAddress(target.bytecode, argument, salt)
        if mark_len > 0 and target_address[2:2+mark_len].lower() != head:
            input(str(target) + " address wrong salt given, press Ctrl-C to quit ")
            return 0
        deployer.Deploy(target.bytecode, argument, salt, addr(_from))
        return target.at(target_address)

    if os.path.exists('.save'):
        with open('.save', 'r') as f:
            salt = int(f.read())
    while salt < 1145141919810:
        target_address = deployer.getAddress(target.bytecode, argument, salt)
        mark = target_address[2:2+mark_len].lower()

        if mark_len == 0 or mark == head:
            print(f"\n\nsalt {salt}: {target_address}")
            with open('.result', 'w+') as f:
                f.write(f"salt {salt}: {target_address}")
            with open('.save', 'w') as f:
                f.write(str(0))
            break
        salt += 1
        if salt % 100 == 0:
            sys.stdout.write('.')
            sys.stdout.flush()
            with open('.save', 'w') as f:
                f.write(str(salt))
    print('\a')
    beepy.beep(sound="ping")
    os.remove(".save")
    return salt


def getProxyFixedAddress(tail):
    admin = load_account('admin')
    deployer = load(Deployer)
    coder = load(Tools)
    empty = load(Empty)
    proxy_admin = load(Admin)
    arg = coder.encode['address,address,bytes'](empty, proxy_admin, bytes(0))
    create2Deploy(deployer, Proxy, arg, admin, tail, 0)


def proxyDeploy(target, tail, salt):
    deployer = load(Deployer)
    admin = load_account('admin')
    coder = load(Tools)
    empty = load(Empty)
    proxy_admin = load(Admin)
    arg = coder.encode(empty, proxy_admin, bytes(0))
    name = target.get_verification_info()['contract_name']

    proxy = create2Deploy(deployer, Proxy, arg, admin, tail, salt)
    temp = target.deploy(addr(admin))
    proxy_admin.upgrade(proxy, temp, addr(admin))
    return Contract.from_abi(name, proxy, target.abi)


def proxyUpdate(target):
    name = target.get_verification_info()['contract_name']
    proxy = load(target)
    admin = load_account('admin')
    proxy_admin = load(Admin)
    temp = target.deploy(addr(admin))
    proxy_admin.upgrade(proxy, temp, addr(admin))
    return Contract.from_abi(name, proxy, target.abi)


def funcEncode(contract, func):
    web3_f = web3.eth.contract(address=contract.address, abi=contract.abi)
    return eval('web3_f.functions.'+func+'.build_transaction()')['data']


def set_nonce(_account, _nonce):
    while _account.nonce < _nonce:
        _account.transfer(_account, 0)


def ddsput(key, value):
    if not 'dds' in locals():
        dds = Contract.from_abi(
            'DDS', '0x1E68f6Aee73e3A8e4Cb09B035b9736Ad193c1001', DDS.abi)

    if type(value) == type(dds):
        value = bytes.fromhex(value.address[2:])

    dds.put('ISOTOP', key, value, addr(
        accounts.add(config['wallets']['admin'])))


def ddskeys():
    if not 'dds' in locals():
        dds = Contract.from_abi(
            'DDS', '0x1E68f6Aee73e3A8e4Cb09B035b9736Ad193c1001', DDS.abi)

    return dds.getKeys('ISOTOP')


def ddsget(key):
    if not 'dds' in locals():
        dds = Contract.from_abi(
            'DDS', '0x1E68f6Aee73e3A8e4Cb09B035b9736Ad193c1001', DDS.abi)

    return dds.get('ISOTOP', key)


def ddsremove(key):
    ddsput(key, bytes(0))


def dump_bytecode(contract):
    pass


def jsonformat(data):
    return json.dumps(data, sort_keys=False, indent=4, separators=(',', ':'), ensure_ascii=False)


def tryto(func):
    try:
        func
    except Exception:
        pass


def load(Obj):
    name = Obj.get_verification_info()['contract_name']
    contract_address = getAddress(name)
    return Contract.from_abi(name, contract_address, Obj.abi)

def loadAsset(addr):
    factory=load(Factory)
    ret= factory.getContractInfo(addr)
    print(f"[{ret[0]}] type {ret[1]} deployed at {str(datetime.fromtimestamp(ret[3]))} by {short(ret[2])}")
    return loadV(ret[1], addr)

def loadV(name, contract_address):
    if not os.path.exists(f'abi/{name}.json'):
        print(f"abi/{name}.json not found, here are some files we have")
        # list all the files in the abi directory
        files = os.listdir('abi')
        # find the file with the same name as the contract
        for file in files:
            if name.split('-')[0] in file and file.endswith('.json') and not file.endswith('.doc.json'):
                print(file)
        return None
    # contract_address = getAddress(name.split('-')[0])
    with open(f'abi/{name}.json', 'r') as f:
        abi = json.load(f)
        return Contract.from_abi(name, contract_address, abi)

def find_attributes(data, key):
    ret={}
    for attr in data:
        if len(key)>0 and key[0]=='*':
            if key[1:] in attr["trait_type"] or key[1:] in attr["value"]:
                ret[attr["trait_type"]]=attr["value"]
        else:
            if attr["trait_type"]== key:
                ret[key]=attr["value"]
    return ret
        
def find_key(data, key):
    ret={}
    for k in data.keys():
        if len(key)>0 and key[0]=='*':
            if key[1:] in k or key[1:] in data[k]:
                ret[k]= data[k]
        else:
            if k == key:
                ret[k]= data[k]
        if k=='attributes':
            # merge two dict
            ret_attr= find_attributes(data[k], key)
            for i in ret_attr.keys():
                ret[i]= ret_attr[i]
    # print(ret)
    return ret

def show_token(addr, id, key=None):
    if not type(addr)==network.contract.ProjectContract:
        asset= loadAsset(addr)
    else:
        asset= addr
    if not asset.exists(id):
        print(f"Asset {id} does not exist")
        return None
    metadata= base64_json(asset.tokenURI(id))
    if not key:
        return metadata
    return find_key(metadata, key)

def show_tokens(addr, key=None):
    if not type(addr)==network.contract.ProjectContract:
        asset= loadAsset(addr)
    else:
        asset= addr

    ret={}
    for token in asset.tokens(0,10000)[1]:
        metadata= base64_json(asset.tokenURI(token))
        if not key:
            ret[token]=metadata
        else:
            ret_key= find_key(metadata, key)
            if len(ret_key.keys())!=0:
                ret[token]=ret_key
            # print(f'looking for {token} : {ret[token]}')
    if key == None:
        return list(ret.keys())
    return ret

def show_user_tokens(user, addr, key=None):
    if not type(addr)==network.contract.ProjectContract:
        asset= loadAsset(addr)
    else:
        asset= addr

    ret={}
    for token in asset.tokensOf(user, 0,10000)[1]:
        metadata= base64_json(asset.tokenURI(token))
        if not key:
            ret[token]=metadata
        else:
            ret_key= find_key(metadata, key)
            if len(ret_key.keys())!=0:
                ret[token]=ret_key
            # print(f'looking for {token} : {ret_key}')
    if key == None:
        return list(ret)
    return ret

def upgrade(Obj):
    admin = load_account('admin')
    adm = load(Admin)
    temp = Obj.deploy(addr(admin))
    proxy = load(Obj)
    adm.upgrade(proxy, temp, addr(admin))


def reset(Obj):
    admin = load_account('admin')
    adm = load(Admin)
    reset = load(Reset)
    proxy = load(Obj)
    adm.upgrade(proxy, reset, addr(admin))
    r = Contract.from_abi('Reset', proxy, Reset.abi)
    r.reset(addr(admin))

def loadContract(name):
    contract_address = getAddress(name)
    f=open(f"build/contracts/{name}.json", "r")
    data=json.load(f)
    f.close()
    return Contract.from_abi(name, contract_address, data['abi'])

def registerAll():
    admin = load_account('admin')
    DateTime.at(load(DateTime))
    factory = load(Factory)
    for contract in project.Nft2Project:
        name = contract.get_verification_info()['contract_name']
        if name in factory.getContractRegisted():
            register(contract)

def register(*args):
    for Obj in args:
        admin = load_account('admin')
        temp = Obj.deploy(addr(admin))
        load(DateTime)
        factory = load(Factory)
        name = temp.contractInfo().split('-')[0]
        factory.register(name, temp, addr(admin))
        # index_dir= 'shucang/abi/'
        # auth = oss2.ProviderAuth(EnvironmentVariableCredentialsProvider())
        # bucket = oss2.Bucket(auth, 'https://oss-cn-beijing.aliyuncs.com', 'yangbo2023')
        # print(f"uploading abi to oss: {index_dir}{temp.contractInfo()}.json and {index_dir}{temp.contractInfo()}.txt")
        # bucket.put_object_from_file(index_dir+temp.contractInfo()+'.json', 'abi/'+name+'.json')
        # bucket.put_object_from_file(index_dir+temp.contractInfo()+'.txt', 'abi/'+name+'.txt')

def abi(Obj):
    name = Obj.get_verification_info()['contract_name']
    admin = load_account('admin')
    temp = load(Obj)
    index_dir= 'shucang/abi/'
    auth = oss2.ProviderAuth(EnvironmentVariableCredentialsProvider())
    bucket = oss2.Bucket(auth, 'https://oss-cn-beijing.aliyuncs.com', 'yangbo2023')
    print(f"uploading abi to oss: {index_dir}{temp.contractInfo()}.json+.txt")
    bucket.put_object_from_file(index_dir+temp.contractInfo()+'.json', 'abi/'+name+'.json')
    bucket.put_object_from_file(index_dir+temp.contractInfo()+'.txt', 'abi/'+name+'.txt')


def register_with_dds(Obj):
    name = Obj.get_verification_info()['contract_name']
    admin = load_account('admin')
    dds = load(DDS)
    temp = Obj.deploy(dds, addr(admin))
    factory = load(Factory)
    factory.register(name, temp, addr(admin))


def clone(Obj, owner):
    name = Obj.get_verification_info()['contract_name']
    factory = load(Factory)
    factory.deployContract(name, addr(owner))
    ret = factory.getLastDeployed(name, owner)
    return Obj.at(ret)

def base64_json(data):
    jsondata= binascii.a2b_base64(str_to_bytes(data[28:])).decode('utf-8')
    return json.loads(jsondata,strict=False)
    # return jsondata

def short(message: str):
    if len(message) > 10:
        return message[:4]+'...'+ message[-4:]
    else:
        return message
    
def list_all_contracts(owner: str):
    factory = load(Factory)
    ret= factory.getContractDeployedList(owner)
    print("{:<5} {:<25} {:<15} {:<15} {:<15}".format("ID", "Contract", "Address", "Owner", "Time"))
    for i in ret:
        print("{:<5} {:<25} {:<15} {:<15} {:<15}".format(i[0],i[1],short(i[2]),short(i[3]),str(datetime.fromtimestamp(i[4]))))

def qrcode(data:bytes):
    segno.make_qr(zlib.compress(data)).show()