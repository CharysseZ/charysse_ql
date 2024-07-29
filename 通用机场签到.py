#只要机场网站''' Powered by SSPANEL ''',就可以进行签到。要确认是否是''' Powered by SSPANEL '''，在机场首页滑倒最底端就可以看到
#参数	是否必须	内容
#JC_URL	是	机场地址
#JC_EMAIL	是	账号邮箱
#JC_PASSWD	是	账号密码

import requests, json, re, os
import notify
session = requests.session()
# 机场的地址
url = os.environ.get('JC_URL')
# 配置用户名（一般是邮箱）
email = os.environ.get('JC_EMAIL')
# 配置用户名对应的密码 和上面的email对应上
passwd = os.environ.get('JC_PASSWD')

login_url = '{}/auth/login'.format(url)
check_url = '{}/user/checkin'.format(url)


header = {
        'origin': url,
        'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
}
data = {
        'email': email,
        'passwd': passwd
}
try:
    print('进行登录...')
    response = json.loads(session.post(url=login_url,headers=header,data=data).text)
    print(response['msg'])
    # 进行签到
    result = json.loads(session.post(url=check_url,headers=header).text)
    print(result['msg'])
    content = result['msg']
    # 进行推送
    notify.send(url,content)
except:
    content = '签到失败'
    print(content)
    notify.send(url,content)
