# -*- coding = utf-8 -*-
# @Time : 2021/7/4 15:44
# @Author : cheng
# @File : send_email3.py
# @Software : PyCharm

import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.header import Header
from log import save_log

def send_email(subject,text=None,image=None):
    # 第三方 SMTP 服务
    mail_host = "smtp.qq.com"  # 设置服务器
    mail_user = "cheng8136623@qq.com"  # 用户名
    mail_pass = "hvanouedhnuabbeg"  # 口令

    sender = 'cheng8136623@qq.com'  #发件人
    receivers = '791154905@qq.com'  # 收件人

    msg = MIMEMultipart('related')
    msg['Subject'] = subject
    msg['From'] = Header(sender, 'utf-8')
    msg['To'] = Header(receivers, 'utf-8')
    if image and text:
        try:
            with open(image, "rb") as f:
                img_data = f.read()
            content = MIMEText('<html><body><h1>打卡失败！</h1><h2>%s</h2><img src="cid:imageid" alt="imageid"></body></html>'%text, 'html', 'utf-8')  # 正文
            msg.attach(content)
            img = MIMEImage(img_data)
            img.add_header('Content-ID', 'imageid')
            msg.attach(img)
        except FileNotFoundError as e:
            save_log("图片未找到！")
    else:
        content = MIMEText(text, 'html', 'utf-8')  # 正文
        msg.attach(content)

    try:
        smtpObj=smtplib.SMTP_SSL(mail_host, 465)
        smtpObj.login(mail_user, mail_pass)
        smtpObj.sendmail(sender, receivers, msg.as_string())
        smtpObj.quit()  # 关闭连接
        #print("邮件发送成功")
        if text:
            save_log("邮件发送成功"+text)
        else:
            save_log("邮件发送成功")
        # return True

    # except smtplib.SMTPException as e:
    except Exception as e:
        #print("Error: 无法发送邮件")
        save_log("Error: 无法发送邮件"+str(e))
        # return False
        #print(e)

