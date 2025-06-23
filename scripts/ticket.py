import json, sys
import time
sys.path.append('scripts')
from eth_account.messages import encode_defunct
from functions import *
import oss2
from oss2.credentials import EnvironmentVariableCredentialsProvider

def comp(ret1, ret2):
    for i in range(len(ret1)):
        if ret1[i]!= ret2[i]:
            print(f"{i} {ret1[i]} {ret2[i]}")

def error_msg(logfile):
    address= set()
    contract= set()

    e2=eTicket[-1]
    # read csv file and get error message    
    with open(logfile, 'r') as f:
        lines= f.readlines()

    with open(logfile[:-3]+'.txt', 'w') as f:
        for line in lines:
            msg= line.split(',')[6].split('"')
            if len(msg)> 6:
                content= eval(str(e2.decode_input(msg[6])))
                contract.add(line.split(',')[5].split('"')[7])
                address.add(content[1][0])
                
                f.write(str(e2.decode_input(msg[6]))+'\n')

    print(f"Tatal {len(contract)} contracts to {len(address)}")


def initETicket(file):
    auth = oss2.ProviderAuth(EnvironmentVariableCredentialsProvider())
    bucket = oss2.Bucket(auth, 'https://oss-cn-beijing.aliyuncs.com', 'yangbo2023')
    admin=load_account('admin')
    with open(file) as f:
        config= json.load(f)

    ret={}

    for contract in config.keys():
        print(f"init {contract}")
        out_file= contract+'.json'

        if os.path.exists(out_file):
            continue
        iwan= load_account('iwan')
        ticket= eTicket.at(contract)
        # if config[contract]['startTime']>=config[contract]['validTime']:
        #     print(f"startTime is late than validTime, skip {contract}")
        #     continue
        # if config[contract]['validTime']<=int(time.time()):
        #     print(f"validTime is less than current time, skip {contract}")
        #     continue
        type_args=[]
        for tt in config[contract]['type']:
            if tt == True:
                tt= 'S'
            if tt == False:
                tt= 'R'
            if tt not in ['S', 'R', 'N']:
                print(f"type is not S or R or N, skip {tt}")
                continue
            type_args.append(str_to_hex(tt))

        print(f"init ticket: {ticket}")
        ticket.init(config[contract]['info'], config[contract]['right'], type_args, config[contract]['startTime']+8*60*60,config[contract]['validTime'], addr(admin))
        if chain.id== 1226:
            print(f"add operator to ticket: {ticket}")
            ticket.addOperator('0x99345DbE15E083cF93e98Ab447Cc870B968d1bCC', addr(admin))
            ticket.addBank(10000, addr(admin))
            ticket.setQuota('0x99345DbE15E083cF93e98Ab447Cc870B968d1bCC',100, addr(admin))
            
        if chain.id== 22356:
            ticket.addOperator('0xc0f67Ec08c9E7eA13aaB3D6070253E321b940058', addr(admin))
            ticket.addBank(10000, addr(admin))
            ticket.setQuota('0xc0f67Ec08c9E7eA13aaB3D6070253E321b940058',100, addr(admin))
        if chain.id== 12231:
            ticket.addOperator('0x44028DA500C013DD54e1E0bEeDC839317799B174', addr(admin))
            ticket.addBank(10000, addr(admin))
            ticket.setQuota('0x44028DA500C013DD54e1E0bEeDC839317799B174',100, addr(admin))


        if not ticket.exists(0):
            ticket.mint(iwan, 0, addr(admin))

        # meta= json.dumps(base64_json(ticket.tokenURI(0)), ensure_ascii= False)
        meta=base64_json(ticket.tokenURI(0))
    
        ret[contract]=meta

        
        with open(out_file, 'w') as f:
            json.dump(meta, f, ensure_ascii = False)
        bucket.put_object_from_file('shucang/project/'+out_file, out_file)

    return ret

def setOperator(file):
    admin=load_account('admin')
    with open(file) as f:
        config= json.load(f)

    ret={}
    for contract in config.keys():
        print(f"init {contract}")
        out_file= contract+'.json'

        if os.path.exists(out_file):
            continue
        iwan= load_account('iwan')
        ticket= eTicket.at(contract)

        if chain.id== 1226:
            ticket.addOperator('0x99345DbE15E083cF93e98Ab447Cc870B968d1bCC', addr(admin))
        if chain.id== 22356:
            ticket.addOperator('0xc0f67Ec08c9E7eA13aaB3D6070253E321b940058', addr(admin))
        if chain.id== 12231:
            ticket.addOperator('0x44028DA500C013DD54e1E0bEeDC839317799B174', addr(admin))

def getTicketURI(file):
    auth = oss2.ProviderAuth(EnvironmentVariableCredentialsProvider())
    bucket = oss2.Bucket(auth, 'https://oss-cn-beijing.aliyuncs.com', 'yangbo2023')

    with open(file) as f:
        config= json.load(f)

    ret={}

    for contract in config.keys():
        ticket= eTicket.at(contract)
        # meta= json.dumps(base64_json(ticket.tokenURI(0)), ensure_ascii= False)
        meta=base64_json(ticket.tokenURI(0))
        meta["attributes"][0]["trait_type"]= "出品方DID"
        
        out_file= contract+'.json'

        ret[contract]=meta
        # print(meta)
        with open(out_file, 'w') as f:
            json.dump(meta, f, ensure_ascii= False) 
        bucket.put_object_from_file('shucang/project/'+out_file, out_file)

    return ret

