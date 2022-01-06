import os
import json
import random
import requests
import time
import csv
import pandas as pd
import locale
from datetime import datetime
from urllib.parse import urlparse, parse_qs

def getReadInfo(url):
    parsed_url = urlparse(url)
    url = "http://mp.weixin.qq.com/mp/getappmsgext"
    headers = {
        "Cookie": os.environ['MP_READER_COOKIE'],
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36 MicroMessenger/6.5.2.501 NetType/WIFI WindowsWechat QBCore/3.43.884.400 QQBrowser/9.0.2524.400"
    }
    data = {
        "is_only_read": "1",
        "is_temp_url": "0",                
        "appmsg_type": "9",
    }
    params = {
        "__biz": parse_qs(parsed_url.query)['__biz'][0],
        "mid": parse_qs(parsed_url.query)['mid'][0],
        "sn": parse_qs(parsed_url.query)['sn'][0],
        "idx": parse_qs(parsed_url.query)['idx'][0],
        "key": os.environ['MP_READER_KEY'],
        "pass_ticket": os.environ['MP_READER_PASS'],
        "appmsg_token": os.environ['MP_READER_TOKEN'],
        "f": "json",
        "wxtokenkey": "777",
        "devicetype": "Windows&nbsp;10",
        "clientversion": "620603c8"
    }
    content = requests.get(url, headers=headers, data=data, params=params).json()
    try:
        return content["appmsgstat"]["read_num"]
    except KeyError:
        # fallback
        origin_url = "https://mp.weixin.qq.com/mp/getappmsgext?"
        appmsgext_url = origin_url + "__biz={}&mid={}&sn={}&idx={}&appmsg_token={}&x5=1".format(params['__biz'], params['mid'], params['sn'], params['idx'], params['appmsg_token'])
        content = requests.get(appmsgext_url, headers=headers, data=data).json()
    
    try:
        return content["appmsgstat"]["read_num"]
    except KeyError:
        return -1

if __name__ == "__main__":
    if os.getenv('CI'):
        print('ENV detected!')
        url = "https://mp.weixin.qq.com/cgi-bin/appmsg"
        headers = {
            "Cookie": os.environ['MP_MANAGE_COOKIE'],
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
        }
        params = { "action": "list_ex", "begin": "0", "count": "5", "fakeid": os.environ['MP_MANAGE_FAKEID'], "type": "9", "token": "1574096682", "lang": "zh_CN", "f": "json", "ajax": "1"}
        date, title, read, link = [], [], [], []

        i = os.environ['CTRL_START']
        while i < os.environ['CTRL_END']:
            params["begin"] = str(i * 5)
            time.sleep(random.randint(5, 10))
            content_json = requests.get(url, headers=headers, params=params, verify=False).json()
            if content_json['base_resp']['ret'] == 200013:
                print("frequencey control, stop at {}".format(params["begin"]))
                break
            if len(content_json['app_msg_list']) == 0:
                print("all ariticle parsed")
                break
            for item in content_json["app_msg_list"]:
                date.append(datetime.fromtimestamp(item['create_time']).strftime("%m.%d(%a)"))
                title.append(item['title'])
                read.append(getReadInfo(item['link']))
                link.append(item['link'])
            print("Job completed for {} item(s).".format(params["begin"]))
            i += 1

        df = pd.DataFrame({"日期": date, "标题": title, "阅读量": read, "链接": link})
        df.to_csv('output.csv', encoding='utf_8_sig')
        print("job complete...")
    else:
        print('ENV not detected!')
    