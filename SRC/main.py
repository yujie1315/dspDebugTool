# coding=gbk
'''
Created on 2019年1月10日
@author: yujie
'''
import sys,os
if hasattr(sys, 'frozen'):
    os.environ['PATH'] = sys._MEIPASS + ";" + os.environ['PATH']
from PyQt5.QtWidgets import QApplication,QMainWindow,QWidget,QAction,\
    QGridLayout,QHBoxLayout,QVBoxLayout,\
    QLabel,QLineEdit,QPushButton,QMessageBox
from debugWidgets.RecieverWidget import RecieverWidget
from debugWidgets.SendWidget import SendWidget
from communication import TransmitMessageThread,ReceiveMessageThread
import socket
from PyQt5.QtCore import QRect,QThread,pyqtSignal
from PyQt5.QtGui import QIntValidator

class toolWindow(QMainWindow):

    def __init__(self,parent = None):
        super(toolWindow,self).__init__(parent)
        self.socketStatus = 0#定义socket连接的状态 0 未连接，不占资源 1 连接中 占用资源 2 连接成功
        self.setupUi()

    #工具界面设置
    def setupUi(self):
        self.setWindowTitle("DspDebugTool")
        self.resize(1200,675)
        #菜单栏设置
        self.file = self.menuBar().addMenu("文件")# 在menuBar上添加文件菜单
        self.openVariable = QAction("打开 (Ctrl+O)", self)
        self.saveVariable = QAction("保存 (Ctrl+S)", self)
        self.exitTool = QAction("退出", self)
        
        #为一个Action设置快捷键
        self.openVariable.setShortcut('Ctrl+O')
        self.saveVariable.setShortcut('Ctrl+S')
        
        #绑定动作控件
        self.file.addAction(self.openVariable)
        self.file.addAction(self.saveVariable)
        self.file.addAction(self.exitTool)

        # 为文件-->保存绑定槽函数
        self.openVariable.triggered.connect(self.openProcess)
        self.saveVariable.triggered.connect(self.saveProcess)
        self.exitTool.triggered.connect(self.exitDspTool)
        
        #添加 关于 的菜单栏
        self.about = self.menuBar().addMenu("关于")
        self.toolInfo = QAction("软件信息", self)
        self.authorInfo = QAction("作者信息", self)
        self.about.addAction(self.toolInfo)
        self.about.addAction(self.authorInfo)
        self.toolInfo.triggered.connect(self.showTool)
        self.authorInfo.triggered.connect(self.showAuthor)

        #实例化控件时可以指定父控件QWidget(self),指定当前类为父控件，也可以不用指定父控件
        self.toolWidget = QWidget()
        self.setCentralWidget(self.toolWidget) #绑定中心控件
        self.widgetLayout = QVBoxLayout()#创建垂直布局
        self.widgetLayout.setGeometry(QRect(0,0,1200,675))
        self.widgetLayout.setObjectName("widgetLayout")
        self.toolWidget.setLayout(self.widgetLayout)#设置中心布局为垂直布局
        
        #创建一系列控件用于设置信息
        self.portMessageSetLayout = QHBoxLayout()#添加水平分布的格子，用于放置端口信息设置
        self.ipBoxHint = QLabel('服务器地址:')
        self.ipBox = QLineEdit('10.10.100.254')
        self.PortHint = QLabel('服务器端口:')
        self.Port = QLineEdit('8899')
        self.Port.setValidator(QIntValidator(0, 65535))
        self.desAddressHint = QLabel('目的地址:')
        self.desAddress = QLineEdit('100')
        self.desAddress.setValidator(QIntValidator(0,254))
        self.connectBox = QPushButton('连接服务器')

        #将控件添加到布局中
        self.portMessageSetLayout.addWidget(self.ipBoxHint)
        self.portMessageSetLayout.addWidget(self.ipBox)
        self.portMessageSetLayout.addWidget(self.PortHint)
        self.portMessageSetLayout.addWidget(self.Port)
        self.portMessageSetLayout.addWidget(self.desAddressHint)
        self.portMessageSetLayout.addWidget(self.desAddress)
        self.portMessageSetLayout.addWidget(self.connectBox)
        self.widgetLayout.addLayout(self.portMessageSetLayout)
        #绑定控件操作
        self.connectBox.clicked.connect(self.connectServer)
        self.desAddress.returnPressed.connect(self.setDesAddress)
        #创建发送变量区
        self.gridLayout_1 = QGridLayout()#创建网格布局
        self.gridLayout_1.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_1.setObjectName("gridLayout_1")
        self.sendList= []
        
        for i in range(15):
            self.sendList.append(SendWidget(self.sendMessageBySocket,self,i))
            self.gridLayout_1.addWidget(self.sendList[i],i//5,i%5)
        self.widgetLayout.addLayout(self.gridLayout_1)
        #创建接收变量显示区
        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.RecieverList= []
        for i in range(12):
            self.RecieverList.append(RecieverWidget(self,i))
            self.gridLayout_2.addWidget(self.RecieverList[i],i//6,i%6)
        self.widgetLayout.addLayout(self.gridLayout_2)
        
        #设置状态栏
        self.socketStatusBar = QLabel('socket等待连接...')
        self.txStatus = QLabel('等待启动发送线程...')
        self.rxStatus = QLabel('等待启动接收线程...')
        self.statusBar().addPermanentWidget(self.socketStatusBar,stretch=2)
        self.statusBar().addPermanentWidget(self.txStatus,stretch=2)
        self.statusBar().addPermanentWidget(self.rxStatus,stretch=2)
        
    def sendMessageBySocket(self,widgetNum,VariableName,VariableValue):
        print('发送信号的插件是：'+str(widgetNum))
        print('发送'+VariableName+'的值为：'+VariableValue)
        self.txStatusShowMessage('插件'+str(widgetNum)+'发送的值为：'+VariableValue)
        
        if not VariableValue == '':#判断数据非空则进行发送
            if self.socketStatus == 2:#判断是否连接上soket
                #通过socket发送数据，首先设置功能码为6
                if self.txThread.setFunctionCode(6):
                    #成功设置功能码则发送的数据，包括寄存器的地址和寄存器
                    self.txThread.sendData([widgetNum,float(VariableValue)])
            else:
                self.showMessageBox('未连接到服务器\n先点击连接服务器')
                pass

    #设置下位机通信地址
    def setDesAddress(self):
        self.txThread.setDestinationAddress(int(self.desAddress.text()))
        self.rxThread.setDestinationAddress(int(self.desAddress.text()))
    
    #新建线程执行耗时任务，避免阻塞界面进程
    def connectServer(self):
        #若socket已连接则需要完全关闭才能重新连接
        if self.socketStatus == 0:
            print('开始连接')
            #新建线程执行链接任务
            self.tcpClientSocket = socket.socket()
            self.conThread = connectThread(self.ipBox.text(),int(self.Port.text()),self.tcpClientSocket)
            self.conThread.connectSignal.connect(self.socketLinkProcess)
            self.conThread.start()
            self.socketStatusBar.setText('socket连接中...')
            self.socketStatus = 1
        
        elif self.socketStatus == 2:
            print('已经打开了socket连接，先关闭再连接到新链接')
            try:
                #释放掉已经连接占用的资源
                self.tcpClientSocket.shutdown(2)
                self.tcpClientSocket.close()
                self.txThread.terminateThread()
                self.rxThread.terminateThread()
                #重新连接
                self.tcpClientSocket = socket.socket()
                self.conThread = connectThread(self.ipBox.text(),int(self.Port.text()),self.tcpClientSocket)
                self.conThread.connectSignal.connect(self.socketLinkProcess)
                self.conThread.start()
                self.socketStatus = 1
                self.socketStatusBar.setText('socket连接中...')
                pass
            except socket.error as e:
                print(e)
                self.showMessageBox('连接服务器时发生错误！\n'+str(e))
                pass
            pass
        
    
    def socketLinkProcess(self,msg):
        if msg =='链接成功！！':
            #启动线程执行发送任务
            self.txThread = TransmitMessageThread(self.tcpClientSocket)#新建一个线程用于发送数据
            self.txThread.statusSignal.connect(self.txStatusShowMessage)
            self.txThread.setDestinationAddress(int(self.desAddress.text()))
            self.txThread.start()#
            self.txStatusShowMessage('发送线程启动')
            
            #启动线程执行接收任务
            self.rxThread = ReceiveMessageThread(self.tcpClientSocket)#新建一个线程用于接收数据
            self.rxThread.statusSignal.connect(self.rxStatusShowMessage)
            self.rxThread.resultSignal.connect(self.receiveData)
            self.rxThread.setDestinationAddress(int(self.desAddress.text()))
            self.rxThread.start()#
            self.rxStatusShowMessage('接收线程启动')
            self.showMessageBox('连接成功！\n已经启动通信线程')
            #socket通信线程启动成功
            self.socketStatus = 2
            self.socketStatusBar.setText('socket连接成功')
        else:
            self.socketStatus = 0 #连接错误时已经释放掉socket资源
            self.showMessageBox(msg)
            pass


    #从DSP接收到数据。并通过界面显示数据
    def receiveData(self):

        if self.rxThread.destinationAddress == 254:
            if self.rxThread.functionCode == 4:
                data = self.rxThread.readData()
                print(data)
                if not data ==[]:
                    for i in range(len(data)-1):
                        self.RecieverList[data[0]+i].label.setText(str(data[i+1]))
                pass
            if self.rxThread.functionCode == 7:
                self.txStatusShowMessage('发送写指令已收到！！！')
                print(self.rxThread.data)
                pass
        self.rxThread.finishedFlag = True
    
    #通过messageBox弹窗警告
    def showMessageBox(self,msg):    
        QMessageBox(QMessageBox.Warning,'警告',msg).exec_()
    
    #展示发送线程的状态
    def txStatusShowMessage(self,msg):
        self.txStatus.setText('发送线程状态:'+msg)
    
    #展示接收线程的状态
    def rxStatusShowMessage(self,msg):
        self.rxStatus.setText('接收线程状态:'+msg)
    
    #保存界面上的内容
    def saveProcess(self):
        with open('info.txt','w',encoding='utf-8') as fileInfo:
            for _ in self.sendList:
                data = [_.lineEditName.text(),_.lineEditValue.text()]
                fileInfo.write(str(data)+'\n')
            fileInfo.flush()
        fileInfo.close()
        self.showMessageBox('保存成功')

    #将界面上保存的内容，导回界面
    def openProcess(self):
        try:
            with open('info.txt','r',encoding='utf-8') as fileInfo:
                for i in range(len(self.sendList)) :
                    info = fileInfo.readline().split(', ')
                    if not info[0] == '[\'\'' :
                        self.sendList[i].lineEditName.setText(info[0][2:-1])
                    if not info[1] == '\'\']\n':
                        self.sendList[i].lineEditValue.setText(info[1][1:-3])
                fileInfo.close
            self.showMessageBox('打开成功')
            pass
        except FileNotFoundError as e:
            print(e)
            self.showMessageBox('文件不存在')
            pass    
    
    #展示软件信息
    def showTool(self):
        msg = 'DSP通信工具 V0.1\n图形库 PyQt5-5.15'
        QMessageBox(QMessageBox.Warning,'信息',msg).exec_()
    
    #展示软件作者信息
    def showAuthor(self):
        msg = 'Created By yujie1315\n2020年11月11日'
        QMessageBox(QMessageBox.Warning,'信息',msg).exec_()

    #退出软件
    def exitDspTool(self):
        print('退出软件')
        self.rxThread.terminateThread()
        self.txThread.terminateThread()
        self.close()

 
#新建线程执行socket连接的耗时任务，避免界面卡死
class connectThread(QThread):
    #pyqt线程间通信方式，不要定义到其他地方，会报错
    connectSignal = pyqtSignal(str)
    
    def __init__(self,ipAddress,port,connectSocket,parent=None):
        super(connectThread,self).__init__(parent)
        self.ipAddress = ipAddress
        self.port = port
        self.connectSocket = connectSocket

    def run(self):
        try:
            self.connectSocket.connect((self.ipAddress,self.port))
            self.connectSignal.emit('链接成功！！')
            pass
        except socket.error as msg:
            print(msg)
            self.connectSocket.close()#连接失败则关闭socket，释放资源
            self.connectSignal.emit('socket连接时发生错误!\n'+str(msg))
            pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = toolWindow()
    mainWindow.show()
    sys.exit(app.exec_())
    pass