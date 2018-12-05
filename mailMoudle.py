#-*-coding:utf8-*-
import smtplib
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

import settings

class mail(object):
    def __init__(self, smtpServer, smtpPort, username, password):
        self.smtpServer = smtpServer
        self.smtpPort = smtpPort
        self.username = username
        self.password = password


    def send(self, subject, to_address_list, cc_address_list, msgText, imgPath):
        sendObj = smtplib.SMTP(self.smtpServer, self.smtpPort)
        sendObj.ehlo()
        sendObj.starttls()

        msg = MIMEMultipart("related") # related表示可以在内容中插入图片
        msg["To"] = ",".join(to_address_list)
        msg["Cc"] = ",".join(cc_address_list)
        msg["Subject"] = Header(subject, "utf-8").encode()

        msgMIMEText = MIMEText(msgText, "html", "utf8")
        msg.attach(msgMIMEText)

        with open(imgPath, "rb") as f:
            img = MIMEImage(f.read())
            img.add_header("Content-ID", "p1")
        msg.attach(img)

        login_result = sendObj.login(self.username, self.password)

        send_result = sendObj.sendmail(self.username, to_address_list+cc_address_list, msg.as_string())

        quit_result = sendObj.quit()

        print login_result, send_result, quit_result

if __name__ == '__main__':
    smtpServer = "west.smtp.chinaunicom.cn"
    smtpPort = 587
    username = "lanbb@chinaunicom.cn"
    password = "E#en#A75"
    i = mail(smtpServer, smtpPort, username, password)

    subject = u"测试"
    to_address_list = ["lanbb@chinaunicom.cn"]
    cc_address_list = ["759775069@qq.com"]
    msgText = u'测试能否发送图片<img src="cid:dns_config" alt="dns配置">'
    imgPath = "./out.png"
    i.send(subject, to_address_list, cc_address_list, msgText, imgPath)