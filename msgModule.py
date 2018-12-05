#-*-coding:utf8-*-
import sys, logging, requests

logger = logging.getLogger("flowMonitor")
logger.setLevel(logging.DEBUG)
streamHandler = logging.StreamHandler()
fileHandler = logging.FileHandler("app.log")
formatter = logging.Formatter(
        fmt = "%(asctime)s %(message)s",
        datefmt = "%y/%m/%d_%H:%M:%S"
    )
streamHandler.setFormatter(formatter)
fileHandler.setFormatter(formatter)
logger.addHandler(streamHandler)
logger.addHandler(fileHandler)

class WxMsgSender(object):
    url = "http://127.0.0.1:7001/"
    
    def __init__(self):
        super(WxMsgSender, self).__init__()

    @classmethod
    def sendWxMsg(self, msg, type):
        """
            type: text/image
            msg: text类型时为文本，image类型时为文件路径
        """
        url = self.url + "sendMsg"
        requests.post(url, data={
                                "msg": msg,
                                "type":type
        })

    def sendMsg(self, msg, type="text", level="debug"):
        self._logMsg(msg, level)
        if level not in ['debug', "DEBUG"]:
            self.sendWxMsg(msg, type)

    def _logMsg(self, msg, level):
        if hasattr(logger, level): #利用反射来实现
            getattr(logger, level)(msg)

    def getYZM(self):
        url = self.url + "getYZM"
        return requests.get(url).json()

class TestMsgManager(WxMsgSender):
    def __init__(self):
        super(TestMsgManager, self).__init__()

    def sendMsg(self, msg, type="text", level="debug"):
        self._logMsg(msg, level)

    def getYZM(self):
        yzmCode = raw_input(u"请输入验证码：".encode("gbk"))
        return yzmCode

if __name__ == '__main__':
    if len(sys.argv)>2 and sys.argv[2]=="test":
        msgManager = TestMsgManager()
    else:
        msgManager = WxMsgSender()
    msgManager.sendMsg("This is a test")
