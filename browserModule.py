#-*-coding:utf8-*-

import os, sys, time, threading, random, datetime, base64
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from PIL import Image

import mailMoudle
import settings

class browserModule(object):
    __path                 = os.getcwd()
    __flowMonitorManageUrl = settings.flowMonitorManageUrl

    def __init__(self, driver, msgManager, user, pwd):
        self.driver = driver
        self.msgManager = msgManager
        self.user = user
        self.pwd = pwd

    def __login(self):
        self.msgManager.sendMsg(u"登录系统...")
        self.driver.get(self.__flowMonitorManageUrl)
        loginBtnLocator = (By.ID, "user_login")
        try:
            WebDriverWait(self.driver, 10, 0.5).until(EC.element_to_be_clickable(loginBtnLocator))
        except TimeoutException:
            raise Exception, u"flowMonitor:无法定位到登录按钮！"

        yzmElement = self.driver.find_element_by_id("verify")
        self.__input_login_info()
        self.msgManager.sendMsg(u"登录成功！")

    def __input_login_info(self): # 输错验证码后可以再次输入，不必刷新页面
        # loginMsgLocator = (By.ID, "div_msg") # 登录信息提示框，比如验证码错误
        yzmElement      = self.driver.find_element_by_id("verify")
        # yzmElement.click()
        try:
            self.__sendYZM(yzmElement)  # 发送图片失败，再发送一次
        except:
            self.msgManager.sendMsg(u"flowMonitor:发送验证码图片失败，尝试再次发送！", "text")
            self.__input_login_info(user, pwd)
            return
        yzm = self.__getYZM()
        self.driver.find_element_by_id("login_userName").send_keys(self.user)
        self.driver.find_element_by_id("login_passWord").send_keys(self.pwd)
        self.driver.find_element_by_id("u_verify").send_keys(yzm)
        self.driver.find_element_by_id("user_login").click()
        # try:
        #     WebDriverWait(self.driver, 3, 0.5).until(EC.visibility_of_element_located(loginMsgLocator))
        # except TimeoutException:
        #     pass
        # else:
        #     self.__input_login_info(user, pwd)

    def __sendYZM(self, yzmElement):
        self.driver.save_screenshot("flowMonitorLogin.png")
        time.sleep(1)
        left   = int(yzmElement.location["x"])
        top    = int(yzmElement.location["y"])
        right  = int(yzmElement.location["x"]+yzmElement.size["width"])
        bottom = int(yzmElement.location["y"]+yzmElement.size["height"])
        im     = Image.open("flowMonitorLogin.png")
        im     = im.crop((left, top, right, bottom))
        im.save("flowMonitorYZM.png")
        self.msgManager.sendMsg(os.path.join(self.__path, "flowMonitorYZM.png"), "image", isSendToWx=True)
        self.msgManager.sendMsg(u"flowMonitor:输入验证码,格式:@+验证码", "text", isSendToWx=True)

    def __getYZM(self):
        while True:
            yzm = self.msgManager.getYZM()
            if yzm:
                self.msgManager.sendMsg(yzm)
                break
            time.sleep(8)
        self.msgManager.sendMsg(u"flowMonitor:输入的验证码: %s" % yzm, "text", isSendToWx=True)
        return yzm

    def __openDevList(self):
        self.msgManager.sendMsg(u"打开设备列表...")
        self.driver.execute_script("index_more('设备列表','indexAction!indexMore.action?sp.type=5')")
        loadingLocator = (By.CLASS_NAME, "ui_loading")  # 通过loading图判断是否完成加载
        try:
            WebDriverWait(self.driver, 10).until(
                EC.invisibility_of_element_located(loadingLocator)
            )
            self.msgManager.sendMsg(u"成功打开设备列表")
        except TimeoutException:
            raise Exception, u"flowMonitor:超时未打开设备列表界面"

    def __screenshot(self):
        self.msgManager.sendMsg(u"截图...")
        self.__loadhtml2canvas()
        js = """
        function genScreenshot(){
            html2canvas(document.querySelector("#base > div:nth-child(2) > table"), {
                useCORS: true
            }).then(function(canvas){
                window.canvasImgContentDecoded = canvas.toDataURL("image/png");
            });
        }
        genScreenshot()
        """
        self.driver.execute_script(js)

        def canvasImgContentDecodedIsFinished(driver):
            js = "return window.canvasImgContentDecoded"
            r = driver.execute_script(js)
            if r==None:
                return False
            return r

        pngContent = WebDriverWait(self.driver, 10, 0.5).until(canvasImgContentDecodedIsFinished)
        pngContent = pngContent.replace("data:image/png;base64,", "")
        with open("out.png", "wb") as f:
            f.write(base64.b64decode(pngContent))
        self.msgManager.sendMsg(u"完成截图")

    def __loadhtml2canvas(self):
        with open("html2canvas.min.js", "rb") as f:
            self.driver.execute_script(f.read())

    def __sendmail(self):
        self.msgManager.sendMsg(u"发送邮件...", isSendToWx=True)
        i = mailMoudle.mail(settings.smtpServer, settings.smtpPort, settings.username, settings.password)
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
        self.msgManager.sendMsg(result, isSendToWx=True)

    def run(self):
        self.__login()
        time.sleep(2)
        self.__openDevList()
        self.__screenshot()
        self.__sendmail()

