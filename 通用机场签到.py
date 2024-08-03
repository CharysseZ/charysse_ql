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

class SignInManager:
    def __init__(self):
        self.session = requests.session()
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
        }

    """
    登录
    """

    def login(self, url, email, passwd):
        print(f'开始对 URL: {url} 进行登录测试...')
        try:
            login_url = f'{url}/auth/login'
            params = {}  # 请根据实际情况设置参数
            data = {
                'email': email,
                'passwd': passwd
            }
            r = self.session.post(url=login_url, data=data, headers=self.headers)
            response = json.loads(r.text)
            if response['ret']!= 1:
                print(f"对 URL: {url} 登录失败, 原因：{response['msg']}")
                return (False, response['msg'])  # 返回失败状态和原因
            else:
                print(f"对 URL: {url} 登录成功")
                return (True, "登录成功")  # 返回成功状态和消息
        except Exception as e:
            print(e)
            return (False, "登录时发生未知错误")  # 返回失败状态和未知错误原因

    """
    签到
    """

    def sign(self, url):
        try:
            check_url = f'{url}/user/checkin'
            params = {}  # 请根据实际情况设置参数
            client = self.session.post(url=check_url, params=params, headers=self.headers)
            response = json.loads(client.text)
            if response['ret']!= 1:
                print(f"对 URL: {url} 签到失败了，原因是{response['msg']}")
                return (False, response['msg']+"\n")  # 返回失败状态和原因
            else:
                self.signSuccessMsg = response
                self.signSuccessOrNot = True
                msg = (f"签到成功:{self.signSuccessMsg['msg']}\n")       
                return (True, msg)  # 返回成功状态和包含详细信息的消息
        except Exception as e:
            print(e)
            return (False, "签到时发生未知错误")  # 返回失败状态和未知错误原因


def main():
    # 从环境变量 JC_URL 中获取多个 URL，以换行符分割
    urls = os.environ.get('JC_URL').split('\n')
    # 配置用户名（一般是邮箱）
    email = os.environ.get('JC_EMAIL')
    # 配置用户名对应的密码 和上面的 email 对应上
    passwd = os.environ.get('JC_PASSWD')

    sign_in_manager = SignInManager()

    results = []
    for url in urls:
        login_success, login_result = sign_in_manager.login(url, email, passwd)
        if login_success:
            sign_success, sign_result = sign_in_manager.sign(url)
            if sign_success:
                results.append((url, sign_result))  # 直接添加签到成功的详细结果
            else:
                results.append((url, f"签到失败：{sign_result}"))  # 包含签到失败原因
        else:
            results.append((url, f"登录失败：{login_result}"))  # 包含登录失败原因

    # 一次性推送所有结果，每个结果换行
    notify.send('机场签到:','\n'.join([f'URL: {url} \n{result}' for url, result in results]))  # 格式化推送内容


if __name__ == "__main__":
    main()
