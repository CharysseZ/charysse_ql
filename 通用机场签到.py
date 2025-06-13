#只要机场网站''' Powered by SSPANEL ''',就可以进行签到。要确认是否是''' Powered by SSPANEL '''，在机场首页滑倒最底端就可以看到
#参数	是否必须	内容
#JC_URL	是	机场地址
#JC_EMAIL	是	账号邮箱
#JC_PASSWD	是	账号密码
"""
cron: 0 9 * * *
new Env('通用机场');
"""

import requests
import json
import os
import notify
import socket
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib3 import PoolManager

class SignInManager:
    def __init__(self):
        self.session = requests.session()
        # 配置DNS解析策略
        adapter = HTTPAdapter(
            max_retries=Retry(total=3, backoff_factor=1),
            pool_connections=2,
            pool_maxsize=10
        )
        self.session.mount('https://', adapter)
        self.session.mount('http://', adapter)
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
        }

    def login(self, url, email, passwd):
        print(f'开始对 URL: {url} 进行登录测试...')
        try:
            login_url = f'{url}/auth/login'
            data = {'email': email, 'passwd': passwd}
            r = self.session.post(url=login_url, data=data, headers=self.headers, timeout=10)
            response = json.loads(r.text)
            if response['ret'] != 1:
                print(f"对 URL: {url} 登录失败, 原因：{response['msg']}")
                return (False, response['msg'])
            else:
                print(f"对 URL: {url} 登录成功")
                return (True, "登录成功")
        except requests.exceptions.Timeout:
            print(f"对 URL: {url} 请求超时")
            return (False, "连接超时")
        except Exception as e:
            print(e)
            return (False, "登录时发生未知错误")

    def sign(self, url):
        try:
            check_url = f'{url}/user/checkin'
            client = self.session.post(url=check_url, headers=self.headers, timeout=10)
            response = json.loads(client.text)
            if response['ret'] != 1:
                print(f"对 URL: {url} 签到失败，原因：{response['msg']}")
                return (False, response['msg']+"\n")
            else:
                msg = f"签到成功:{response['msg']}\n"
                return (True, msg)
        except requests.exceptions.Timeout:
            print(f"对 URL: {url} 签到请求超时")
            return (False, "签到超时")
        except Exception as e:
            print(e)
            return (False, "签到时发生未知错误")


def main():
    urls = os.environ.get('JC_URL').split('\n')
    email = os.environ.get('JC_EMAIL')
    passwd = os.environ.get('JC_PASSWD')

    sign_in_manager = SignInManager()
    results = []

    for url in urls:
        retry_count = 0
        max_retries = 3
        success = False

        while retry_count < max_retries and not success:
            retry_count += 1
            login_success, login_result = sign_in_manager.login(url, email, passwd)
            
            if login_success:
                sign_success, sign_result = sign_in_manager.sign(url)
                if sign_success:
                    results.append(f'URL: {url} 签到成功')
                    success = True
                else:
                    if '超时' in sign_result and retry_count < max_retries:
                        print(f'第{retry_count}次重试...')
                        continue
                    results.append(f'URL: {url} 签到失败：{sign_result}')
            else:
                if '超时' in login_result and retry_count < max_retries:
                    print(f'第{retry_count}次重试...')
                    continue
                results.append(f'URL: {url} 登录失败：{login_result}')

    notify.send('机场签到', '\n'.join(results))


if __name__ == "__main__":
    main()
