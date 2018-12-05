#-*-coding:utf8-*-

import sys, datetime, selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from threading import Timer
import browserModule, msgModule, settings

def initialDriver():
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--start-maximized")
    driver = webdriver.Chrome(chrome_options=chrome_options)
    return driver

def main(msgManager):
    user = settings.USER
    pwd  = settings.PWD

    try:
        driver = initialDriver()
        browserFlowMonitor = browserModule.browserModule(driver, msgManager, user, pwd)
        browserFlowMonitor.run()
    except Exception,e:
        msgManager.sendMsg(e)
        import traceback
        msgManager.sendMsg(traceback.format_exc())

    now = datetime.datetime.now()
    tom = now + datetime.timedelta(days=1)
    tom1 = datetime.datetime(year=tom.year, month=tom.month, day=tom.day, hour=8, minute=30)
    timeDelta = (tom1 - now).total_seconds()
    timeDelta = 60

    Timer(timeDelta, main, (msgManager,)).start()

if __name__ == '__main__':
    import pdb;pdb.set_trace()
    if len(sys.argv)>1 and sys.argv[1]=="test":
        msgManager = msgModule.TestMsgManager()
    else:
        msgManager = msgModule.WxMsgSender()
    main(msgManager)
