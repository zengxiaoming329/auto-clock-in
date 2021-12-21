from playwright.sync_api import Playwright, sync_playwright
import send_email
import time
import os
import pytz
import datetime
from log import save_log

username = ''#账号
password = ''#密码
message = ''#关键信息，你的名字
recipient=''#收件人


def run(playwright: Playwright):
    browser = playwright.chromium.launch(headless=True)
    iphone=playwright.devices['iPhone 12 Pro']
    #创建一个实例并伪造地理位置跟时区
    context = browser.new_context(**iphone,geolocation={"longitude": 113.880063, "latitude": 22.914918},permissions=["geolocation"],locale='zh_CN',timezone_id='Asia/Shanghai')
    # Open new page
    page = context.new_page()
    try:

        # Go to https://yqfk-daka.dgut.edu.cn/
        page.goto("https://yqfk-daka.dgut.edu.cn/",timeout=60000)

        # Go to https://yqfk-daka.dgut.edu.cn/login/dgut
        page.goto("https://yqfk-daka.dgut.edu.cn/login/dgut",timeout=60000)

        # Go to https://cas.dgut.edu.cn/home/Oauth/getToken/appid/yqfkdaka/state/%2Fhome.html
        page.goto("https://cas.dgut.edu.cn/home/Oauth/getToken/appid/yqfkdaka/state/%2Fhome.html",timeout=60000)
        # Click [placeholder="请输入中央认证账号"]
        page.click("[placeholder=\"请输入中央认证账号\"]")

        # Fill [placeholder="请输入中央认证账号"]
        page.fill("[placeholder=\"请输入中央认证账号\"]", username)

        # Click [placeholder="请输入中央认证密码"]
        page.click("[placeholder=\"请输入中央认证密码\"]")

        # Fill [placeholder="请输入中央认证密码"]
        page.fill("[placeholder=\"请输入中央认证密码\"]", password)

        # Click #loginBtn
        with page.expect_navigation():
            page.click("#loginBtn")


        # page.wait_for_timeout(60000)
        # 等待关键信息的出现
        page.wait_for_selector("text=居民身份证",timeout=60000)

        # 获取关键信息
        remind1 = page.query_selector_all('.van-grid-item')
        message1 = remind1[0].text_content().strip()
        # message2 = remind1[1].text_content()

        #根据关键信息判断打卡状态
        if '已连续打卡' in message1 or '已打卡' in message1:
            save_log(message1)
            send_email.send_email(recipient,"打卡成功！", message1)
            return True
        elif '未打卡' in message1:

            #等待关键信息的出现
            page.wait_for_selector("text=居民身份证", timeout=60000)

            # submit_button=page.query_selector ('.am-button')
            #点击提交按钮
            # Click button:has-text("提交")
            page.click("button:has-text(\"提交\")")
            

            #重新加载
            page.reload()

            # 等待关键信息的出现
            page.wait_for_selector("text=居民身份证", timeout=60000)

            #获取关键信息
            remind2=page.query_selector_all('.van-grid-item')
            message3 = remind2[0].text_content().strip()
            # message4 = remind2[1].text_content()

            #判断打卡状态
            if '已连续打卡' in message3 or '未打卡' not in message3 or '已打卡' in message3:
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
    save_log('程序启动！')
    #从环境变量中获取账号、密码、关键信息、邮箱
    username = os.getenv('USERNAME')
    password = os.getenv('PASSWORD')
    message = os.getenv('NAME')
    recipient = os.getenv('EMAIL')
    if username == '' or password == '' \
            or message == '' or recipient == '':
        save_log('没有设置环境变量！')
    else:

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
