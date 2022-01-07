import json
import random
import requests
import time
import pandas as pd

import locale
from datetime import datetime
try:
    locale.setlocale(locale.LC_ALL, 'zh-CN.UTF-8')
except locale.Error:
    print("Fail to set locale, continue...")

import os
from dotenv import load_dotenv
load_dotenv()
from urllib.parse import urlparse, parse_qs

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class WeChatLogin(object):
    # mock WeChat Desktop login
    def __init__(self):
        '''
        An environment should include the following:
        - WECHAT_COOKIE: login Cookie of any WeChat (not MP) Account
        - WECHAT_KEY: login key of any WeChat (not MP) Account
        - WECHAT_PASS: login pass_ticket of any WeChat (not MP) Account
        - WECHAT_TOKEN: login token of any WeChat (not MP) Account
        '''
        try:
            self.headers = {
                "Accept": "*/*",
                "Cookie": os.environ['WECHAT_COOKIE'],
                "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x6304052d)",
                "X-Requested-With": "XMLHttpRequest"
            }
            self.data = {
                "__biz": None,
                "appmsg_type": "9",
                "mid": None,
                "sn": None,
                "idx": None,
                "is_only_read": "1",
                "is_temp_url": "0",
                "is_need_ad": "0",
                # "pass_ticket": os.environ['WECHAT_PASS'],
            }
            self.params = {
                "f": "json",
                "mock": "",
                "uin": "MzM1NDIzMzE2Nw==",
                # "pass_ticket": os.environ['WECHAT_PASS'],
                # "key": os.environ['WECHAT_KEY'],
                "wxtoken": "777",
                "devicetype": "Windows&nbsp;10&nbsp;x64",
                "clientversion": "6304052d",
                "__biz": None,
                "appmsg_token": os.environ['WECHAT_TOKEN'],
                "x5": 0,
            }
            self.url = "http://mp.weixin.qq.com/mp/getappmsgext"
            self.err = ""
        except KeyError:
            # this function is not yet available
            # and as of this moment, nothing I looked into works
            # if you find a solution, contact me plz
            # self.err = "\x1b[31mError: please check your wechat login information, some may be missing.\x1b[0m"
            print(self.err)

    def setTarget(self, target_url):
        if self.err:
            return
        parsed_url = parse_qs(urlparse(target_url).query)
        for arg in ['__biz', 'mid', 'sn', 'idx']:
            self.data[arg] = parsed_url[arg][0]
        self.params['__biz'] = parsed_url['__biz'][0]
    def getMPStats(self, target_url):
        '''
        INPUT : url of a MP post (with query string)
        OUTPUT: read, like comment counts
        '''
        if self.err:
            return -1, -1, -1
        self.setTarget(target_url)
        content = requests.post(self.url, headers=self.headers, data=self.data, params=self.params, verify=False).json()
        try:
            print(content)
            return content["appmsgstat"]["read_num"], content["appmsgstat"]["like_num"], content["appmsgstat"]["comment_count"]
        except KeyError:
            self.err = "\x1b[33mWarning: please check your wechat login information, may be invalid or out of date.\x1b[0m"
            print(self.err)
            return -1, -1, -1

class WeChatMP_Crawler(object):
    def __init__(self):
        '''
        An environment should include the following:
        - MP_COOKIE: login Cookie of any WeChat *MP* Account
        - MP_TOKEN: login token of any WeChat *MP* Account
        - TARGET_FAKEID: FakeID of the TARGET WeChat *MP* Account
        '''
        try:
            self.url = "https://mp.weixin.qq.com/cgi-bin/appmsg"
            self.headers = {
                "Cookie": os.environ['MP_COOKIE'],
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
            }
            self.params = {
                "action": "list_ex",
                "begin": "0",
                "count": "5",
                "fakeid": os.environ['TARGET_FAKEID'],
                "type": "9",
                "token": os.environ['MP_TOKEN'],
                "lang": "zh_CN",
                "f": "json",
                "ajax": "1"
                }
            self.wechat = WeChatLogin()
            self.err = ""
        except KeyError:
            self.err = "\x1b[31mFatal Error: check your Wechat MP login information and the target FakeID.\x1b[0m"
            print(self.err)

    def crawler(self):
        '''
        An environment should include the following:
        - CTRL_START: start page number of MP posts (a page include 5 posts)
        - CTRL_END: end page number of MP posts (a page include 5 posts)
        '''
        if self.err:
            print(self.err)
            return
        col_date, col_title, col_link = [], [], []
        col_read, col_like, col_comment = [], [], []
        try:
            start, end = int(os.environ['CTRL_START']), int(os.environ['CTRL_END'])
        except TypeError:
            start, end = 0, 5

        for i in range(start, end):

            self.params["begin"] = str(i * 5)
            content_json = requests.get(self.url, headers=self.headers, params=self.params, verify=False).json()

            try:
                if content_json['base_resp']['ret'] == 200013:
                    print("frequencey control, stop at {}".format(self.params["begin"]))
                    break
                if len(content_json['app_msg_list']) == 0:
                    print("All posts have been parsed")
                    break
                for post in content_json["app_msg_list"]:
                    col_date.append(datetime.fromtimestamp(post['create_time']).strftime("%m.%d(%a)"))

                    col_title.append(post['title'])
                    col_link.append(post['link'])

                    read, like, comment = self.wechat.getMPStats(post['link'])
                    col_read.append(read)
                    col_like.append(like)
                    col_comment.append(comment)
            except KeyError:
                print("Fatal Error: please check your WeChat MP Login information.")
                break

            print("Job completed at %d-%d post(s)." % (i*5, i*5+4) )
            time.sleep(random.randint(5, 10))

        df = pd.DataFrame({
            "日期": col_date,
            "标题": col_title,
            "阅读量": col_read,
            "点赞数": col_like,
            "评论数": col_comment,
            "链接": col_link
        })
        df.to_csv('./data/%s@%d-%d.csv' % (self.params['fakeid'], start, end), encoding='utf_8_sig')
        print("Data saved to /data/%s@%d-%d.csv" % (self.params['fakeid'], start, end))
        print("All jobs completed, exiting...")

if __name__ == "__main__":
    wechat = WeChatLogin()
    url = "http://mp.weixin.qq.com/s?__biz=MzIxMTExODU1NA==&mid=2649907219&idx=1&sn=a147afb08156e16268db64207cc712de&chksm=8f5cf0a6b82b79b0a64ba87724d6010b732c1fe60cec2fbac96cf8ab5a8fca590e30fbf6a1eb"
    wechat.getMPStats(url)
    print(wechat.params)
    print(wechat.data)