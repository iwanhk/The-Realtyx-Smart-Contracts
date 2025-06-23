import json
import sys, os
sys.path.append('scripts')
from functions import *

deploy_commands={
    "DateTime"	:	"DateTime.deploy(addr(admin))",
    # "DDS"	:	"DDS.deploy(addr(admin))",
    # "DIDAsset1155"	:	"DIDAsset1155.deploy(addr(admin))",
    "DIDAsset721"	:	"DIDAsset721.deploy(addr(admin))",
    # "DIDCard721"	:	"DIDCard721.deploy(addr(admin))",
    # "DID"	:	"DID.deploy(addr(admin))",
    # "DID2"	:	"DID2.deploy(addr(admin))",
    # "DIDPoints"	:	"DIDPoints.deploy(addr(admin))",
    # "DIDRight721"	:	"DIDRight721.deploy(addr(admin))",
    # "Deployer"	:	"Deployer.deploy(addr(admin))",
    "Factory"	:	"Factory.deploy(addr(admin))",
    # "Forwarder"	:	"Forwarder.deploy(addr(admin))",
    # "ISOTOP1010"	:	"ISOTOP1010.deploy(addr(admin))",
    # "ISOTOP1011"	:	"ISOTOP1011.deploy(addr(admin))",
    # "ISOTOP1012"	:	"ISOTOP1012.deploy(addr(admin))",
    # "ISOTOP1013"	:	"ISOTOP1013.deploy(addr(admin))",
    # "ISOTOP1014"	:	"ISOTOP1014.deploy(addr(admin))",
    # "ISOTOP1015"	:	"ISOTOP1015.deploy(addr(admin))",
    # "ISOTOP1016"	:	"ISOTOP1016.deploy(addr(admin))",
    # "ISOTOP1016A"	:	"ISOTOP1016A.deploy(addr(admin))",
    "ISOTOP1017"	:	"ISOTOP1017.deploy(addr(admin))",
    # "ISOTOP1018"	:	"ISOTOP1018.deploy(addr(admin))",
    # "ISOTOP1019"	:	"ISOTOP1019.deploy(addr(admin))",
    # "ISOTOP101A"	:	"ISOTOP101A.deploy(addr(admin))",
    # "ISOTOP1020"	:	"ISOTOP1020.deploy(addr(admin))",
    # "ISOTOP1021"	:	"ISOTOP1021.deploy(addr(admin))",
    # "ISOTOP1022"	:	"ISOTOP1022.deploy(addr(admin))",
    # "ISOTOP1052"	:	"ISOTOP1052.deploy(addr(admin))",
    # "ISOTOP1052Single"	:	"ISOTOP1052Single.deploy(addr(admin))",
    "ISOTOP1053"	:	"ISOTOP1053.deploy(addr(admin))",
    # "ISOTOP1054"	:	"ISOTOP1054.deploy(addr(admin))",
    # "TaojingLing"	:	"TaojingLing.deploy(addr(admin))",
    "eCard"	        :	"eCard.deploy(addr(admin))",
    "ePointCard"	:	"ePointCard.deploy(addr(admin))",
    "eTicket"	    :	"eTicket.deploy(addr(admin))",
    "manghe"	    :	"manghe.deploy(addr(admin))",
    "eCupon"	    :	"eCupon.deploy(addr(admin))",
    "testABI"       :   "testABI.deploy(addr(admin))",
    # "exchangeCode"  : "exchangeCode.deploy(addr(admin))"
    "XinYuan"	    :	"XinYuan.deploy(addr(admin))"
}

def merge_value(old_value, levels):
    if len(levels)==1 and levels[0]=="示例":
        if "示例" in old_value:
            return old_value["示例"]
        else:
            return {}
    if not isinstance(old_value, dict):
        # print(f"Not a dict {old_value}")
        return ""
    for level in levels:
        # print(f"merge {level} in {old_value}")
        if level not in old_value:
            # print(f"Not found {level} in {old_value}")
            return ""
        else:
            if len(levels)==1:
                if isinstance(old_value[level], str):
                    return old_value[level]
                return ""
            return merge_value(old_value[level], levels[1:])

def main():
    if not os.path.exists('abi'):
        os.mkdir('abi')
    acl = Accounts(active_network)

    try:
        admin, creator, consumer, iwan, newbie, newbie1, dep, alice, zhao, one = acl.getAccounts()
        for contract, command in deploy_commands.items():
            new_doc={}
            try:
                print("Deploying " + contract + "...")
                instance= eval(command)
            except:
                print(f"{command} failed")
                continue
            
            metadata = {}
            metadata['abi'] = eval(contract + '.abi')
            version= instance.contractInfo()
            doc_file='abi/'+contract+'.doc.json'
            abi_file= 'abi/'+ version+'.json'
            
            # metadata['bytecode'] = eval(contract + '.bytecode')
            if not os.path.exists(abi_file) or metadata['abi']!= open(abi_file, 'r').read():
                with open(abi_file, 'w') as f:
                    json.dump(metadata['abi'], f, indent=4, ensure_ascii=False)

            
            old_doc={}
            if os.path.exists(doc_file):
                old_doc= json.load(open(doc_file, 'r'))

            new_doc['合约及版本']= version
            new_doc['获取方法']= merge_value(old_doc, ['获取方法'])
            new_doc['描述']=merge_value(old_doc, ['描述'])
            new_doc["ABI"]= version+'.json'
            new_doc['方法']={}

            for item in metadata['abi']:
                if item['type'] != 'function':
                    continue

                if item['stateMutability'] == "view" or item['stateMutability'] == "pure":
                    method_type= "🇷"
                else:
                    method_type= "🇼"
                signature= item['name']+'('+','.join([i['type'] for i in item['inputs']])+')'
                method= signature+method_type
                new_doc['方法'][method]= {}
                new_doc['方法'][method]["描述"]= merge_value(old_doc, ['方法', method, '描述'])
                new_doc['方法'][method]["selector"]=  web3.keccak(text=signature)[:4].hex()
                new_doc['方法'][method]["版本更新"]= ""

                if len(item['inputs'])>0:
                    new_doc['方法'][method]["参数"]= {}
                if len(item['outputs'])>0:
                    new_doc['方法'][method]["返回值"]= {}

                new_doc['方法'][method]["备注"]= merge_value(old_doc, ['方法', method, '备注'])

                
                for input in item['inputs']:
                    arg= f"[{input['type']}] {input['name']}"
                    new_doc['方法'][method]['参数'][arg]= merge_value(old_doc, ['方法', method, '参数', arg])
                for output in item['outputs']:
                    arg= f"[{output['type']}] {output['name']}"
                    new_doc['方法'][method]['返回值'][arg]= merge_value(old_doc, ['方法', method, '返回值', arg])
                    new_doc['方法'][method]["备注"]=merge_value(old_doc, ['方法', method, '备注'])

            new_doc['示例']=merge_value(old_doc, ['示例'])
            if new_doc!= old_doc:
                with open(doc_file, 'w') as f:
                    json.dump(new_doc, f, indent=4, ensure_ascii=False)


    except Exception:
        console.print_exception()
        # Test net contract address


if __name__ == "__main__":
    main()
