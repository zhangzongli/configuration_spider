#!/usr/bin/env python
# _*_ coding:utf-8 _*_
import os
import urllib
from http import cookiejar
from bs4 import BeautifulSoup



fileName = "result"

# 结果文件是否存在，存在则删除
def removeExits():
    pathOfResult = "./" + fileName
    if (os.path.exists(pathOfResult)):
        print("info:" + fileName + "文件存在，给删除喽~")
        os.remove(pathOfResult)

# 获取爬到的结果，并转成2.0数据库所需sql
def getResultToSql():
    loginUrl = "http://localhost:8080/Index!zdindex.action"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
    }
    formData = {
        'username': 'admin',
        'password': 'Tsingcon!2017'
    }
    data = urllib.parse.urlencode(formData).encode('utf-8')
    # cookie存储文件名
    cookie_filename = 'cookie.txt'
    cookie = cookiejar.MozillaCookieJar(cookie_filename)
    auth_handler = urllib.request.HTTPCookieProcessor(cookie)
    opener = urllib.request.build_opener(auth_handler)
    request = urllib.request.Request(loginUrl, data, headers)
    try:
        response = opener.open(request)
        # print(page)
    except urllib.error.URLError as e:
        print(e.code, ':', e.reason)
    # 保存cookie
    cookie.save(cookie_filename, True, True)

    # 切换项目
    changeProUrl = 'http://localhost:8080/zdmonitor/Index!ajaxChangeCurrentPcId.action?pcId=21'
    changeRequest = urllib.request.Request(changeProUrl, headers=headers)
    changeRsponse = opener.open(changeRequest)

    getUrl = 'http://localhost:8080/zdmonitor/css/configuration.css'
    getRequest = urllib.request.Request(getUrl, headers=headers)
    getReponse = opener.open(getRequest)

    # soup = BeautifulSoup(getReponse)
    # testdiv = soup.select(".two_mlmhlgd_left_waterbump01")


    print(getReponse.read().decode())


    return


if __name__ == "__main__":
    print("info: 我要开始爬组态图数据啦")
    removeExits()
    getResultToSql()
    print("info: 我已经爬完啦，sql结果在./result文件中")