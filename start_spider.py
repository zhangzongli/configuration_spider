#!/usr/bin/env python
# _*_ coding:utf-8 _*_
import os

fileName = "result"

# 结果文件是否存在，存在则删除
def removeExits():
    pathOfResult = "./" + fileName
    if (os.path.exists(pathOfResult)):
        print("info:" + fileName + "文件存在，给删除喽~")
        os.remove(pathOfResult)

# 获取爬到的结果，并转成2.0数据库所需sql
def getResultToSql():

    return


if __name__ == "__main__":
    print("info: 我要开始爬组态图数据啦")
    removeExits()
    print("info: 我已经爬完啦，sql结果在./result文件中")