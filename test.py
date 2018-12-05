#-*-coding:utf8-*-

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
import time, base64

chrome_options = Options()
chrome_options.add_argument('--disable-web-security')
chrome_options.add_argument(r'--user-data-dir=D:\MyChromeDevUserData')
chrome_options.add_argument('--start-maximized')
driver = webdriver.Chrome(options=chrome_options)
# driver = webdriver.Chrome()

driver.get("http://www.kaoyan.com/")

time.sleep(10)

with open("html2canvas.min.js", "rb") as f:
	driver.execute_script(f.read())

js = """
function genScreenshot(){
	var canvasImgContentDecoded;
	html2canvas(document.querySelector("body > div.waper > div.mainCon > div:nth-child(5)"),{
		// allowTaint:true,
		useCORS:true	//浏览器需要关闭CORS才行
	}).then(function(canvas){
	    // document.body.appendChild(canvas);
    	window.canvasImgContentDecoded = canvas.toDataURL("image/png");
	});
}
genScreenshot();
"""

driver.execute_script(js)

def canvasImgContentDecodedIsFinished(driver):
	js = """
	return window.canvasImgContentDecoded
	"""
	rsp = driver.execute_script(js)
	if rsp==None:
		return False
	return rsp

pngContent = WebDriverWait(driver, 10, 0.5).until(canvasImgContentDecodedIsFinished)
pngContent = pngContent.replace("data:image/png;base64,", "")
with open("out.png", "wb") as f:
	f.write(base64.b64decode(pngContent))
# time.sleep(10)

# pngContent = driver.execute_script("return window.canvasImgContentDecoded")

# print pngContent
