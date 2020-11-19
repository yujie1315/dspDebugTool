# coding=gbk
'''
Created on 2019��1��10��
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
        self.socketStatus = 0#����socket���ӵ�״̬ 0 δ���ӣ���ռ��Դ 1 ������ ռ����Դ 2 ���ӳɹ�
        self.setupUi()

    #���߽�������
    def setupUi(self):
        self.setWindowTitle("DspDebugTool")
        self.resize(1200,675)
        #�˵�������
        self.file = self.menuBar().addMenu("�ļ�")# ��menuBar������ļ��˵�
        self.openVariable = QAction("�� (Ctrl+O)", self)
        self.saveVariable = QAction("���� (Ctrl+S)", self)
        self.exitTool = QAction("�˳�", self)
        
        #Ϊһ��Action���ÿ�ݼ�
        self.openVariable.setShortcut('Ctrl+O')
        self.saveVariable.setShortcut('Ctrl+S')
        
        #�󶨶����ؼ�
        self.file.addAction(self.openVariable)
        self.file.addAction(self.saveVariable)
        self.file.addAction(self.exitTool)

        # Ϊ�ļ�-->����󶨲ۺ���
        self.openVariable.triggered.connect(self.openProcess)
        self.saveVariable.triggered.connect(self.saveProcess)
        self.exitTool.triggered.connect(self.exitDspTool)
        
        #��� ���� �Ĳ˵���
        self.about = self.menuBar().addMenu("����")
        self.toolInfo = QAction("�����Ϣ", self)
        self.authorInfo = QAction("������Ϣ", self)
        self.about.addAction(self.toolInfo)
        self.about.addAction(self.authorInfo)
        self.toolInfo.triggered.connect(self.showTool)
        self.authorInfo.triggered.connect(self.showAuthor)

        #ʵ�����ؼ�ʱ����ָ�����ؼ�QWidget(self),ָ����ǰ��Ϊ���ؼ���Ҳ���Բ���ָ�����ؼ�
        self.toolWidget = QWidget()
        self.setCentralWidget(self.toolWidget) #�����Ŀؼ�
        self.widgetLayout = QVBoxLayout()#������ֱ����
        self.widgetLayout.setGeometry(QRect(0,0,1200,675))
        self.widgetLayout.setObjectName("widgetLayout")
        self.toolWidget.setLayout(self.widgetLayout)#�������Ĳ���Ϊ��ֱ����
        
        #����һϵ�пؼ�����������Ϣ
        self.portMessageSetLayout = QHBoxLayout()#���ˮƽ�ֲ��ĸ��ӣ����ڷ��ö˿���Ϣ����
        self.ipBoxHint = QLabel('��������ַ:')
        self.ipBox = QLineEdit('10.10.100.254')
        self.PortHint = QLabel('�������˿�:')
        self.Port = QLineEdit('8899')
        self.Port.setValidator(QIntValidator(0, 65535))
        self.desAddressHint = QLabel('Ŀ�ĵ�ַ:')
        self.desAddress = QLineEdit('100')
        self.desAddress.setValidator(QIntValidator(0,254))
        self.connectBox = QPushButton('���ӷ�����')

        #���ؼ���ӵ�������
        self.portMessageSetLayout.addWidget(self.ipBoxHint)
        self.portMessageSetLayout.addWidget(self.ipBox)
        self.portMessageSetLayout.addWidget(self.PortHint)
        self.portMessageSetLayout.addWidget(self.Port)
        self.portMessageSetLayout.addWidget(self.desAddressHint)
        self.portMessageSetLayout.addWidget(self.desAddress)
        self.portMessageSetLayout.addWidget(self.connectBox)
        self.widgetLayout.addLayout(self.portMessageSetLayout)
        #�󶨿ؼ�����
        self.connectBox.clicked.connect(self.connectServer)
        self.desAddress.returnPressed.connect(self.setDesAddress)
        #�������ͱ�����
        self.gridLayout_1 = QGridLayout()#�������񲼾�
        self.gridLayout_1.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_1.setObjectName("gridLayout_1")
        self.sendList= []
        
        for i in range(15):
            self.sendList.append(SendWidget(self.sendMessageBySocket,self,i))
            self.gridLayout_1.addWidget(self.sendList[i],i//5,i%5)
        self.widgetLayout.addLayout(self.gridLayout_1)
        #�������ձ�����ʾ��
        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.RecieverList= []
        for i in range(12):
            self.RecieverList.append(RecieverWidget(self,i))
            self.gridLayout_2.addWidget(self.RecieverList[i],i//6,i%6)
        self.widgetLayout.addLayout(self.gridLayout_2)
        
        #����״̬��
        self.socketStatusBar = QLabel('socket�ȴ�����...')
        self.txStatus = QLabel('�ȴ����������߳�...')
        self.rxStatus = QLabel('�ȴ����������߳�...')
        self.statusBar().addPermanentWidget(self.socketStatusBar,stretch=2)
        self.statusBar().addPermanentWidget(self.txStatus,stretch=2)
        self.statusBar().addPermanentWidget(self.rxStatus,stretch=2)
        
    def sendMessageBySocket(self,widgetNum,VariableName,VariableValue):
        print('�����źŵĲ���ǣ�'+str(widgetNum))
        print('����'+VariableName+'��ֵΪ��'+VariableValue)
        self.txStatusShowMessage('���'+str(widgetNum)+'���͵�ֵΪ��'+VariableValue)
        
        if not VariableValue == '':#�ж����ݷǿ�����з���
            if self.socketStatus == 2:#�ж��Ƿ�������soket
                #ͨ��socket�������ݣ��������ù�����Ϊ6
                if self.txThread.setFunctionCode(6):
                    #�ɹ����ù��������͵����ݣ������Ĵ����ĵ�ַ�ͼĴ���
                    self.txThread.sendData([widgetNum,float(VariableValue)])
            else:
                self.showMessageBox('δ���ӵ�������\n�ȵ�����ӷ�����')
                pass

    #������λ��ͨ�ŵ�ַ
    def setDesAddress(self):
        self.txThread.setDestinationAddress(int(self.desAddress.text()))
        self.rxThread.setDestinationAddress(int(self.desAddress.text()))
    
    #�½��߳�ִ�к�ʱ���񣬱��������������
    def connectServer(self):
        #��socket����������Ҫ��ȫ�رղ�����������
        if self.socketStatus == 0:
            print('��ʼ����')
            #�½��߳�ִ����������
            self.tcpClientSocket = socket.socket()
            self.conThread = connectThread(self.ipBox.text(),int(self.Port.text()),self.tcpClientSocket)
            self.conThread.connectSignal.connect(self.socketLinkProcess)
            self.conThread.start()
            self.socketStatusBar.setText('socket������...')
            self.socketStatus = 1
        
        elif self.socketStatus == 2:
            print('�Ѿ�����socket���ӣ��ȹر������ӵ�������')
            try:
                #�ͷŵ��Ѿ�����ռ�õ���Դ
                self.tcpClientSocket.shutdown(2)
                self.tcpClientSocket.close()
                self.txThread.terminateThread()
                self.rxThread.terminateThread()
                #��������
                self.tcpClientSocket = socket.socket()
                self.conThread = connectThread(self.ipBox.text(),int(self.Port.text()),self.tcpClientSocket)
                self.conThread.connectSignal.connect(self.socketLinkProcess)
                self.conThread.start()
                self.socketStatus = 1
                self.socketStatusBar.setText('socket������...')
                pass
            except socket.error as e:
                print(e)
                self.showMessageBox('���ӷ�����ʱ��������\n'+str(e))
                pass
            pass
        
    
    def socketLinkProcess(self,msg):
        if msg =='���ӳɹ�����':
            #�����߳�ִ�з�������
            self.txThread = TransmitMessageThread(self.tcpClientSocket)#�½�һ���߳����ڷ�������
            self.txThread.statusSignal.connect(self.txStatusShowMessage)
            self.txThread.setDestinationAddress(int(self.desAddress.text()))
            self.txThread.start()#
            self.txStatusShowMessage('�����߳�����')
            
            #�����߳�ִ�н�������
            self.rxThread = ReceiveMessageThread(self.tcpClientSocket)#�½�һ���߳����ڽ�������
            self.rxThread.statusSignal.connect(self.rxStatusShowMessage)
            self.rxThread.resultSignal.connect(self.receiveData)
            self.rxThread.setDestinationAddress(int(self.desAddress.text()))
            self.rxThread.start()#
            self.rxStatusShowMessage('�����߳�����')
            self.showMessageBox('���ӳɹ���\n�Ѿ�����ͨ���߳�')
            #socketͨ���߳������ɹ�
            self.socketStatus = 2
            self.socketStatusBar.setText('socket���ӳɹ�')
        else:
            self.socketStatus = 0 #���Ӵ���ʱ�Ѿ��ͷŵ�socket��Դ
            self.showMessageBox(msg)
            pass


    #��DSP���յ����ݡ���ͨ��������ʾ����
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
                self.txStatusShowMessage('����дָ�����յ�������')
                print(self.rxThread.data)
                pass
        self.rxThread.finishedFlag = True
    
    #ͨ��messageBox��������
    def showMessageBox(self,msg):    
        QMessageBox(QMessageBox.Warning,'����',msg).exec_()
    
    #չʾ�����̵߳�״̬
    def txStatusShowMessage(self,msg):
        self.txStatus.setText('�����߳�״̬:'+msg)
    
    #չʾ�����̵߳�״̬
    def rxStatusShowMessage(self,msg):
        self.rxStatus.setText('�����߳�״̬:'+msg)
    
    #��������ϵ�����
    def saveProcess(self):
        with open('info.txt','w',encoding='utf-8') as fileInfo:
            for _ in self.sendList:
                data = [_.lineEditName.text(),_.lineEditValue.text()]
                fileInfo.write(str(data)+'\n')
            fileInfo.flush()
        fileInfo.close()
        self.showMessageBox('����ɹ�')

    #�������ϱ�������ݣ����ؽ���
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
            self.showMessageBox('�򿪳ɹ�')
            pass
        except FileNotFoundError as e:
            print(e)
            self.showMessageBox('�ļ�������')
            pass    
    
    #չʾ�����Ϣ
    def showTool(self):
        msg = 'DSPͨ�Ź��� V0.1\nͼ�ο� PyQt5-5.15'
        QMessageBox(QMessageBox.Warning,'��Ϣ',msg).exec_()
    
    #չʾ���������Ϣ
    def showAuthor(self):
        msg = 'Created By yujie1315\n2020��11��11��'
        QMessageBox(QMessageBox.Warning,'��Ϣ',msg).exec_()

    #�˳����
    def exitDspTool(self):
        print('�˳����')
        self.rxThread.terminateThread()
        self.txThread.terminateThread()
        self.close()

 
#�½��߳�ִ��socket���ӵĺ�ʱ���񣬱�����濨��
class connectThread(QThread):
    #pyqt�̼߳�ͨ�ŷ�ʽ����Ҫ���嵽�����ط����ᱨ��
    connectSignal = pyqtSignal(str)
    
    def __init__(self,ipAddress,port,connectSocket,parent=None):
        super(connectThread,self).__init__(parent)
        self.ipAddress = ipAddress
        self.port = port
        self.connectSocket = connectSocket

    def run(self):
        try:
            self.connectSocket.connect((self.ipAddress,self.port))
            self.connectSignal.emit('���ӳɹ�����')
            pass
        except socket.error as msg:
            print(msg)
            self.connectSocket.close()#����ʧ����ر�socket���ͷ���Դ
            self.connectSignal.emit('socket����ʱ��������!\n'+str(msg))
            pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = toolWindow()
    mainWindow.show()
    sys.exit(app.exec_())
    pass