from playwright.sync_api import Playwright, sync_playwright
import send_email
import time
import os
import pytz
import datetime
import sys
from log import save_log

username = ''#账号
password = ''#密码
message = ''#关键信息，你的名字
recipient=''#收件人


def run(playwright: Playwright):
    browser = playwright.chromium.launch(headless=True)

    #创建一个实例并伪造地理位置
    context = browser.new_context(geolocation={"longitude": 113.8697, "latitude": 22.9054},permissions=["geolocation"],locale='zh_CN',timezone_id='Asia/Shanghai')

    # Open new page
    page = context.new_page()
    try:
        # Go to https://yqfk.dgut.edu.cn/main
        page.goto("https://yqfk.dgut.edu.cn/main",timeout=60000)

        # Go to https://cas.dgut.edu.cn/home/Oauth/getToken/appid/illnessProtectionHome/state/home
        page.goto("https://cas.dgut.edu.cn/home/Oauth/getToken/appid/illnessProtectionHome/state/home",timeout=60000)

        # Click [placeholder="请输入中央认证账号"]
        page.click("[placeholder=\"请输入中央认证账号\"]")

        # Fill [placeholder="请输入中央认证账号"]
        page.fill("[placeholder=\"请输入中央认证账号\"]", username)

        # Click [placeholder="请输入中央认证密码"]
        page.click("[placeholder=\"请输入中央认证密码\"]")

        # Fill [placeholder="请输入中央认证密码"]
        page.fill("[placeholder=\"请输入中央认证密码\"]", password)

        # Click #loginBtn
        # with page.expect_navigation(url="https://yqfk.dgut.edu.cn/main"):
        with page.expect_navigation():
            page.click("#loginBtn")

        #获取关键信息
        page.wait_for_timeout(60000)
        remind1 = page.query_selector_all('.remind___fRE9P')
        message1 = remind1[0].text_content()
        message2 = remind1[1].text_content()

        #根据关键信息判断打卡状态
        if '已连续打卡' in message1 or '提交成功' in message2:
            save_log(message1)
            send_email.send_email(recipient,"打卡成功！", message1)
            return True
        elif '未打卡' in message1:

            #等待关键信息的出现
            page.wait_for_selector("text=%s"%message)

            # submit_button=page.query_selector ('.am-button')
            #点击提交按钮
            page.click('.am-button')

            #重新加载
            page.reload()

            # 等待关键信息的出现
            page.wait_for_selector("text=%s"%message)

            #获取关键信息
            remind2=page.query_selector_all('.remind___fRE9P')
            message3 = remind2[0].text_content()
            message4 = remind2[1].text_content()

            #判断打卡状态
            if '已连续打卡' in message3 or '未打卡' not in message3 or '提交成功' in message4:
                #写入日志
                save_log("打卡成功！")
                #发送邮件
                send_email.send_email(recipient,"打卡成功！","打卡成功！")
                return True
            elif '未打卡' in message3:
                #写入日志
                save_log("打卡失败！")
            else:
                #获取当前时间
                date = datetime.datetime.now(pytz.timezone('PRC')).strftime("%Y-%m-%d_%H-%M-%S")
                #异常情况截图并保存
                page.screenshot(path='./screenshot/' + date + '.png')
                send_email.send_email(recipient,"打卡失败！","打卡失败！",'./screenshot/' + date+ '.png')
                return False
        else:
            #异常截图
            date=datetime.datetime.now(pytz.timezone('PRC')).strftime("%Y-%m-%d_%H-%M-%S")
            page.screenshot(path='./screenshot/' + date + '.png')
            send_email.send_email(recipient,"打卡失败！", "打卡异常！", './screenshot/' + date + '.png')
            return False

    except Exception as e:
        #捕抓错误，并发送邮件
        save_log(str(e)+'1')
        date = datetime.datetime.now(pytz.timezone('PRC')).strftime("%Y-%m-%d_%H-%M-%S")
        try:
            page.screenshot(path='./screenshot/' + date + '.png')
            send_email.send_email(recipient,"打卡失败！", "打卡异常！", './screenshot/' + date + '.png')
        except Exception as e2:
            if os.path.exists('./screenshot/' + date + '.png'):
                print('截图成功！发生未知错误！')
            else:
                save_log("截图异常，浏览器可能已经关闭！"+str(e2))
        return False

    finally:
        try:
            # 关闭页面，浏览器，驱动器
            page.close()
            context.close()
            browser.close()
        except Exception as e:
            save_log("浏览器关闭异常！"+str(e))

def clock_in():
    with sync_playwright() as playwright:
        state=run(playwright)
    date = datetime.datetime.now(pytz.timezone('PRC')).strftime("%Y-%m-%d_%H-%M-%S")
    with open('time_log.txt', 'w', encoding='utf-8') as f:
        f.write(date+' '+str(state))

if __name__ == '__main__':
    #传入账号、密码、关键信息、
    if len(sys.argv) != 5:
        save_log('输入的参数数目不对！你输入的参数数量为：'+len(sys.argv))
    else:
        username=sys.argv[1]
        password=sys.argv[2]
        message=sys.argv[3]
        recipient=sys.argv[4]

        if os.path.exists('time_log.txt'):
            #读取时间日志
            with open('time_log.txt', 'r', encoding='utf-8') as f:
                line = f.readline()
            #分割字符
            m=line.split(' ')
            #解析时间
            last_time=time.strptime(m[0],"%Y-%m-%d_%H-%M-%S")
            date = datetime.datetime.now(pytz.timezone('PRC')).strftime("%Y-%m-%d_%H-%M-%S")
            now_time=time.strptime(date,"%Y-%m-%d_%H-%M-%S")
            # m[1]==True or False
            if m[1]=='True':
                if now_time[3]==0 or now_time[3]==13:
                    clock_in()
            else:
                clock_in()
        else:
            clock_in()
