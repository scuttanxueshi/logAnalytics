#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Author: AsherYang
Email : ouyangfan1991@gmail.com
Date  : 2017/12/23
Desc  : 程序使用 QSettings 保存配置类
doc @see: http://blog.csdn.net/loster_li/article/details/52841607

设置值，在window 可在注册表查找：
HKEY_USERS\S-1-5-21-1891589526-117931021-550679562-10201\Software\AsherYang\LogAnalytics\textWrapKeyGroup
"""

from PyQt4 import QtCore

import Constants

textWrapKeyGroup = 'textWrapKeyGroup'
textWrapKey = 'textWrap'
# 0: 不换行， 默认值
textWrapOn = 0
# 1：换行(自动换行)
textWrapOff = 1

# 设置 Logs-CopyToPC.bat 的路径Group
LogCommandKeyGroup = 'xtcLogKeyGroup'
copyLogPathKey = 'copyLogPath'
copyLauncherPathKey = 'copyLauncherPath'
deleteLogPathKey = 'deleteLogPath'

# 设置 QFileDialog last path
lastFilePathGroup = 'lastFilePathGroup'
lastFilePathKey = 'lastFilePath'


def init():
    QtCore.QCoreApplication.setOrganizationName(Constants.OrganizationName)
    QtCore.QCoreApplication.setOrganizationDomain(Constants.OrganizationDomain)
    QtCore.QCoreApplication.setApplicationName(Constants.ApplicationName)


# 设置文本换行。 0：不换行，1：换行； 默认为0 不换行。
def setTextWrap(value=0):
    setting = QtCore.QSettings()
    setting.beginGroup(textWrapKeyGroup)
    setting.setValue(textWrapKey, value)
    setting.endGroup()
    setting.sync()


def getTextWrap():
    setting = QtCore.QSettings()
    setting.beginGroup(textWrapKeyGroup)
    textWrapValue = setting.value(textWrapKey, 0).toString()
    setting.endGroup()
    return textWrapValue


# 设置copy system log file command dir
def setCopySystemLogCmdPath(dirPath):
    if dirPath is None:
        return
    setting = QtCore.QSettings()
    setting.beginGroup(LogCommandKeyGroup)
    setting.setValue(copyLogPathKey, dirPath)
    setting.endGroup()
    setting.sync()


def getCopySystemLogCmdPath():
    setting = QtCore.QSettings()
    setting.beginGroup(LogCommandKeyGroup)
    copyLogFilePath = setting.value(copyLogPathKey, "").toString()
    setting.endGroup()
    return copyLogFilePath


# 设置copy launcher log file command dir
def setCopyLauncherLogCmdPath(dirPath):
    if dirPath is None:
        return
    setting = QtCore.QSettings()
    setting.beginGroup(LogCommandKeyGroup)
    setting.setValue(copyLauncherPathKey, dirPath)
    setting.endGroup()
    setting.sync()


def getCopyLauncherLogCmdPath():
    setting = QtCore.QSettings()
    setting.beginGroup(LogCommandKeyGroup)
    copyLauncherFilePath = setting.value(copyLauncherPathKey, "").toString()
    setting.endGroup()
    return copyLauncherFilePath


# 记录上次QFileDialog 打开文件路径
# @see http://blog.csdn.net/shawpan/article/details/50281085
# 连接里使用 options=QtGui.QFileDialog.DontUseNativeDialog 配合dir=''可以实现功能，但是在window下也忒丑了.
# 所以决定使用 QSetting 来记录位置
def setLastDir(dirPath):
    if dirPath is None:
        return
    setting = QtCore.QSettings()
    setting.beginGroup(lastFilePathGroup)
    setting.setValue(lastFilePathKey, dirPath)
    setting.endGroup()
    setting.sync()


def getLastDir():
    setting = QtCore.QSettings()
    setting.beginGroup(lastFilePathGroup)
    # 默认路径设置为 'D://'
    lastFilePath = setting.value(lastFilePathKey, "d://").toString()
    setting.endGroup()
    return lastFilePath
