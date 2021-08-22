# -*- coding = utf-8 -*-
# @Time : 2021/7/4 13:45
# @Author : cheng
# @File : auto_clock.py
# @Software : PyCharm

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
# from selenium.common.exceptions import WebDriverException
import time
import send_email
from log import save_log

def auto_clock():
    chrome_options = Options()
    chrome_options.binary_location='./chrome/chrome'
    chrome_options.add_argument('window-size=1920x1080')  # 指定浏览器分辨率
    chrome_options.add_argument('--no-sandbox')  # 解决DevToolsActivePort文件不存在的报错
    chrome_options.add_argument('--disable-gpu')  # 谷歌文档提到需要加上这个属性来规避bug
    chrome_options.add_argument('--headless')  # 浏览器不提供可视化页面. linux下如果系统不支持可视化不加这条会启动失败
    driver = webdriver.Chrome(executable_path='./chromedriver',options=chrome_options)  # 导入设置,并创建一个窗口
    try:
        # 网站授权定位
        driver.execute_cdp_cmd(
            "Browser.grantPermissions",
            {
                "origin": "https://yqfk.dgut.edu.cn/main",
                "permissions": ["geolocation"]
            },
        )
        # 浏览器位置信息设置
        driver.execute_cdp_cmd(
            "Emulation.setGeolocationOverride",
            {
                "latitude": 22.2336,
                "longitude": 111.2118,
                "accuracy": 100,
            },
        )
        driver.get('https://yqfk.dgut.edu.cn/main')  # 访问网页
        time.sleep(10)
        driver.implicitly_wait(30)
        username =driver.find_element_by_id('username')
        username.send_keys('201841416226')
        password=driver.find_element_by_id('casPassword')
        password.send_keys('QSC8136623ww')
        time.sleep(1)
        login=driver.find_element_by_id('loginBtn')
        login.click()
        time.sleep(2)
        for i in range(5):
            inputs=driver.find_elements_by_tag_name ('input')
            if not inputs:
                driver.refresh()
            else:
                break
        time.sleep(5)
        remind1=driver.find_elements_by_class_name('remind___fRE9P')
        message1 = remind1[0].text
        message2 = remind1[1].text
        if '已连续打卡' in message1 or '提交成功' in message2:
            save_log(message1)
            send_email.send_email("打卡通知：已打卡！", message1)
            return True
        elif '未打卡' in message1:
            for j in range(3):
                submit_button=driver.find_element_by_class_name ('am-button')
                submit_button.click()
                time.sleep(5)
                driver.refresh()
                remind2 = driver.find_elements_by_class_name('remind___fRE9P')
                message3 = remind2[0].text
                message4 = remind2[1].text
                if '已连续打卡' in message3 or '未打卡' not in message3 or '提交成功' in message4:
                    save_log("打卡成功！")
                    send_email.send_email("打卡成功！","打卡成功！")
                    return True
                elif '未打卡' in message3:
                    save_log("打卡失败！")
                else:
                    date = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
                    driver.get_screenshot_as_file('./screenshot/' + date + '.png')
                    # send_email.send_email("打卡成功！","打卡成功！",'./screenshot/' + date+ '.png')
            send_email.send_email("打卡失败！","打卡失败！")
            return False
        else:
            date = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
            driver.get_screenshot_as_file('./screenshot/' + date + '.png')
            send_email.send_email("打卡异常！", "打卡异常！", './screenshot/' + date + '.png')
            return False
    except Exception as e:
        save_log(str(e))
        date = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
        try:
            driver.get_screenshot_as_file('./screenshot/' + date + '.png')
            send_email.send_email("打卡失败！", "打卡异常！", './screenshot/' + date + '.png')
        except Exception as e2:
            save_log("截图异常，浏览器可能已经关闭！"+str(e2))
        return False
    finally:
        try:
            driver.quit()
        except Exception as e:
            save_log("浏览器关闭异常！")
