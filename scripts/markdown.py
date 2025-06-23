import json
import sys, os
import shutil
sys.path.append('scripts')
import datetime
import oss2
from oss2.credentials import EnvironmentVariableCredentialsProvider

methods={}

def trans_emoji(number: int) -> str:
    digits='⁰¹²³⁴⁵⁶⁷⁸⁹'
    return ''.join([digits[int(i)] for i in str(number)])

def dict_to_markdown(data, level=1):
    markdown = ""
    global methods
    important= False
    new_version=False
    index=1
    
    for key, value in data.items():
        key= key.strip()
        if isinstance(value, dict):
            if key=='示例':
                # 不解析示例内容
                if len(value)>0:
                    markdown += f'# <b id="sample">{key} 🌰</b>\n```json\n {json.dumps(value, indent=4, ensure_ascii=False)}\n```\n'
                continue
            else:
                if key.endswith('🇼') or key.endswith('🇷'):
                    # 对于方法，加一个矛点
                    foot= '🇷 🇼'.index(key[-1])//2+1
                    markdown += f'{level*"#"} {trans_emoji(index)} <b id="{key}">{key}</b>[^{foot}]  [🔙](#home)\n'
                    index+=1
                    sub_markdown, sub_important, sub_new_version = dict_to_markdown(value, level+1)      # 递归处理字典
                    if sub_important:
                        important=True
                    if sub_new_version:
                        new_version=True
                    markdown += sub_markdown
                    methods[key]=(data[key]["描述"],important, new_version)
                    important= False
                    new_version=False
                else:
                    if key== "方法":
                        markdown += f'{level*"#"} {key}「✔ ᵛᵉʳᶦᶠᶦᵉᵈ」\n'
                    else:
                        markdown += f'{level*"#"} {key}\n'
                    sub_markdown, sub_important, sub_new_version = dict_to_markdown(value, level+1)      # 递归处理字典
                    markdown += sub_markdown
        else:
            if key!="selector" and key!="ABI" and key!="版本更新" and len(value)> 0:
                markdown += f'- **{key}**: {value}\n'
                important=True
            else:
                if key=="版本更新" and len(value)>0:
                    new_version=True
                if key=='ABI':
                    markdown += f'- **{key}🔗**: [{value}](https://gitee.com/iwancao_admin/contract_doc/blob/master/{value})\n'
                else:
                    markdown += f'- {key}: {value}\n'
    
    return markdown, important, new_version


def gen_markdown(upload, contracts):
    global methods

    for contract in contracts:
        methods={}
        doc_file= 'abi/'+contract+'.doc.json'
        content= json.load(open(doc_file, 'r'))
        version= content["合约及版本"]
        abi_file= 'abi/'+version+'.json'
        md_file= 'abi/'+version+'.md'


        with open(md_file, 'w') as f:
            md, _, _ = dict_to_markdown(content)
            index=1
            table= '''| <b id="home">方法</b>   ╰┈➤    [🌰](#sample)  〰   [⬇](#end) | 说明  | 重要  | 更新    |\n|:-------|:-------|:-------|:-------|\n'''
            for m in methods.keys():
                if methods[m][1]:
                    mark1= "✅"
                else:
                    mark1= ''
                if methods[m][2]:
                    mark2= "✅"
                else:
                    mark2= ''
                table+= f'| {trans_emoji(index)} [{m}](#{m})| {methods[m][0]} | {mark1} | {mark2} |\n'
                index+=1
            md= table+ '\n'+ md+ f'___\n*[🔙](#home) <b id="end">updated</b>: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}          i̧͎̩̦̯͓͓͔̯̦̭s͖̰̫͈̬͕̱̠͜o̖̗̩̬̥͖͕̝͢t̢͖̤̙̲o̪͉͕̲͔͉͈̥͕͜p̘̞͎̪̩̤͓͢*\n'
            md+= '\n[^1]: 🇷读方法是同步操作，可以直接得到返回值，不消耗GAS费用。\n[^2]: 🇼写方法是异步操作，需要消耗GAS费用，没有返回值，需要通过交易hash查询链上是否成功。\n'
            print(md_file+ " updated...")
            f.write(md)
        if upload:
            shutil.copyfile(doc_file, '../contract_doc/'+version+'.doc.json')
            shutil.copyfile(abi_file, '../contract_doc/'+version+'.json')
            shutil.copyfile(md_file, '../contract_doc/'+version+'.md')
            index_dir= 'shucang/'
            auth = oss2.ProviderAuth(EnvironmentVariableCredentialsProvider())
            bucket = oss2.Bucket(auth, 'https://oss-cn-beijing.aliyuncs.com', 'yangbo2023')
            print(f"uploading to oss directory: {index_dir} \n{doc_file} \n{abi_file} \n{md_file}")
            bucket.put_object_from_file(index_dir+abi_file, abi_file)
            bucket.put_object_from_file(index_dir+'/abi/'+version+'.doc.json', doc_file)
            bucket.put_object_from_file(index_dir+md_file, md_file)

if __name__ == "__main__":
    if len(sys.argv)<2:
        print("Usage: python markdown.py [-U] CONTRACT ...")
        exit(-1)

    upload=False

    if sys.argv[1]=='-U':
        upload= True
        contracts= sys.argv[2:]
    else:
        contracts= sys.argv[1:]
    if len(contracts)==0:
        print("Usage: python markdown.py [-U] CONTRACT ...")
        exit(-1)

    gen_markdown(upload, contracts)
