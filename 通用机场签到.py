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

def login_and_checkin(url, email, passwd):
    """
    对给定的 URL 进行登录和签到操作

    Args:
        url (str): 要操作的 URL
        email (str): 登录用户名（邮箱）
        passwd (str): 登录密码
    """
    session = requests.session()
    login_url = '{}/auth/login'.format(url)
    header = {
        'origin': url,
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
    }
    data = {
        'email': email,
        'passwd': passwd
    }

    try:
        print(f'正在对 URL: {url} 进行登录...')
        response = json.loads(session.post(url=login_url, headers=header, data=data).text)
        print(f'对 URL: {url} 的登录结果: {response["msg"]}')

        check_url = '{}/user/checkin'.format(url)
        try:
            print(f'正在对 URL: {url} 进行签到...')
            result = json.loads(session.post(url=check_url, headers=header).text)
            print(f'对 URL: {url} 的签到结果: {result["msg"]}')
            content = result['msg']
            # 进行推送
            notify.send(url, content)
        except:
            print(f'对 URL: {url} 的签到失败')
            content = '对 URL: {} 签到失败'.format(url)
            notify.send(url, content)
    except:
        print(f'对 URL: {url} 的登录失败')
        content = '对 URL: {} 登录失败'.format(url)
        notify.send(url, content)

def main():
    """
    主函数，获取环境变量并执行登录和签到操作
    """
    # 从环境变量 JC_URL 中获取多个 URL，以换行符分割
    urls = os.environ.get('JC_URL').split('\n')
    # 配置用户名（一般是邮箱）
    email = os.environ.get('JC_EMAIL')
    # 配置用户名对应的密码 和上面的 email 对应上
    passwd = os.environ.get('JC_PASSWD')

    for url in urls:
        login_and_checkin(url, email, passwd)

if __name__ == "__main__":
    main()
