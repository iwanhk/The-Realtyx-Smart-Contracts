import sys
import time
sys.path.append('scripts')
from functions import *

def loadIndex():
    """
    Reads the current index value from the file '.index', increments it by 1, writes the updated value back to the file, and returns the original index value.
    """
    with open('.index', 'r') as f:
        index= int(f.read())
    with open('.index', 'w') as f:
        f.write(str(index+1))
    return index

def testCheckCoder():
    admin= load_account('admin')
    iwan= load_account('iwan')
    if active_network in LOCAL_NETWORKS:
        DateTime.deploy(addr(admin))
        exchange= checkCoder.deploy(addr(admin))
        ticket= eTicket.deploy(addr(admin))
        ticket.addOperator(exchange, addr(admin))
    else:
        date=load(DateTime)
        index= loadIndex()
        factory=load(Factory)
        factory.deployContract(index, "eTicket", addr(admin))
        ticket= eTicket.at(factory.getContractDeployed(index, admin))
        exchange=checkCoder[-1]

    print(exchange)
    ticket.addBank(100, addr(admin))

    ticket.init([
        "漫葡·看见贺兰沉浸式演艺小镇",
        "【需预约】看见贺兰是一座中国宁夏贺兰山下的沉浸式演艺小镇。给游客一场看见自我的狂野之旅。游宁夏，从看见贺兰开始！",
        "http://quanyishucang.chuxingshi.top/uploads/20240828/1d6b247db4856dfe6583f40bc217c3ac.jpg",
        "extURL",
        "https://m.ly.com/scenery/scenerymap_221798.html",
        "宁夏漫葡旅游开发有限公司.did"],
        [
        "漫葡小镇景区入口游客中心",
        "http://quanyishucang.chuxingshi.top/uploads/20240828/12b830f568720d92c17f5710dfaf79f8.jpg"
        ],
        [str_to_hex('S')],
        date.dateTime(2025,1,1, 8),
        date.dateTime(2025,12,10, 8), addr(admin))
    timeStamp= str(time.time_ns())
    print("Gen code, secret: ", timeStamp)
    exchange.addOperator(iwan, addr(admin))
    exchange.generateCode(timeStamp, ticket, 50, addr(iwan))
    print("Get code: ", exchange.getCodes(timeStamp, ticket, iwan))

    return exchange
    
def find_ticket(name):
    owner="0x8eb045f280CAdb651dF9BBBeA86fF46a28161e18"
    factory= load(Factory)
    ret=[]
    for i in factory.getContractdeployedList(owner):
        ticket= eTicket.at(i[2])
        if name in ticket.name():
            print("Found ticket: ", ticket.name())
            print(f"order: {i[0]}, \nversion: {i[1]}, \naddress: {i[2]}, \nTime: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(i[4]))}")
            # covert timestamp to datetime
            ret.append(ticket)
            print()
    return ret
        
def testAll():
    co =testCupon()
    t1=testTicket()
    t2=testTicket2()
    card1=testCardTicket(t1, t2)
    card2=testPointTicket(t1, t2)
    return co, t1, t2, card1, card2

def testCupon():
    admin= load_account('admin')
    iwan= load_account('iwan')

    if active_network in LOCAL_NETWORKS:
        date= DateTime.deploy(addr(admin))
        cupon= eCupon.deploy(addr(admin))
    else:
        date=load(DateTime)
        index= loadIndex()
        factory=load(Factory)
        factory.deployContract(index, "eCupon", addr(admin))
        cupon= eCupon.at(factory.getContractDeployed(index, admin))
    print(cupon)
    cupon.addBank(100, addr(admin))
    cupon.addOperator(iwan, addr(admin))
    cupon.init([
        "河南省文旅消费券",
        "河南省5000家商户可使用",
        "http://quanyishucang.chuxingshi.top/uploads/20240828/1d6b247db4856dfe6583f40bc217c3ac.jpg",
        "extURL",
        "https://m.ly.com/scenery/scenerymap_221798.html",
        "河南省旅游有限公司.did"],
        [
        "10元抵用券",
        "http://quanyishucang.chuxingshi.top/uploads/20240828/12b830f568720d92c17f5710dfaf79f8.jpg"
        ],
        [str_to_hex('S')],
        date.dateTime(2024,12,10, 8),
        date.dateTime(2025,12,30, 8), addr(admin))
    
    
    cupon.mint(iwan, "ORDER100", addr(iwan))
    tokenId= cupon.getTokenID("ORDER100")
    cupon.check(tokenId, 0, addr(iwan))
    cupon.check(tokenId, 1, addr(iwan))

    cupon.setAttr(tokenId, '备注名称', "赣链存证", addr(iwan))
    cupon.setAttr(tokenId, '区块链备案号', str_to_bytes(str(cupon)), addr(iwan))
    cupon.setAttr(tokenId, '资产哈希', str_to_bytes('0xed7b1f3f'), addr(iwan))

    return cupon