def main():
    active_network = network.show_active()
    print("Current Network:" + active_network)
    acl = Accounts(active_network)
    nathan = accounts.add(
        '0x9da140920525b01dff587494a21a909c5f635112d518e9b69f85d5c8c5076ed5')
    zhong = accounts.add(
        "0x6a34b5b8c08711f18669dc6f27ed16f4a5f3e06fb884d882e186822fbfa4656")
    nathan2 = '0x44028da500c013dd54e1e0beedc839317799b174'
    nathan3='0xa2fdAaD6Ca69A3784753fB6671b505BA762C59eD'
    cctv1= accounts.add('0xdc2ceb5de41d996ca92226c75b8b6b1b70716148a20dd3847fb94db31edbf276')
    cctv2= accounts.add('0xf482e4cc4410da038f6ab23318ff77c27f6f28741a51493acb50ab529237d535')
    cctv3= accounts.add('0xda009a51eea1d531c83ad7880a63e182414011b79f2043a65c87142236bd0199')
    hbx= accounts.add('0x85c3b995f8dc424adc71fcf7f33642d095da29476de2331eabdb6c6ff87937e2')


    try:
        admin, creator, consumer, iwan, newbie, newbie1, dep, alice, zhao, one = acl.getAccounts()
        fei= accounts.add('0x67410d8ee1a979d5086eba6d7ae4d832fae645ca3a44242387d5293da496a17b')

        if active_network in LOCAL_NETWORKS:
            date=DateTime.deploy(addr(admin))
            ticket = eTicket.deploy(addr(admin))
            ticket.addBank(100, addr(admin))
            ticket.addOperator(iwan, addr(admin))

            ticket.init([
                "漫葡·看见贺兰沉浸式演艺小镇",
                "【需预约】看见贺兰是一座中国宁夏贺兰山下的沉浸式演艺小镇。给游客一场看见自我的狂野之旅。游宁夏，从看见贺兰开始！",
                "http://quanyishucang.chuxingshi.top/uploads/20250828/1d6b247db4856dfe6583f40bc217c3ac.jpg",
                "extURL",
                "https://m.ly.com/scenery/scenerymap_221798.html",
                "宁夏漫葡旅游开发有限公司.did"],
                [
                "漫葡小镇景区入口游客中心",
                "http://quanyishucang.chuxingshi.top/uploads/20250828/12b830f568720d92c17f5710dfaf79f8.jpg"
                ],
                [str_to_hex('S')],
                date.dateTime(2024,8,26,0,30,30, -8),
                date.dateTime(2025,8,31,23,30,30, -8), addr(admin))
            
            
            ticket.mint(iwan, "ORDER0", addr(iwan))
            tokenId= ticket.getTokenID("ORDER0")
            ticket.check(tokenId, 0, addr(iwan))

            ticket.mint(iwan,  "ORDER2", addr(iwan))
            tokenId= ticket.getTokenID("ORDER2")
            ticket.check(tokenId, 0, addr(iwan))

            ticket2 = eTicket.deploy(addr(admin))
            ticket2.addBank(100, addr(admin))
            ticket2.init(["故宫博物院", 
                          "故宫博物院成立于1925年10月10日，是以明清两代皇宫和宫廷旧藏文物为基础建立起来的大型综合性古代艺术博物馆，是世界文化遗产地、全国重点文物保护单位和爱国主义教育基地",
                            "https://cctv2025.oss-cn-beijing.aliyuncs.com/gugong.png",
                            "extURL",
                            "https://isotop.oss-cn-shanghai.aliyuncs.com/20250102/2f0c555cd605483b9edd679f4e9d6d27.html",
                            "故宫博物院.did"],
                ["入口",
                    "午门及东西雁翅楼展厅",
                    "永寿宫展厅",
                    "斋宫展厅",
                    "古陶瓷研究中心",
                    "古书画研究中心",
                    "神武门展厅",
                    "入口 Image",
                    "午门及东西雁翅楼展厅 Image",
                    "永寿宫展厅 Image",
                    "斋宫展厅 Image",
                    "古陶瓷研究中心 Image",
                    "古书画研究中心 Image",
                    "神武门展厅 Image"],
                [str_to_hex('S'), str_to_hex('S'), str_to_hex('S'), str_to_hex('S'), str_to_hex('S'), str_to_hex('S'), str_to_hex('S')],
                date.dateTime(2024,8,26,0,30,30, -8),
                date.dateTime(2025,8,31,23,30,30, -8), addr(admin))
            ticket2.mint(iwan, "ORDER1", addr(admin))
            tokenId= ticket2.getTokenID("ORDER1")
            ticket2.check(tokenId, 0, addr(admin))
            ticket2.check(tokenId, 1, addr(admin))
            ticket2.check(tokenId,2,addr(admin))
            ticket2.check(tokenId, 3,addr(admin))

        if active_network in TEST_NETWORKS:
            pass
            
        if active_network in REAL_NETWORKS:
            pass

    except Exception:
        console.print_exception()
        # Test net contract address


if __name__ == "__main__":
    main()
