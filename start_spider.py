#!/usr/bin/env python
# _*_ coding:utf-8 _*_
import os
import urllib
import pymysql
import configparser
from http import cookiejar
from bs4 import BeautifulSoup
import re
import json

# -------------- 读取配置文件开始 ------------------
config = configparser.ConfigParser()
config.read("db.cfg")
dbInfo = config.sections()[0]
host = config.get(dbInfo, "host")
port = config.getint(dbInfo, "port")
user = config.get(dbInfo, "user")
passwd = config.get(dbInfo, "passwd")
db = config.get(dbInfo, "db")

# 目标数据库链接
db = pymysql.Connect(
    host=host,
    port=port,
    user=user,
    passwd=passwd,
    db=db,
    charset='utf8'
)

# 获取游标
cursor = db.cursor()

# 1.0数据库项目id
oneProIdInfo = config.sections()[1]
oldProjectId = config.get(oneProIdInfo, "one_projectId")

# 2.0数据库项目id
proIdInfo = config.sections()[2]
project_id = config.get(proIdInfo, "two_projectId")

# 组态图底图 name
configPicInfo = config.sections()[3]
configPicName = config.get(configPicInfo, "config_pic_name")

# -------------- 读取配置文件结束 ------------------

# ------------2.0该项目的设备信息----------------
chillerList = []
chilledPumpList = []
coolingPumpList = []
coolingTowerList = []
# ------------2.0该项目的设备信息----------------

fileName = "result"

# 结果文件是否存在，存在则删除
def removeExits():
    pathOfResult = "./" + fileName
    if (os.path.exists(pathOfResult)):
        print("info:" + fileName + "文件存在，给删除喽~")
        os.remove(pathOfResult)

# 获取爬到的结果，并转成2.0数据库所需sql
def getResultToSql():
    # 插入组态图底图
    sqlStr = "insert into configuration_config (project_id, pic_url) VALUES ("+project_id+", '"+configPicName+"' );\n"
    loginUrl = "https://hvac.ecopm.cn/ecopm/Index!zdindex.action"
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
    if (os.path.exists("./cookie.txt")):
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
    changeProUrl = 'https://hvac.ecopm.cn/ecopm/zdmonitor/Index!ajaxChangeCurrentPcId.action?pcId=' + oldProjectId
    changeRequest = urllib.request.Request(changeProUrl, headers=headers)
    changeResponse = opener.open(changeRequest)

    # 获取组态图界面html
    configUrl = "https://hvac.ecopm.cn/ecopm/zdmonitor/Configuration.action"
    configRequest = urllib.request.Request(configUrl, headers=headers)
    configResponse = opener.open(configRequest)

    # 获取css
    getUrl = 'https://hvac.ecopm.cn/ecopm/zdmonitor/css/configuration.css'
    getRequest = urllib.request.Request(getUrl, headers=headers)
    getReponse = opener.open(getRequest)

    soupConfig = BeautifulSoup(configResponse.read().decode(), features="html.parser")

    soupCss = BeautifulSoup(getReponse.read().decode(), features="html.parser")

    # 获取map数据
    areaList = soupConfig.find_all("area")
    i = 0
    for area in areaList:
        coords = area['coords']
        areaSql = ""
        if i < len(chilledPumpList):
            sqlStr = sqlStr + "insert into configuration_config (project_id, device_id, device_type_code, css_coords, model) VALUES ("+project_id+", '"+str(
                chilledPumpList[i][0])+"', 'CHILLED_PUMP_FLAG', '"+coords+"', 'fixBox' );\n"
        elif i >= len(chilledPumpList) and i < len(coolingPumpList) + len(chilledPumpList):
            sqlStr = sqlStr + "insert into configuration_config (project_id, device_id, device_type_code, css_coords, model) VALUES (" + project_id + ", '"+str(
                coolingPumpList[i-len(chilledPumpList)][0])+"', 'COOLING_PUMP_FLAG', '" + coords + "', 'fixBox' );\n"
        elif i >= len(chilledPumpList) + len(coolingPumpList) and i < len(chilledPumpList) + len(coolingPumpList) + len(chillerList):
            sqlStr = sqlStr + "insert into configuration_config (project_id, device_id, device_type_code, css_coords, model) VALUES (" + project_id + ", '" + str(
                coolingPumpList[i - len(chilledPumpList) - len(coolingPumpList)][0]) + "', 'CHILLER_FLAG', '" + coords + "', 'fixBox' );\n"
        elif i >= len(chilledPumpList) + len(coolingPumpList) + len(chillerList):
            sqlStr = sqlStr + "insert into configuration_config (project_id, device_id, device_type_code, css_coords, model) VALUES (" + project_id + ", '" + str(
                coolingPumpList[i - len(chilledPumpList) - len(coolingPumpList) - len(chillerList)][0]) + "', 'COOLING_TOWER_FLAG', '" + coords + "', 'fixBox' );\n"
        i = i + 1

    # 获取隐藏悬浮窗的数据
    window = soupConfig.select('.configuration_alertmsg > div')
    soupCssStr = str(soupCss).replace("\r", "").replace("\n", "").replace("\t", "")
    for div in window:
        className = str(div.attrs['class']).replace("[\'", "").replace("\']", "")
        startData = str(re.findall(r'.'+className+'{(.*)}', soupCssStr))
        data_json = json.dumps(startData[0:startData.find("}")].replace(";", ","))
        width = data_json.width


    # testdiv = soup.select(".two_mlmhlgd_left_waterbump01")


    # print(getReponse.read().decode())

    file = open(fileName, "x", encoding='utf-8')
    file.write(sqlStr)
    file.close()

    return

def getDeviceIdList():
    # 获取主机各设备id
    chillerSql = "select device_id from chiller_config  where project_id = " + project_id
    cursor.execute(chillerSql)
    global chillerList
    chillerList = cursor.fetchall()

    # 获取冷冻泵各设备id
    chilledPumpSql = "select w.device_id from water_pump_config w INNER JOIN sys_param_config s on w.device_type = s.`value`" \
                 " and w.project_id = s.project_id where s.`code` = \"CHILLED_PUMP_FLAG\" and w.project_id = " + project_id
    cursor.execute(chilledPumpSql)
    global chilledPumpList
    chilledPumpList = cursor.fetchall()

    # 获取冷却泵的各设备Id
    coolingPumpSql = "select w.device_id from water_pump_config w INNER JOIN sys_param_config s on w.device_type = s.`value`" \
                 " and w.project_id = s.project_id where s.`code` = \"COOLING_PUMP_FLAG\" and w.project_id = " + project_id
    cursor.execute(coolingPumpSql)
    global coolingPumpList
    coolingPumpList = cursor.fetchall()

    # 获取冷却塔的各设备Id
    coolingTowerSql = "select device_id from cooling_tower_config where project_id = " + project_id
    cursor.execute(coolingTowerSql)
    global coolingTowerList
    coolingTowerList = cursor.fetchall()


if __name__ == "__main__":
    print("info: 我要开始爬组态图数据啦")
    removeExits()
    getDeviceIdList()
    getResultToSql()
    print("info: 我已经爬完啦，sql结果在./result文件中")