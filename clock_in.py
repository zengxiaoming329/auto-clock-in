from playwright.sync_api import Playwright, sync_playwright
import send_email
import time
import os
import pytz
import datetime
from log import save_log


def run(playwright: Playwright):
    browser = playwright.chromium.launch(headless=False)

    #创建一个实例并伪造地理位置
    context = browser.new_context(geolocation={"longitude": 113.8697, "latitude": 22.9054},permissions=["geolocation"])

    # Open new page
    page = context.new_page()
    try:
        # Go to https://yqfk.dgut.edu.cn/main
        page.goto("https://yqfk.dgut.edu.cn/main")

        # Go to https://cas.dgut.edu.cn/home/Oauth/getToken/appid/illnessProtectionHome/state/home
        page.goto("https://cas.dgut.edu.cn/home/Oauth/getToken/appid/illnessProtectionHome/state/home")

        # Click [placeholder="请输入中央认证账号"]
        page.click("[placeholder=\"请输入中央认证账号\"]")

        # Fill [placeholder="请输入中央认证账号"]
        page.fill("[placeholder=\"请输入中央认证账号\"]", "201841416226")

        # Click [placeholder="请输入中央认证密码"]
        page.click("[placeholder=\"请输入中央认证密码\"]")

        # Fill [placeholder="请输入中央认证密码"]
        page.fill("[placeholder=\"请输入中央认证密码\"]", "QSC8136623ww")

        # Click #loginBtn
        # with page.expect_navigation(url="https://yqfk.dgut.edu.cn/main"):
        with page.expect_navigation():
            page.click("#loginBtn")

        #获取关键信息
        remind1 = page.query_selector_all('.remind___fRE9P')
        # print(len(remind1))
        message1 = remind1[0].text_content()
        message2 = remind1[1].text_content()
        # message3 = remind1[2].text_content()
        # print(message1,message2,message3)

        #根据关键信息判断打卡状态
        if '已连续打卡' in message1 or '提交成功' in message2:
            save_log(message1)
            send_email.send_email("打卡通知！", message1)
            return True
        elif '未打卡' in message1:
            # print('wei')
            # for j in range(3):
            #等待关键信息的出现
            page.wait_for_selector("text=叶家成")

            # submit_button=page.query_selector ('.am-button')
            #点击提交按钮
            page.click('.am-button')
            # time.sleep(5)

            #重新加载
            page.reload()

            # 等待关键信息的出现
            page.wait_for_selector("text=叶家成")

            #获取关键信息
            remind2=page.query_selector_all('.remind___fRE9P')
            # remind2 = driver.find_elements_by_class_name('remind___fRE9P')
            message3 = remind2[0].text_content()
            message4 = remind2[1].text_content()

            #判断打卡状态
            if '已连续打卡' in message3 or '未打卡' not in message3 or '提交成功' in message4:
                #写入日志
                save_log("打卡成功！")
                #发送邮件
                send_email.send_email("打卡通知！","打卡成功！")
                return True
            elif '未打卡' in message3:
                #写入日志
                save_log("打卡失败！")
            else:
                #获取当前时间
                date = datetime.datetime.now(pytz.timezone('PRC')).strftime("%Y-%m-%d_%H-%M-%S")

                # date = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
                #异常情况截图并保存
                page.screenshot(path='./screenshot/' + date + '.png')
                # driver.get_screenshot_as_file('./screenshot/' + date + '.png')
                send_email.send_email("打卡通知！","打卡失败！",'./screenshot/' + date+ '.png')
                return False
            # send_email.send_email("打卡通知！","打卡失败！")
            # return False
        else:
            date=datetime.datetime.now(pytz.timezone('PRC')).strftime("%Y-%m-%d_%H-%M-%S")
            # date = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
            page.screenshot(path='./screenshot/' + date + '.png')
            # driver.get_screenshot_as_file('./screenshot/' + date + '.png')
            send_email.send_email("打卡通知！", "打卡异常！", './screenshot/' + date + '.png')
            return False
        # Click text=您已连续打卡472天
        # page.click("text=您已连续打卡472天", button="right")

        # Click text=您已提交成功！您可一天一出校园！
        # page.click("text=您已提交成功！您可一天一出校园！")
    except Exception as e:
        save_log(str(e)+'1')
        date = datetime.datetime.now(pytz.timezone('PRC')).strftime("%Y-%m-%d_%H-%M-%S")
        # date = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
        try:
            # driver.get_screenshot_as_file('./screenshot/' + date + '.png')
            page.screenshot(path='./screenshot/' + date + '.png')
            s=send_email.send_email("打卡通知！", "打卡异常！", './screenshot/' + date + '.png')
        except Exception as e2:
            if os.path.exists('./screenshot/' + date + '.png'):
                print('截图成功！发生未知错误！')
            else:
                save_log("截图异常，浏览器可能已经关闭！"+str(e2))
        return False
        # print('error')
    # Close page
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
    # lt=time.localtime()
    # date = time.strftime("%Y-%m-%d_%H-%M-%S", lt)
    date = datetime.datetime.now(pytz.timezone('PRC')).strftime("%Y-%m-%d_%H-%M-%S")

    # if lt[3] == 0 or lt[3]==13:
    #     n='1'
    # else:
    #     n='2'
    with open('time_log.txt', 'w', encoding='utf-8') as f:
        f.write(date+' '+str(state))
    # return state
if __name__ == '__main__':
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
        if m[1]:
            if now_time[3]==0 or now_time[3]==13:
                clock_in()
            # if (last_time[3]==0 or last_time[3]==13) and m[2]=='1':
            #     clock_in()
            # elif m[2]=='2':

            # if abs(last_time[3]-now_time[3])>13:
            #     clock_in()
        else:
            clock_in()
    else:
        clock_in()
