import os
import requests
import notify
import re
import time
from lxml import etree


def dailyTask():
    JYLT_Cookie = os.environ.get('JYLT_Cookie')
    msg = ""

    # 更新 User-Agent
    headers = {
        'cookie': JYLT_Cookie,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
    }

    session = requests.session()

    url_page = 'https://bbs.125.la/plugin.php?id=dsu_paulsign:sign'
    # 1.登录得到帖子
    rep = session.get(url=url_page, headers=headers)

    hot_message = re.findall(r'/thread-14(.*).html" target="_blank"', rep.text)
    # print(hot_message)

    formhash = re.findall(r'formhash=(.*)">退出', rep.text)
    print("formhash:{}".format(formhash))

    url_page = 'https://bbs.125.la/plugin.php?id=dsu_paulsign:sign&operation=qiandao&infloat=1'
    # 2.自动签到
    rep = session.post(url=url_page, headers=headers,
                       data={'formhash': formhash[0] if formhash else '', "submit": "1", "targerurl": "",
                             "todaysay": "", "qdxq": "kx"})
    try:
        msg = re.findall(r'{"status":0,"msg":"(.*)"}', rep.text)[0]
    except IndexError:
        msg = "签到结果未知，可能出现错误"
    print("签到结果：{}".format(msg))

    # 3.自动评分
    for i in range(0, len(hot_message)):
        # 动态构建帖子详情页 URL
        url_page = 'https://bbs.125.la/thread-14' + hot_message[i] + '.html'
        rep = session.get(url=url_page, headers=headers)
        if rep.status_code == 200:
            print('进入帖子详情页成功')
            tree = etree.HTML(rep.text)
            # 更加通用的方式查找评分链接的 onclick 属性
            a_list = tree.xpath('//*[@id="ak_rate"]/@onclick')
            if a_list:
                addr = a_list[0]
                str1 = addr.split(',')
                str2 = str1[1].split('&')
                tid1 = str2[2]
                pid1 = str2[3]
                tid2 = tid1.split('=')[1]
                pid2 = pid1.split('=')[1]
                pid3 = pid2.split('\'')[0]
                tid = tid2
                pid = pid3  # 获取到 tid 与 pid
                formash1 = tree.xpath('//*[@id="vfastpost"]/input/@value')
                formash = formash1[0]  # 获取到 formash
                # print("获取 pid={}与 tid={}与 formash={}成功，开始自动评分".format(pid, tid, formash))
                # 开始评分
                url_score = 'https://bbs.125.la/forum.php?mod=misc&action=rate&ratesubmit=yes&infloat=yes&inajax=1'
                data = 'formhash=' + formash + '&tid=' + tid + '&pid=' + pid + '&referer=https%3A%2F%2Fbbs.125.la%2Fforum.php%3Fmod%3Dviewthread%26tid%3D' + tid + '%26page%3D0%23pid' + pid + '&handlekey=rate&score4=%2B1&reason=%E6%84%9F%E8%B0%A2%E5%88%86%E4%BA%AB%EF%BC%8C%E5%BE%88%E7%BB%99%E5%8A%9B%EF%BC%81%7E'
                headers['Content-Type'] = 'application/x-www-form-urlencoded'
                headers['Referer'] = 'https://bbs.125.la/thread-14720892-1-1.html'

                rep_score = session.post(url=url_score, data=data, headers=headers)

                # 更加全面地检查评分结果
                if "成功" in rep_score.text or "success" in rep_score.text:
                    print("评分任务:{}，成功".format(i))
                
                else:
                    print("评分任务:{}，失败".format(i))

                score_message = re.findall(r'CDATA\[(.*)<scrip', rep_score.text)[0]
                result = re.search(r'class="showmenu">积分: (\d+)</a>', rep.text)
                if result:
                    number = result.group(1)
                    print("评分反馈:{},积分:{}".format(score_message, number))
                else:
                
                    print("未找到匹配的内容")

                time.sleep(2)
                error_limit = rep_score.text.find("超过限制")
                if error_limit!= -1:
                    print("已经完成评分次数{},24 小时评分数超过限制".format(i))
                    break;
            else:
                print("未找到评分链接")
        else:
            print('进入帖子失败')

    # 4.自动评价
    for i in range(0, len(hot_message)):
        # 动态构建帖子详情页 URL
        url_page = 'https://bbs.125.la/thread-14' + hot_message[i] + '.html'
        rep = session.get(url=url_page, headers=headers)
        if rep.status_code == 200:
            print('进入帖子详情页成功')
            tree = etree.HTML(rep.text)
            # 更加通用的方式查找评分链接的 onclick 属性
            a_list = tree.xpath('//*[@id="ak_rate"]/@onclick')
            if a_list:
                addr = a_list[0]
                str1 = addr.split(',')
                str2 = str1[1].split('&')
                tid1 = str2[2]
                pid1 = str2[3]
                tid2 = tid1.split('=')[1]
                pid2 = pid1.split('=')[1]
                pid3 = pid2.split('\'')[0]
                tid = tid2
                pid = pid3  # 获取到 tid 与 pid
                # print("获取 pid={}与 tid={}与 formash={}成功，开始自动评分".format(pid, tid, formash))
                # 开始评分
                url_score = 'https://bbs.125.la/forum.php?mod=misc&action=recommend&do=add&hash=d6e734c8&ajaxmenu=1&inajax=1&ajaxtarget=recommend_add_menu_content'
                data ='&tid=' + tid
                headers['Content-Type'] = 'application/x-www-form-urlencoded'
                headers['Referer'] = 'https://bbs.125.la/thread-14720892-1-1.html'

                rep_score = session.post(url=url_score, data=data, headers=headers)

                # 更加全面地检查评分结果
                if "+1" in rep_score.text:
                    print("评价任务:{}，成功".format(i))
                    
                else:
                    print("评价任务:{}，失败".format(i))

                score_message = re.findall(r'/>(.*)<scrip', rep_score.text)[0]
                result = re.search(r'class="showmenu">积分: (\d+)</a>', rep.text)
                if result:
                    number = result.group(1)
                    print("评价反馈:{},积分:{}".format(score_message, number))
                else:
                
                    print("未找到匹配的内容")

                time.sleep(2)

                error_limit = rep_score.text.find("超过限制")
                if error_limit!= -1:
                    print("已经完成评价次数{}".format(i))
                    break;
            else:
                 print("未找到评价链接")
        else:
            print('进入帖子失败')


    return msg


if __name__ == '__main__':
    msg = dailyTask()
    print("执行完毕~")
    notify.send("精易论坛", "签到结果：" + msg)