def testTicket():
    admin= load_account('admin')
    iwan= load_account('iwan')

    if active_network in LOCAL_NETWORKS:
        date= DateTime.deploy(addr(admin))
        ticket= eTicket.deploy(addr(admin))
    else:
        date=load(DateTime)
        index= loadIndex()
        factory=load(Factory)
        factory.deployContract(index, "eTicket", addr(admin))
        ticket= eTicket.at(factory.getContractDeployed(index, admin))
    print(ticket)
    ticket.addBank(100, addr(admin))
    ticket.addOperator(iwan, addr(admin))

    ticket.init([
        "漫葡·看见贺兰沉浸式演艺小镇",
        "【需预约】看见贺兰是一座中国宁夏贺兰山下的沉浸式演艺小镇。给游客一场看见自我的狂野之旅。游宁夏，从看见贺兰开始！",
        "http://quanyishucang.chuxingshi.top/uploads/20240828/1d6b247db4856dfe6583f40bc217c3ac.jpg",
        "extURL",
        "https://m.ly.com/scenery/scenerymap_221798.html",
        "宁夏漫葡旅游开发有限公司.did"],
        [
        "漫葡小镇景区入口游客中心",
        "http://quanyishucang.chuxingshi.top/uploads/20240828/12b830f568720d92c17f5710dfaf79f8.jpg"
        ],
        [str_to_hex('S')],
        date.dateTime(2024,12,10, 8),
        date.dateTime(2025,12,30, 8), addr(admin))
    
    
    ticket.mint(iwan, "ORDER0", addr(iwan))
    tokenId= ticket.getTokenID("ORDER0")
    ticket.reserve(tokenId, date.dateTime(2025,3,20,8), addr(iwan))
    ticket.reserve(tokenId, time.time(), addr(iwan))
    ticket.reserve(tokenId, time.time(), addr(iwan))
    ticket.check(tokenId, 0, addr(iwan))
    ticket.check(tokenId, 1, addr(iwan))

    ticket.setAttr(tokenId, '备注名称', "赣链存证", addr(iwan))
    ticket.setAttr(tokenId, '区块链备案号', str_to_bytes(str(ticket)), addr(iwan))
    ticket.setAttr(tokenId, '资产哈希', str_to_bytes('0xed7b1f3f'), addr(iwan))


    return ticket

