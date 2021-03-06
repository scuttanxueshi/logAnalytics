# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'LogAnalytics.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

import StringIO
import os
import sys
import threading

from PyQt4 import QtCore, QtGui
from PyQt4.QtNetwork import QLocalServer, QLocalSocket

import Constants
import FileUtil
import QSettingsUtil
import RunSysCommand
import SupportFiles
import WinCommandEnCoding
import WinRightKeyReg
from RunSysCommand import RunCopyXTCLogCmd
from WinRightKeyReg import RegisterCmdWinKey
from WinRightKeyReg import RegisterLogAnalyticsWinKey
from CallFailWindow import CallFailWindow
from SplitExcelWindow import SplitExcelWindow
from EncodeUtil import _translate, _fromUtf8
from IconResourceUtil import resource_path
import multiprocessing

reload(sys)
# print sys.getdefaultencoding()
sys.setdefaultencoding('utf8')
# print sys.getdefaultencoding()


class Ui_MainWidget(object):
    def setupUi(self, mainWindow, localServer, argv=None):
        self.mainwindow = mainWindow
        # 解决多终端问题 http://www.oschina.net/code/snippet_54100_629
        self.localServer = localServer
        # 保存所有 Tab 的 originalData
        self.originalDataList = []
        # 保存所有 Tab 的 filePath
        self.tabFilePathList = []
        # 获取当前脚本所在的目录
        self.sysArg0 = argv[0]
        self.filterConfigFilePath = os.path.join(os.path.dirname(os.path.realpath(self.sysArg0)),
                                                 Constants.filterConfigFileName)
        mainWindow.setObjectName(_fromUtf8("MainWindow"))
        mainWindow.setWindowIcon(QtGui.QIcon(resource_path('img/log.png')))
        # MainWindow.resize(800, 600)
        self.centralwidget = QtGui.QWidget(mainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))

        self.statusBar = QtGui.QStatusBar(mainWindow)
        self.menubar = QtGui.QMenuBar(mainWindow)
        file = self.menubar.addMenu(' &File')
        openFileAction = QtGui.QAction('Open file', mainWindow)
        openFileAction.setStatusTip(_fromUtf8('选择日志文件'))
        openFileAction.setShortcut('Ctrl+O')
        openFileAction.connect(openFileAction, QtCore.SIGNAL('triggered()'), self.openFile)

        saveLogAnalyticsAction = QtGui.QAction('Save Analytics', mainWindow)
        saveLogAnalyticsAction.setStatusTip(_fromUtf8('保存日志分析文件'))
        saveLogAnalyticsAction.setShortcut('Ctrl+Alt+S')
        saveLogAnalyticsAction.connect(saveLogAnalyticsAction, QtCore.SIGNAL('triggered()'), self.saveLogAnalyticsFile)

        loadLogAnalyticsAction = QtGui.QAction('Load Analytics', mainWindow)
        loadLogAnalyticsAction.setStatusTip(_fromUtf8('加载日志分析文件'))
        loadLogAnalyticsAction.setShortcut('Ctrl+Alt+O')
        loadLogAnalyticsAction.connect(loadLogAnalyticsAction, QtCore.SIGNAL('triggered()'), self.loadLogAnalyticsFile)

        file.addAction(openFileAction)
        file.addAction(loadLogAnalyticsAction)
        file.addAction(saveLogAnalyticsAction)

        setting = self.menubar.addMenu('&Setting')
        settingLogAnalyticsWinRightKeyAction = QtGui.QAction('set log key', mainWindow)
        settingLogAnalyticsWinRightKeyAction.setStatusTip(_fromUtf8('注册LogAnalytics到右键'))
        settingLogAnalyticsWinRightKeyAction.connect(settingLogAnalyticsWinRightKeyAction, QtCore.SIGNAL('triggered()'),
                                                     self.setLogAnalyticsWinRightKey)
        setting.addAction(settingLogAnalyticsWinRightKeyAction)

        settingCmdRightKeyAction = QtGui.QAction('set cmd key', mainWindow)
        settingCmdRightKeyAction.setStatusTip(_fromUtf8('注册cmdPrompt到右键'))
        settingCmdRightKeyAction.connect(settingCmdRightKeyAction, QtCore.SIGNAL('triggered()'),
                                         self.setCmdWinRightKey)
        setting.addAction(settingCmdRightKeyAction)
        setting.addSeparator()

        # 设置"copy log file" command path
        settingCopyLogCmdPathAction = QtGui.QAction('copy system cmd', mainWindow)
        settingCopyLogCmdPathAction.setStatusTip(_fromUtf8('设置copy system log cmd 脚本路径'))
        settingCopyLogCmdPathAction.connect(settingCopyLogCmdPathAction, QtCore.SIGNAL('triggered()'),
                                            self.setCopySystemLogCmdPath)
        setting.addAction(settingCopyLogCmdPathAction)

        settingCopyLauncherLogCmdPathAction = QtGui.QAction('copy launcher cmd', mainWindow)
        settingCopyLauncherLogCmdPathAction.setStatusTip(_fromUtf8('设置copy launcher log cmd 脚本路径'))
        settingCopyLauncherLogCmdPathAction.connect(settingCopyLauncherLogCmdPathAction, QtCore.SIGNAL('triggered()'),
                                                    self.setCopyLauncherLogCmdPath)
        setting.addAction(settingCopyLauncherLogCmdPathAction)
        setting.addSeparator()

        # 设置文本换行
        self.settingTextWrapAction = QtGui.QAction('set text wrap', mainWindow)
        checkIconPixmap = QtGui.QPixmap(resource_path('img/check.png'))
        self.settingTextWrapAction.setIcon(QtGui.QIcon(checkIconPixmap))
        self.settingTextWrapAction.setStatusTip(_fromUtf8('自动换行'))
        self.setTextWrapIconVisible()
        self.settingTextWrapAction.connect(self.settingTextWrapAction, QtCore.SIGNAL('triggered()'),
                                           self.changeTextWrap)
        setting.addAction(self.settingTextWrapAction)

        # Auto Analytics分析, 可用于分析特定关键字，输出结果
        autoAnalytics = self.menubar.addMenu('&Auto')
        autoAnalyticsCallFailAction = QtGui.QAction('call fail analytics', mainWindow)
        autoAnalyticsCallFailAction.setStatusTip(_fromUtf8('掉话分析'))
        autoAnalyticsCallFailAction.connect(autoAnalyticsCallFailAction, QtCore.SIGNAL('triggered()'),
                                            self.showAutoAnalyticsCallFailDialog)
        autoAnalyticsCallFailAction.setShortcut('Ctrl+Alt+F')
        autoAnalytics.addAction(autoAnalyticsCallFailAction)

        # Tools
        tools = self.menubar.addMenu('&Tools')
        # cmd tools:　copy xtc system log to D:\xxFolder
        self.toolCopyXtcSystemLogAction = QtGui.QAction('copy system log', mainWindow)
        self.toolCopyXtcSystemLogAction.setStatusTip(_fromUtf8('从SDCard拷贝System Log到D盘'))
        self.toolCopyXtcSystemLogAction.setShortcut('Ctrl+Alt+C')
        self.toolCopyXtcSystemLogAction.connect(self.toolCopyXtcSystemLogAction, QtCore.SIGNAL('triggered()'),
                                                self.copyXtcSystemLogThread)
        self.toolCopyXtcSystemLogAction.connect(self.toolCopyXtcSystemLogAction,
                                                QtCore.SIGNAL('copyLogTipSignal(QString)'),
                                                self.showCopyLogTips)
        tools.addAction(self.toolCopyXtcSystemLogAction)
        # cmd tools:　copy xtc launcher log to D:\xxFolder
        self.toolCopyXtcLauncherLogAction = QtGui.QAction('copy launcher log', mainWindow)
        self.toolCopyXtcLauncherLogAction.setStatusTip(_fromUtf8('从SDCard拷贝Launcher Log到D盘'))
        self.toolCopyXtcLauncherLogAction.setShortcut('Ctrl+Alt+L')
        self.toolCopyXtcLauncherLogAction.connect(self.toolCopyXtcLauncherLogAction, QtCore.SIGNAL('triggered()'),
                                                  self.copyXtcLauncherLogThread)
        self.toolCopyXtcLauncherLogAction.connect(self.toolCopyXtcLauncherLogAction,
                                                  QtCore.SIGNAL('copyLogTipSignal(QString)'),
                                                  self.showCopyLogTips)
        tools.addAction(self.toolCopyXtcLauncherLogAction)
        tools.addSeparator()
        # split excel data tools.
        self.toolSplitExcelAction = QtGui.QAction('split excel data', mainWindow)
        self.toolSplitExcelAction.setStatusTip(_fromUtf8('拆分Excel 数据'))
        self.toolSplitExcelAction.connect(self.toolSplitExcelAction, QtCore.SIGNAL('triggered()'), self.showSplitExcelDialog)
        tools.addAction(self.toolSplitExcelAction)
        tools.addSeparator()

        # 添加到 mainWindow
        mainWindow.setMenuBar(self.menubar)
        mainWindow.setStatusBar(self.statusBar)

        # vBoxLayout 和 hBoxLayout 的选择依据是：根据2个控件的排列方向，上下排(vBoxLayout)还是左右排(hBoxLayout)
        vBoxLayout = QtGui.QVBoxLayout()
        hBboxLayout = QtGui.QHBoxLayout()

        # 需要设置添加到 self.centralwidget
        self.logAnalyticsEdit = QtGui.QTextEdit()
        self.logAnalyticsEdit.setFont(self.getFont('Monospace'))

        self.filterLineEdit = QtGui.QLineEdit()
        self.filterLineEdit.setFont(self.getFont('Consolas'))
        self.filterBtn = QtGui.QPushButton()
        self.filterBtn.setText(u'Filter')
        self.saveKeyWordBtn = QtGui.QPushButton()
        self.saveKeyWordBtn.setText(u'Save')
        self.LoadKeyWorkBtn = QtGui.QPushButton()
        self.LoadKeyWorkBtn.setText(u'Load')
        self.filterBtn.setFixedWidth(60)
        self.saveKeyWordBtn.setFixedWidth(60)
        self.LoadKeyWorkBtn.setFixedWidth(60)

        self.filterBtn.setFont(self.getFont('Consolas'))
        self.saveKeyWordBtn.setFont(self.getFont('Consolas'))
        self.LoadKeyWorkBtn.setFont(self.getFont('Consolas'))

        self.filterBtn.setStatusTip(u'请输入过滤字符，多个字符间以 "|" 分割(Ctrl+F)')
        self.filterBtn.setShortcut('Ctrl+F')
        self.saveKeyWordBtn.setStatusTip(u'保存过滤条件(Ctrl+B)')
        self.saveKeyWordBtn.setShortcut('Ctrl+B')
        self.LoadKeyWorkBtn.setStatusTip(u'加载过滤条件(Ctrl+L)')
        self.LoadKeyWorkBtn.setShortcut('Ctrl+L')

        self.filterBtn.connect(self.filterBtn, QtCore.SIGNAL('clicked()'), self.filter)
        self.saveKeyWordBtn.connect(self.saveKeyWordBtn, QtCore.SIGNAL('clicked()'), self.saveKeyWord)
        self.LoadKeyWorkBtn.connect(self.LoadKeyWorkBtn, QtCore.SIGNAL('clicked()'), self.loadKeyWord)

        self.tabWidget = QtGui.QTabWidget()
        self.tabWidget.setTabsClosable(True)
        self.tabWidget.setMovable(True)
        self.tabWidget.connect(self.tabWidget, QtCore.SIGNAL('tabCloseRequested(int)'), self.tabClose)
        self.tabWidget.connect(self.tabWidget, QtCore.SIGNAL('currentChanged(int)'), self.currentTabChange)
        self.tabWidget.connect(mainWindow, QtCore.SIGNAL('closeCurrentTabSignal()'), self.currentTabCloseSlot)
        self.tabWidget.connect(mainWindow, QtCore.SIGNAL('dropOpenFileSignal(QString)'), self.setLogTxt)

        self.filterLineEdit.setMaximumHeight(28)
        self.filterLineEdit.setMinimumHeight(28)
        hFilterSplitter = QtGui.QSplitter(QtCore.Qt.Horizontal)
        hFilterSplitter.addWidget(self.filterLineEdit)
        hFilterSplitter.addWidget(self.filterBtn)
        hFilterSplitter.addWidget(self.saveKeyWordBtn)
        hFilterSplitter.addWidget(self.LoadKeyWorkBtn)
        # 禁止鼠标拖动
        hHandler = hFilterSplitter.handle(1)
        if hHandler:
            hHandler.setDisabled(True)

        vSplitter = QtGui.QSplitter(QtCore.Qt.Vertical)
        vSplitter.addWidget(hFilterSplitter)
        vSplitter.addWidget(self.tabWidget)
        vHandler = vSplitter.handle(1)
        if vHandler:
            vHandler.setDisabled(True)

        self.hSplitter = QtGui.QSplitter(QtCore.Qt.Horizontal)
        self.hSplitter.addWidget(vSplitter)
        self.hSplitter.addWidget(self.logAnalyticsEdit)
        # 按比例分配 5:3
        self.hSplitter.setStretchFactor(0, 5)
        self.hSplitter.setStretchFactor(1, 3)
        # feature: arrow/collapse button to open/hidden logAnalyticsEdit
        # 设置LogAnalyticsEdit split 显示与隐藏
        hHandler = self.hSplitter.handle(1)
        toggleButton = QtGui.QPushButton(hHandler)
        toggleButton.setShortcut('Ctrl+T')
        toggleButton.move(0, 300)
        toggleButton.resize(10, 50)
        toggleButton.connect(toggleButton, QtCore.SIGNAL('clicked()'), self.handleSplitterButton)
        # 设置 LogAnalyticsEdit 默认隐藏
        self.hSplitter.setSizes([1, 0])
        hBboxLayout.addWidget(self.hSplitter)
        vBoxLayout.addLayout(hBboxLayout)

        self.centralwidget.setLayout(vBoxLayout)

        # 处理右键打开，或者直接拖文件到桌面图标启动。
        # argv 参数大于1，说明有其他文件路径。第0位是当前应用程序，第1位则是我们需要处理的文件路径
        # 注意这里，是需要处理sys.argv 的编码问题的，方法是使用 WinCommandEnCoding.py 处理
        if len(argv) > 1:
            filePath = argv[1]
            if SupportFiles.hasSupportFile(filePath):
                self.setLogTxt(_translate('', filePath, None))
        # 监听新到来的连接(新的终端被打开)
        self.localServer.connect(localServer, QtCore.SIGNAL('newConnection()'), self.newLocalSocketConnection)

        mainWindow.setCentralWidget(self.centralwidget)

    def getFont(self, fontStr):
        font = QtGui.QFont()
        font.setFamily(fontStr)
        font.setPointSize(10)
        font.setFixedPitch(True)
        return font

    # 设置LogAnalyticsEdit split 显示与隐藏
    def handleSplitterButton(self):
        # print all(self.hSplitter.sizes())
        if not all(self.hSplitter.sizes()):
            self.hSplitter.setSizes([1, 1])
        else:
            self.hSplitter.setSizes([1, 0])

    # 设置windows 右键打开方式, 加入windows 注册表
    def setLogAnalyticsWinRightKey(self):
        programPath = os.path.join(os.path.dirname(os.path.realpath(self.sysArg0)), WinRightKeyReg.prog_name)
        winRightKey = RegisterLogAnalyticsWinKey(programPath)
        winRightKey.register()

    def setCmdWinRightKey(self):
        cmdWinKey = RegisterCmdWinKey()
        cmdWinKey.register()

    # 设置copy system log cmd path
    def setCopySystemLogCmdPath(self):
        copyLogCmdPath = QSettingsUtil.getCopySystemLogCmdPath()
        filePath = unicode(QtGui.QFileDialog.getOpenFileName(None, 'Open file', copyLogCmdPath, 'log cmd(*.bat)'))
        if not filePath:
            return
        print "bat file path = ", filePath.strip()
        QSettingsUtil.setCopySystemLogCmdPath(str(_translate("", filePath.strip(), None)))

    # 设置 copy launcher log cmd path
    def setCopyLauncherLogCmdPath(self):
        copyLauncherCmdPath = QSettingsUtil.getCopyLauncherLogCmdPath()
        filePath = unicode(QtGui.QFileDialog.getOpenFileName(None, 'Open file', copyLauncherCmdPath,
                                                             'launcher cmd(*.bat)'))
        if not filePath:
            return
        print 'launcher bat file path = ', filePath.strip()
        QSettingsUtil.setCopyLauncherLogCmdPath(str(_translate("", filePath.strip(), None)))

    # copy xtc system log to D:\xxFolder in thread
    def copyXtcSystemLogThread(self):
        self.showCopyLogTips(u'start copy system log..')
        copySystemLogCmdPath = QSettingsUtil.getCopySystemLogCmdPath()
        if not copySystemLogCmdPath:
            copySystemLogCmdPath = RunSysCommand.copyXtcSystemLogPath
        thread = threading.Thread(target=self.copyXtcLog, args=(copySystemLogCmdPath,))
        thread.setDaemon(True)
        thread.start()

    # copy xtc launcher log to D:\xxFolder in thread
    def copyXtcLauncherLogThread(self):
        self.showCopyLogTips(u'start copy launcher log..')
        copyLauncherLogCmdPath = QSettingsUtil.getCopyLauncherLogCmdPath()
        if not copyLauncherLogCmdPath:
            copyLauncherLogCmdPath = RunSysCommand.copyXtcLauncherLogPath
        thread = threading.Thread(target=self.copyXtcLog, args=(copyLauncherLogCmdPath,))
        thread.setDaemon(True)
        thread.start()

    def copyXtcLog(self, cmdPath):
        copyXtcLogCommand = RunCopyXTCLogCmd()
        result = copyXtcLogCommand.run(str(_translate("", cmdPath, None)), callback=self.emitCopyLogTip)
        # print 'result = ', result.returncode
        if result.returncode == 0:
            print 'copy log over'

    def showCopyLogTips(self, msg):
        self.statusBar.showMessage(msg)

    def copyLogTipSignal(self, msg):
        pass

    # emit tip 解决在子线程中刷新UI 的问题。' QWidget::repaint: Recursive repaint detected '
    def emitCopyLogTip(self, msg):
        self.toolCopyXtcSystemLogAction.emit(QtCore.SIGNAL('copyLogTipSignal(QString)'), msg)

    # 设置文本换行
    def changeTextWrap(self):
        if QSettingsUtil.getTextWrap() == QtCore.QString.number(QSettingsUtil.textWrapOn):
            self.settingTextWrapAction.setIconVisibleInMenu(True)
            # textWrapOff 自动换行
            self.setTextWrapOff()
        else:
            self.settingTextWrapAction.setIconVisibleInMenu(False)
            # textWrapOn 不换行
            self.setTextWrapOn()

    def setTextWrapOn(self):
        QSettingsUtil.setTextWrap(QSettingsUtil.textWrapOn)
        self.setShowTabTxtWrap()
        # print QSettingsUtil.getTextWrap()

    def setTextWrapOff(self):
        QSettingsUtil.setTextWrap(QSettingsUtil.textWrapOff)
        self.setShowTabTxtWrap()

    def setTextWrapIconVisible(self):
        if QSettingsUtil.getTextWrap() == QtCore.QString.number(QSettingsUtil.textWrapOn):
            self.settingTextWrapAction.setIconVisibleInMenu(False)
        else:
            self.settingTextWrapAction.setIconVisibleInMenu(True)

    def setShowTabTxtWrap(self):
        tabCount = self.tabWidget.count()
        txtWrap = QtGui.QTextEdit.NoWrap
        if QSettingsUtil.getTextWrap() == QtCore.QString.number(QSettingsUtil.textWrapOn):
            txtWrap = QtGui.QTextEdit.NoWrap
        else:
            txtWrap = QtGui.QTextEdit.WidgetWidth
        for index in range(0, tabCount):
            self.tabWidget.widget(index).setLineWrapMode(txtWrap)

    # 打开文件，对应 Ctrl+O
    def openFile(self):
        filePath = unicode(QtGui.QFileDialog.getOpenFileName(
            None, 'Open file', self.getLastOpenDir(), 'log files(*.log *.md *.txt)'))
        if not filePath:
            return
        QSettingsUtil.setLastDir(FileUtil.getFileDir(str(_translate("", filePath.strip(), None))))
        self.setLogTxt(filePath)

    # 加载LOG 到显示区，同时将current tab name 设置为当前文件名
    def setLogTxt(self, filePath):
        if not filePath:
            return
        filePath = _translate('', filePath, None)
        file = QtCore.QFile(filePath)
        if not file.open(QtCore.QIODevice.ReadOnly):
            return
        stream = QtCore.QTextStream(file)
        stream.setCodec('UTF-8')
        data = stream.readAll()
        file.close()
        loadTextEdit = QtGui.QTextEdit()
        loadTextEdit.setFont(self.getFont('Monospace'))
        loadTextEdit.setText(_translate('', data, None))
        if QSettingsUtil.getTextWrap() == QtCore.QString.number(QSettingsUtil.textWrapOn):
            # NoWrap: 不自动换行
            loadTextEdit.setLineWrapMode(QtGui.QTextEdit.NoWrap)
        else:
            # WidgetWidth：自动换行
            loadTextEdit.setLineWrapMode(QtGui.QTextEdit.WidgetWidth)
        filePath = str(_translate('', filePath, None))
        fileName = FileUtil.getFileName(filePath)
        # print 'fileName= %s' %fileName
        self.originalDataList.append(data)
        self.tabFilePathList.append(_translate('', filePath, None))
        self.tabWidget.addTab(loadTextEdit, _translate('', fileName, None))

    # 获取QFileDialog 上次打开的路径
    def getLastOpenDir(self):
        # open last remember directory
        lastPath = QSettingsUtil.getLastDir()
        if not QtCore.QFile(lastPath).exists():
            lastPath = 'd://'
        return lastPath

    def saveLogAnalyticsFile(self):
        logEditTxt = _translate('', self.logAnalyticsEdit.toPlainText(), None)
        logTxtStream = QtCore.QTextStream(logEditTxt)
        logTxtStream.setCodec('UTF-8')
        firstLine = logTxtStream.readLine()
        logTxtName = ''
        if firstLine:
            logTxtName = str(firstLine)
            # logTxtName = firstTxt.split('\n')[0]
            if logTxtName.find('#') >= 0:
                # 字符串切片
                logTxtName = logTxtName[(logTxtName.find('#') + 1):] + '.md'
            else:
                logTxtName += '.txt'
        # print logTxtName
        logTxtName = _translate('', logTxtName, None)
        fileName = unicode(QtGui.QFileDialog.getSaveFileName(None, 'save File', './' + logTxtName))
        if not fileName:
            return

        try:
            out_file = QtCore.QFile(_translate('', fileName, None))
            if not out_file.open(QtCore.QIODevice.ReadWrite):
                return
            stream = QtCore.QTextStream(out_file)
            stream.setCodec('UTF-8')
            # stream 流操作方式
            stream << _translate('', logEditTxt, None)
            stream.flush()
            out_file.close()
        except IOError:
            print u'未能保存Log分析文件'
            return

    def loadLogAnalyticsFile(self):
        supportFiles = SupportFiles.files()
        if not supportFiles:
            print "not support one file !"
            return
        supportFileStr = ''
        for file in supportFiles:
            supportFileStr += "*." + file + " "
        supportFileStr = supportFileStr.strip()
        fileName = unicode(QtGui.QFileDialog.getOpenFileName(
            None, 'Open file', self.getLastOpenDir(), 'log files(' + supportFileStr + ')'))
        if not fileName:
            return
        QSettingsUtil.setLastDir(FileUtil.getFileDir(str(_translate("", fileName.strip(), None))))
        file = QtCore.QFile(fileName)
        if not file.open(QtCore.QIODevice.ReadOnly):
            return
        stream = QtCore.QTextStream(file)
        stream.setCodec('UTF-8')
        data = stream.readAll()
        file.close()
        self.logAnalyticsEdit.setText(_translate('', data, None))
        # open logAnalyticsEdit show
        self.hSplitter.setSizes([1, 1])

    def currentTabCloseSlot(self):
        tabIndex = self.tabWidget.currentIndex()
        if tabIndex < 0:
            return
        self.tabClose(tabIndex)

    # 当前 tab 关闭
    def tabClose(self, index):
        self.tabWidget.removeTab(index)
        del self.originalDataList[index]
        del self.tabFilePathList[index]
        if len(self.tabFilePathList) == 0:
            self.mainwindow.setWindowTitle(Constants.ApplicationName)

    def currentTabChange(self, index):
        self.mainwindow.setWindowTitle(self.tabFilePathList[index])

    # 获取当前 Tab 的 OriginalData
    def getCurrentTabOriginalData(self):
        tabIndex = self.tabWidget.currentIndex()
        if self.tabWidget.count() == 0 or tabIndex == -1:
            return
        return self.originalDataList[tabIndex]

    def filter(self):
        currentTabOriginalData = self.getCurrentTabOriginalData()
        if not currentTabOriginalData:
            return
        if not self.filterLineEdit.text():
            self.tabWidget.currentWidget().setText(_translate('', currentTabOriginalData, None))
            return
        filterList = str(self.filterLineEdit.text()).split('|')
        currentTxt = StringIO.StringIO(currentTabOriginalData)
        filterTxt = ''
        # print currentTxt.readline()
        while True:
            textLine = str(_translate('', currentTxt.readline(), None))
            if textLine == '':
                print 'read over. '
                break
            textLineLower = textLine.lower()
            for filterWord in filterList:
                if not filterWord.strip():
                    continue
                filterWord = filterWord.lower()
                keywordIndex = textLineLower.find(filterWord.strip())
                if keywordIndex != -1:
                    # print keywordIndex
                    filterTxt += textLine
        # print filterTxt
        self.tabWidget.currentWidget().setText(_translate('', filterTxt, None))

    def saveKeyWord(self):
        filterStr = self.filterLineEdit.text()
        if not filterStr:
            return
        filterFile = QtCore.QFile(self.filterConfigFilePath)
        if not filterFile.open(QtCore.QFile.ReadWrite):
            filterFile.close()
            return
        oldTxt = QtCore.QTextStream(filterFile)
        oldTxt.setCodec('UTF-8')
        # 注意readAll() 读取一次之后，就不能再重复读了，后面重复读取不到数据
        allFilter = str(oldTxt.readAll())
        filterStr = str(filterStr).lower()
        if allFilter:
            allFilterList = allFilter.split('#@$')
            for oneFilter in allFilterList:
                if oneFilter == filterStr:
                    return
            # 加入分隔符
            oldTxt << '#@$'
        # << 写入操作
        oldTxt << _translate('', filterStr, None)
        oldTxt.flush()
        filterFile.close()

    def loadKeyWord(self):
        filterFile = QtCore.QFile(self.filterConfigFilePath)
        if not filterFile.open(QtCore.QFile.ReadOnly):
            filterFile.close()
            return
        oldTxt = QtCore.QTextStream(filterFile)
        oldTxt.setCodec('UTF-8')
        allFilter = str(oldTxt.readAll())
        allFilterList = allFilter.split('#@$')
        self.showFilterDialog(allFilterList)
        filterFile.close()

    def showFilterDialog(self, filterList):
        if not filterList:
            return
        filterDialog = QtGui.QDialog()
        filterDialog.setWindowTitle(u'过滤条件')
        filterDialog.resize(260, 400)
        filterLayout = QtGui.QGridLayout()
        self.filterListWidget = QtGui.QListWidget()
        listItemIndex = 0
        for filterStr in filterList:
            # listItem = QtGui.QListWidgetItem(_translate('', filterStr, None))
            # listItem.setIcon(QtGui.QIcon('img/delete.png'))
            if not filterStr:
                continue
            listItem = QtGui.QListWidgetItem()
            customListItemWidget = CustomFilterItemWidget()
            customListItemWidget.setItemText(_translate('', filterStr, None))
            customListItemWidget.setItemIcon(resource_path('img/delete.png'))
            customListItemWidget.setItemIndex(listItemIndex)
            listItem.setSizeHint(customListItemWidget.sizeHint())
            listItemIndex += 1
            customListItemWidget.connect(customListItemWidget, QtCore.SIGNAL('deleteItem(int)'),
                                         self.filterItemDeleteClick)

            self.filterListWidget.addItem(listItem)
            self.filterListWidget.setItemWidget(listItem, customListItemWidget)

        filterLayout.addWidget(self.filterListWidget)
        filterDialog.setLayout(filterLayout)
        # itemDoubleClicked signal
        self.filterListWidget.connect(self.filterListWidget, QtCore.SIGNAL('itemDoubleClicked(QListWidgetItem *)'),
                                      self.filterItemDoubleClick)
        filterDialog.exec_()

    def filterItemDoubleClick(self, listWidgetItem):
        # 获取到自定义的 widget, 先获取 QListWidget 在获取他的 itemWidget
        customWidget = self.filterListWidget.itemWidget(listWidgetItem)
        # print customWidget.getItemText()
        selectTxt = str(customWidget.getItemText()).strip()
        filterTxt = str(self.filterLineEdit.text()).strip()
        if not filterTxt:
            self.filterLineEdit.setText(_translate('', selectTxt, None))
        else:
            filterList = filterTxt.split('|')
            for onFilter in filterList:
                onFilter = onFilter.strip()
                if onFilter == selectTxt:
                    return
            filterList.append(selectTxt)
            filterStr = "|".join(filterList)
            self.filterLineEdit.setText(_translate('', filterStr, None))

    def filterItemDeleteClick(self, index):
        filterCount = self.filterListWidget.count()
        if index > filterCount:
            return
        customWidget = self.filterListWidget.itemWidget(self.filterListWidget.item(index))
        self.deleteFilterOnFile(customWidget.getItemText())
        self.filterListWidget.takeItem(index)
        # 修正index
        for x in range(0, filterCount):
            x = int(x)
            if x >= index:
                listItem = self.filterListWidget.item(x)
                customWidget = self.filterListWidget.itemWidget(listItem)
                if customWidget:
                    itemIndex = int(customWidget.getItemIndex()) - 1
                    customWidget.setItemIndex(itemIndex)

    def deleteFilterOnFile(self, text):
        if not text:
            return
        filterFile = QtCore.QFile(self.filterConfigFilePath)
        if not filterFile.open(QtCore.QFile.ReadWrite):
            filterFile.close()
            return
        oldTxt = QtCore.QTextStream(filterFile)
        oldTxt.setCodec('UTF-8')
        allFilter = str(oldTxt.readAll())
        allFilterList = allFilter.split('#@$')
        for oneFilter in allFilterList:
            if oneFilter == str(text):
                allFilterList.remove(oneFilter)

        filterFile.resize(0)
        filterStr = '#@$'.join(allFilterList)
        if not filterStr:
            return
        oldTxt << _translate('', filterStr, None)
        oldTxt.flush()
        filterFile.close()

    # 监听新到来的连接(新的终端被打开)
    def newLocalSocketConnection(self):
        # print 'newLocalSocketConnection'
        # 处理新启动的程序(终端)发过来的参数
        serverSocket = self.localServer.nextPendingConnection()
        if not serverSocket:
            return
        serverSocket.waitForReadyRead(1000)
        stream = QtCore.QTextStream(serverSocket)
        stream.setCodec('UTF-8')
        pathData = str(_translate('', stream.readAll(), None))
        serverSocket.close()
        # 由于客户端在发送的时候，就已经处理只发送(传递) 打开的文件路径参数，故此处不做校验处理
        # print SupportFiles.hasSupportFile(pathData)
        if pathData and SupportFiles.hasSupportFile(pathData):
            self.setLogTxt(pathData)
        # print pathData

    def showAutoAnalyticsCallFailDialog(self):
        cfwin = CallFailWindow(self.mainwindow)
        cfwin.show()

    def showSplitExcelDialog(self):
        spExcelWin = SplitExcelWindow(self.mainwindow)
        spExcelWin.show()

