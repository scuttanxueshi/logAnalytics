#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Author: AsherYang
Email : ouyangfan1991@gmail.com
Date  : 2018/11/27
Desc  : 通过浏览器下载LOG 日志

pyInstaller 打包时遇到console=False无法启动chrome的问题的解决方案
https://stackoverflow.com/questions/46639052/pyinstaller-one-file-no-console-does-not-work-fatal-error
"""
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import time

XTC_CALL_FAIL_LOG_URL = r'http://172.28.199.58/watch/index_prod.html#/watchda_web/logCollection'
CHROME_DRIVER_PATH = r'D:/program_file/python/chromedriver.exe'
USER_NAME = r'20251572'
USER_PWD = r'123456'


class DownloadLogByWeb:
    def __init__(self):
        chrome_options = webdriver.ChromeOptions()
        # 不显示chrome 浏览器，即无界面模式
        # chrome_options.add_argument('--headless')
        # 0 为禁止弹出窗口， 指定下载路径为 E:\call_fail_log
        # https://www.cnblogs.com/caoj/p/7815837.html
        chrome_prefs = {'profile.default_content_settings.popups': 0, 'download.default_directory': 'E:\\call_fail_log'}
        chrome_options.add_experimental_option('prefs', chrome_prefs)
        self.driver = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH, chrome_options=chrome_options)
        # self.driver = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH)
        self.driver.get(XTC_CALL_FAIL_LOG_URL)
        self.user_name = USER_NAME
        self.password = USER_PWD
        self.binder_number_list = []
        self.call_back = None

    def setCallBack(self, call_back):
        self.call_back = call_back

    def setLoginInfo(self, userName, password):
        self.user_name = userName
        self.password = password

    def login(self):
        driver = self.driver
        userNameFieldCssSelect = r'#username'
        passwordFieldCssSelect = r'#pwdtxt'
        loginBtnFieldCssSelect = r'input.button_blue'
        logoCssSelect = r'div.content-header.right-side'
        logMenuCssSelect = r'ul.menu-tree > li.menu-item > span.menu-name'
        logCollectMenuCssSelect = r'ul.sub-menu-tree > a:first-child > li.menu-item.sub-menu-item > span.menu-name'
        try:
            userNameFieldElement = WebDriverWait(driver, 10).until(lambda driver: driver.find_elements_by_css_selector(userNameFieldCssSelect))
            passwordFieldElement = WebDriverWait(driver, 10).until(lambda driver: driver.find_elements_by_css_selector(passwordFieldCssSelect))
            loginBtnFieldElement = WebDriverWait(driver, 10).until(lambda driver: driver.find_elements_by_css_selector(loginBtnFieldCssSelect))
            userNameFieldElement[0].clear()
            userNameFieldElement[0].send_keys(self.user_name)
            passwordFieldElement[0].clear()
            passwordFieldElement[0].send_keys(self.password)
            loginBtnFieldElement[0].click()
            # login over
            WebDriverWait(driver, 10).until(lambda driver: driver.find_elements_by_css_selector(logoCssSelect))
            logMenuFieldElement = WebDriverWait(driver, 10).until(lambda driver: driver.find_elements_by_css_selector(logMenuCssSelect))
            logMenuFieldElement[0].click()
            logCollectFieldElement = WebDriverWait(driver, 10).until(lambda driver: driver.find_elements_by_css_selector(logCollectMenuCssSelect))
            logCollectFieldElement[0].click()
            # print '--> logMenuFieldElement: ', logMenuFieldElement
            # print '--> logCollectFieldElement: ', logCollectFieldElement
        except Exception as e:
            raise e
        # finally:
            # driver.close()
            # driver.quit()

    def setBinderNumberList(self, binder_number_list):
        self.binder_number_list = binder_number_list

    # 开始下载LOG
    def downloadLog(self):
        time.sleep(3)
        if not self.binder_number_list:
            return
        # print 'len(binder_number_list): ', len(self.binder_number_list)
        for binderNumber in self.binder_number_list:
            self.doDownloadSingleLog(binderNumber)

    # 单个LOG下载
    def doDownloadSingleLog(self, binder_number):
        # strTmp = u'请开始下载: ' + binder_number
        # self.doCallBack(strTmp)
        driver = self.driver
        inputBinderCssSelect = r'#bandNumberInput'
        searchBinderBtnCssSelect = r'div.search-btn.btn.lime-btn.inline-block'
        try:
            inputBinderElement = WebDriverWait(driver, 10).until(lambda driver: driver.find_elements_by_css_selector(inputBinderCssSelect))
            searchBinderBtnElement = WebDriverWait(driver, 10).until(lambda driver: driver.find_elements_by_css_selector(searchBinderBtnCssSelect))
            inputBinderElement[0].clear()
            inputBinderElement[0].send_keys(binder_number)
            searchBinderBtnElement[0].click()
            time.sleep(10)
        except Exception as e:
            raise e
        pass

    # 回调函数
    def doCallBack(self, msg):
        if self.call_back:
            self.call_back(msg)


if __name__ == '__main__':
    dlLogByWeb = DownloadLogByWeb()
    dlLogByWeb.setLoginInfo(USER_NAME, USER_PWD)
    dlLogByWeb.login()
    pass