def testTicket2():
    admin= load_account('admin')
    iwan= load_account('iwan')
    if active_network in LOCAL_NETWORKS:
        date= DateTime.deploy(addr(admin))
        ticket2= eTicket.deploy(addr(admin))
    else:
        date=load(DateTime)
        index= loadIndex()
        factory=load(Factory)
        admin= load_account('admin')
        iwan= load_account('iwan')
        factory.deployContract(index, "eTicket", addr(admin))
        ticket2= eTicket.at(factory.getContractDeployed(index, admin))
    print(ticket2)
    ticket2.addBank(100, addr(admin))
    ticket2.init(["故宫博物院", 
                    "故宫博物院成立于1925年10月10日，\r\n“”是以明清两代皇宫和宫廷旧藏文物为基础建立起来的大型综合性古代艺术博物馆，是世界文化遗产地、全国重点文物保护单位和爱国主义教育基地",
                    "https://cctv2024.oss-cn-beijing.aliyuncs.com/gugong.png",
                    "extURL",
                    "https://isotop.oss-cn-shanghai.aliyuncs.com/20240102/2f0c555cd605483b9edd679f4e9d6d27.html",
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
        date.dateTime(2024,12,10, 8),
        date.dateTime(2025,12,11,8), addr(admin))
    
    ticket2.mint(iwan, "ORDER1", addr(admin))
    tokenId= ticket2.getTokenID("ORDER1")
    ticket2.reserve(tokenId, time.time(), addr(admin))
    ticket2.check(tokenId, 0, addr(admin))
    ticket2.check(tokenId, 1, addr(admin))
    ticket2.check(tokenId,2,addr(admin))
    ticket2.check(tokenId, 3,addr(admin))
    # ticket2.check(3, 0, addr(admin))
    # ticket2.check(3, 1, addr(admin))
    # ticket2.check(3, 2, addr(admin))


    ticket2. setAttr(tokenId, '标注', date.dateTime(2024,12,10, 8), addr(admin))

    return ticket2 

def testCardTicket(ticket, ticket2):
    admin= load_account('admin')
    iwan= load_account('iwan')
    if active_network in LOCAL_NETWORKS:
        date= DateTime.deploy(addr(admin))
        card1= eCard.deploy(addr(admin))
    else:
        date=load(DateTime)
        index= loadIndex()
        factory=load(Factory)
        admin= load_account('admin')
        iwan= load_account('iwan')
        factory.deployContract(index, "eCard", addr(admin))
        card1= eCard.at(factory.getContractDeployed(index, admin))
    print(card1)
    card1.addBank(100, addr(admin))
    card1.addOperator(iwan, addr(admin))
    card1.init(["十一特惠卡", "中青文旅特别款，仅限学生用户", 
                "https://cctv2024.oss-cn-beijing.aliyuncs.com/gugong.png",
                "https://isotop.oss-cn-shanghai.aliyuncs.com/20240102/2f0c555cd605483b9edd679f4e9d6d27.html",
                "detailsURI"
                ],
                [ticket, ticket2],
                date.dateTime(2024,12,10, 8),
                date.dateTime(2025,12,30,23,30,30, 8), addr(admin))
    ticket.addOperator(card1, addr(admin))
    # ticket.setQuota(card1, 5, addr(admin))
    ticket2.addOperator(card1, addr(admin))
    # ticket2.setQuota(card1, 5, addr(admin))
    
    card1.mint(iwan, "ORDER3", addr(iwan))
    tokenId, _, _= card1.getTokenID("ORDER3")
    card1.reserve(tokenId, 1, time.time(), addr(iwan))
    card1.reserve(tokenId, 0, time.time(), addr(iwan))
    card1.check(tokenId, 0, 0,  addr(iwan))

    card1.setAttr(tokenId, 'MAYI', time.time(), addr(iwan))
    return  card1

def testPointTicket(ticket, ticket2):
    admin= load_account('admin')
    iwan= load_account('iwan')
    if active_network in LOCAL_NETWORKS:
        date= DateTime.deploy(addr(admin))
        card2= ePointCard.deploy(addr(admin))
    else:
        date=load(DateTime)
        index= loadIndex()
        factory=load(Factory)
        admin= load_account('admin')
        iwan= load_account('iwan')
        factory.deployContract(index, "ePointCard", addr(admin))
        card2= ePointCard.at(factory.getContractDeployed(index, admin))
    print(card2)
    card2.addBank(100, addr(admin))
    card2.addOperator(iwan, addr(admin))
    card2.init(["十一特惠卡", "中青文旅特别款，仅限学生用户", 
                "https://cctv2024.oss-cn-beijing.aliyuncs.com/gugong.png",
                "https://isotop.oss-cn-shanghai.aliyuncs.com/20240102/2f0c555cd605483b9edd679f4e9d6d27.html",
                "detailsURI"
                ],
                [ticket, ticket2],
                date.dateTime(2024,12,10, 8),
                date.dateTime(2025,12,30,23,30,30, 8), addr(admin))
    card2.addBank(500, addr(admin))
    ticket.addOperator(card2, addr(admin))
    ticket.setQuota(card2, 5,addr(admin))
    ticket2.addOperator(card2, addr(admin))
    ticket2.setQuota(card2, 5,addr(admin))
    
    card2.mint(iwan, "ORDER4", addr(admin))
    tokenId, _, _= card2.getTokenID("ORDER4")
    card2.redeem(tokenId, ticket, addr(admin))
    card2.reserve(tokenId, 0, time.time(),addr(admin))
    card2.check(tokenId, 0,0, addr(admin))
    card2.setAttr(tokenId, 'MAYI', time.time(), addr(admin))

    return card2

def main():
    active_network = network.show_active()
    print("Current Network:" + active_network)
    acl = Accounts(active_network)
    # nathan = accounts.add(
    #     '0x9da140920525b01dff587494a21a909c5f635112d518e9b69f85d5c8c5076ed5')
    # zhong = accounts.add(
    #     "0x6a34b5b8c08711f18669dc6f27ed16f4a5f3e06fb884d882e186822fbfa4656")
    # nathan2 = '0x44028da500c013dd54e1e0beedc839317799b174'
    # nathan3='0xa2fdAaD6Ca69A3784753fB6671b505BA762C59eD'
    # cctv1= accounts.add('0xdc2ceb5de41d996ca92226c75b8b6b1b70716148a20dd3847fb94db31edbf276')
    # cctv2= accounts.add('0xf482e4cc4410da038f6ab23318ff77c27f6f28741a51493acb50ab529237d535')
    # cctv3= accounts.add('0xda009a51eea1d531c83ad7880a63e182414011b79f2043a65c87142236bd0199')
    # hbx= accounts.add('0x85c3b995f8dc424adc71fcf7f33642d095da29476de2331eabdb6c6ff87937e2')


    try:
        admin, creator, consumer, iwan, newbie, newbie1, dep, alice, zhao, one = acl.getAccounts()
        fei= accounts.add('0x67410d8ee1a979d5086eba6d7ae4d832fae645ca3a44242387d5293da496a17b')
        nathan= accounts.add('b14a8c9cecfa0e26c54f8b466fce7fb03d0faa17790bc070fdf6eb5b36db8e91')
        sim= accounts.add('E49A84AF8FCAA1B0779E15FCE6B89BFEA4E7F178FE4E8E0883CAF3EAC5EF7773')

        if active_network in LOCAL_NETWORKS:
            # deployer= Deployer.deploy(addr(one))
            # checkCoder= create2Deploy(deployer, CheckCoder, bytes(0), admin, '005',salts[5])
            pass

        if active_network in TEST_NETWORKS:
            date=load(DateTime)
            factory=load(Factory)
            
        if active_network in REAL_NETWORKS:
            date=load(DateTime)
            factory=load(Factory)

    except Exception:
        console.print_exception()
        # Test net contract address


if __name__ == "__main__":
    main()