# Load filter item
class CustomFilterItemWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self)
        hItemBoxLayout = QtGui.QHBoxLayout()
        self.itemText = QtGui.QLabel()
        self.itemIconBtn = QtGui.QPushButton()
        self.itemIndex = 0
        hItemBoxLayout.addWidget(self.itemText)
        hItemBoxLayout.addWidget(self.itemIconBtn)

        self.itemIconBtn.connect(self.itemIconBtn, QtCore.SIGNAL('clicked()'), self.iconClick)

        self.setLayout(hItemBoxLayout)

    def setItemText(self, text):
        self.itemText.setText(text)

    def getItemText(self):
        return self.itemText.text()

    def setItemIndex(self, index):
        self.itemIndex = index

    def getItemIndex(self):
        return self.itemIndex

    def setItemIcon(self, imgPath):
        iconPixmap = QtGui.QPixmap(imgPath)
        self.itemIconBtn.setIcon(QtGui.QIcon(iconPixmap))
        # setFixedSize
        self.itemIconBtn.setIconSize(iconPixmap.rect().size())
        self.itemIconBtn.setFixedSize(iconPixmap.rect().size())

    def iconClick(self):
        # self.getItemIndex() is arguments
        self.emit(QtCore.SIGNAL('deleteItem(int)'), self.getItemIndex())

    def deleteItem(self, itemIndex):
        return


class LogMainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self)

        screen = QtGui.QDesktopWidget().screenGeometry()
        self.resize(screen.width() / 4 * 3, screen.height() / 4 * 3)
        self.setWindowTitle(Constants.ApplicationName)
        self.setAcceptDrops(True)

    def keyPressEvent(self, event):
        # 设置 "Ctrl+w" 快捷键，用于关闭 tab
        if event.key() == QtCore.Qt.Key_W and event.modifiers() == QtCore.Qt.ControlModifier:
            self.emit(QtCore.SIGNAL('closeCurrentTabSignal()'))

    def dragEnterEvent(self, event):
        # http://www.iana.org/assignments/media-types/media-types.xhtml
        if event.mimeData().hasUrls() and event.mimeData().hasFormat("text/uri-list"):
            for url in event.mimeData().urls():
                filePath = str(url.toLocalFile()).decode('utf-8')
                if SupportFiles.hasSupportFile(filePath):
                    event.acceptProposedAction()
                else:
                    print 'not accept this file!'
        else:
            print 'not accept this file too!'

    # 和 dragEnterEvent 结合使用，处理拖拽文件进窗口区域，进行打开。与右键和拖文件到桌面图标打开方式不同。
    # 本方式是在窗口打开的前提下，直接拖文件到窗口上，这种方式打开。
    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                filePath = str(url.toLocalFile()).decode('utf-8')
                # print filePath
                self.emit(QtCore.SIGNAL('dropOpenFileSignal(QString)'), filePath)
        return

    def closeCurrentTabSignal(self):
        return

    def dropOpenFileSignal(self, filePath):
        return


