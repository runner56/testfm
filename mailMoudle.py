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


    def send(self, subject, to_address_list, cc_address_list, msgText, imgDict):
        sendObj = smtplib.SMTP(self.smtpServer, self.smtpPort)
        sendObj.ehlo()
        sendObj.starttls()

        msg = MIMEMultipart("related") # related表示可以在内容中插入图片
        msg["To"] = ",".join(to_address_list)
        msg["Cc"] = ",".join(cc_address_list)
        msg["Subject"] = Header(subject, "utf-8").encode()

        msgMIMEText = MIMEText(msgText, "html", "utf8")
        msg.attach(msgMIMEText)

        for k,imgPath in imgDict.items():
            with open(imgPath, "rb") as f:
                img = MIMEImage(f.read())
                img.add_header("Content-ID", k)
            msg.attach(img)

        login_result = sendObj.login(self.username, self.password)

        send_result = sendObj.sendmail(self.username, to_address_list+cc_address_list, msg.as_string())

        quit_result = sendObj.quit()

        return "login_result:%s\nsend_result:%s\nquit_result:%s" % (login_result, send_result, quit_result)

if __name__ == '__main__':
    import time
    i = mail(settings.smtpServer, settings.smtpPort, settings.username, settings.password)
    lt = time.localtime()    
    ft = time.strftime('%y/%m/%d_%H:%M:%S', lt)
    subject = "%s(%s)" % (u"IDC流量监控平台运行状态", ft)
    msgText = u"<p><span style='color:green;font-weight:bold'>绿色</span>代表采集设备运行状态正常，<span style='color:red;font-weight:bold'>红色</span>代表异常</p>"
    msgText += u"<p>截图时间：%s</p><img src='cid:p1'/>" % ft
    msgText += u"<p style='font-weight:bold'>流量监控平台拓扑图</p><img src='cid:p2'/>"
    imgDict = {
        "p1":"./out.png",
        "p2":"./topo.jpg"
    }
    result = i.send(subject, settings.to_address_list, settings.cc_address_list, msgText, imgDict)
    print result