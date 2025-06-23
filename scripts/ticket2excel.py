import sys
import json
import pandas as pd
import requests
import hashlib
from rich.console import Console
from pprint import pprint
from datetime import datetime
import time
import wget
import logging
import os


RPC='https://tickets.cctvyb.com/ticket-api'
apiKey='2c9b2a3d3e58aece100fec7243fdf122'
apiSecret='d8fbe0975b26e7c8a45869f99db2db622c3562d072b62d15cfd1ad5ea20e3049'

def makeHeader(body):
    sortArgs = {}
    header = {}
    hash = hashlib.md5()

    # 当前日期和时间
    now = datetime.timestamp(datetime.now())
    header['timestamp'] = str(int(now))
    header['nonce'] = str(int(now*1000000))
    header['apiKey'] = apiKey
    sortArgs.update(header)
    sortArgs.update(body)

    content = ''
    for item in sorted(sortArgs):
        content += item+sortArgs[item]

    content += apiSecret

    hash.update(content.encode(encoding='utf-8'))

    header["content-type"] = "application/x-www-form-urlencoded"
    header['sign'] = hash.hexdigest()

    print(header)
    return header

def request(name, code, num):
    body = {}
    body['ticketName'] = name
    body['code'] = code
    body['num'] = num

    api_url = "/ticket/scenic-ticket-code/getCode"

    response = requests.post(RPC+api_url, params=body, headers=makeHeader(body))

    json = response.json()
    print(json)
    if json['code'] == 0:
        return json['results']
    else:
        print(json['msg'])

def get_code(chanel, name, jsonfile):
    df= pd.read_json(jsonfile)
    df.columns=['门票兑换码']
    df['门票名称']= name
    df['渠道'] = chanel
    df.to_excel(jsonfile.replace('.json','.xlsx'), index=False)


def main(chanel, name, code, num):
    ret = request(name, code, num)
    if ret== None or not ret.endswith('.json'):
        print("No data found")
        return

    local_file= time.strftime("%Y%m%d-%H%M%S", time.localtime())+ '.'+ chanel+ '.' + name+'.'+code+'.'+num+'.json'
    wget.download(ret, out=local_file, bar=wget.bar_thermometer)
    get_code(chanel, name, local_file)
    logging.info(f"成功领取:{num} 个 给渠道:{chanel} 名称:{name} 批次:{code} ")
    print(f"成功领取:{num} 个 给渠道:{chanel} 名称:{name} 批次:{code} ")
    # os.system(f"open {local_file.replace('.json','.xlsx')}")

if __name__ == '__main__':
    logging.basicConfig(filename='央博门票领取记录.log', filemode='a', level=logging.INFO, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    if len(sys.argv)== 5:
        main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
        exit(0)
    if len(sys.argv)== 4:
        get_code(sys.argv[1], sys.argv[2], sys.argv[3])
        exit(0)

    print("Usage: python ticket2excel.py <chanel> <name> <code> <num>") 
    print("Usage: python ticket2excel.py <chanel> <name> <jsonfile>") 

    