def main():
    app = QtGui.QApplication(sys.argv)
    QSettingsUtil.init()
    logMainWin = LogMainWindow()
    uiMainWidget = Ui_MainWidget()
    winOsArgv = WinCommandEnCoding.getOsArgv()
    # single QApplication solution
    # http://blog.csdn.net/softdzf/article/details/6704187
    serverName = 'LogAnalyticsServer'
    clientSocket = QLocalSocket()
    clientSocket.connectToServer(serverName)
    # 如果连接成功， 表明server 已经存在，当前已经有实例在运行, 将参数发送给服务端
    if clientSocket.waitForConnected(500):
        # print u'连接成功 arg = ', winOsArgv
        stream = QtCore.QTextStream(clientSocket)
        # for i in range(0, len(winOsArgv)):
        #     stream << winOsArgv[i]
        # 对于打开终端来说，所携带参数为第1位(打开文件的地址)，第0位为本执行程序地址
        if len(winOsArgv) > 1:
            stream << winOsArgv[1]
            stream.setCodec('UTF-8')
            stream.flush()
            clientSocket.waitForBytesWritten()
        # close client socket
        clientSocket.close()
        return app.quit()
    # 如果没有实例执行，创建服务器
    localServer = QLocalServer()
    # 一直监听端口
    localServer.listen(serverName)
    try:
        uiMainWidget.setupUi(logMainWin, localServer, winOsArgv)
        logMainWin.show()
        sys.exit(app.exec_())
    finally:
        localServer.close()


if __name__ == '__main__':
    # Windows 平台要加上这句，避免 RuntimeError
    # https://jingsam.github.io/2015/12/31/multiprocessing.html
    multiprocessing.freeze_support()
    main()
