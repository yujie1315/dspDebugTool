# coding=gbk
'''
Created on 2020年11月08日

@author: yujie
'''
from appDir import app_path
import socket
import struct
import time
#from datetime import datetime
from PyQt5.QtCore import QThread,pyqtSignal

class MessageData():
    def __init__(self):
        self.finishedFlag = True
        self.start_bytes = b'\x3a'#起始标志符
        self.datalength = 0 #数据长度,单位是byte
        self.destinationAddress = 0 #数据目的地址
        self.sourceAddress = 254 #数据源地址，默认上位机软件的地址
        self.functionCode = 0  #功能码
        self.data = []  #数据内容。

    def setSourceAddress(self,Addr):
        self.sourceAddress = Addr

    def setDestinationAddress(self,Addr):
        #print('设置目的地址为：'+str(Addr))
        self.destinationAddress = Addr
    
    def setFunctionCode(self,code):
        if self.finishedFlag:
            #print('设置功能码为：'+str(code))
            self.functionCode = code
            self.finishedFlag = False
            return True
        else:
            return False
    
    #设置数据格式为[寄存器起始地址 寄存器值 寄存器值 ......]
    def sendData(self,data=[1,1]):
        for i in range(len(data)):
            self.data.append(data[i])
        if self.functionCode == 6:
            self.datalength = 4*(len(data)-1)+6
        elif self.functionCode == 3:
            self.datalength = 7

#socket发送线程
class TransmitMessageThread(QThread,MessageData):
    
    statusSignal = pyqtSignal(str)#传递错误信号
    def __init__(self,txSocket,parent=None):
        super(TransmitMessageThread,self).__init__(parent)
        self.txSocket = txSocket
        self.runFlag = True

    def run(self):
        try:
            print('开始发送线程')
            timeLast = time.time()
            while self.runFlag:
                time.sleep(0.01)
                
                if (time.time() - timeLast)>0.5:#每间隔500ms发送一次读指令
                    #print(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]+'发送间隔计时')
                    timeLast = time.time()
                    if self.setFunctionCode(3):
                        self.sendData([12,0])
                
                #判断是否有需要发送的数据M
                if not self.finishedFlag:
                    sendBytes = self.constractDataBytes()
                    if not sendBytes==None:
                        #print('传递的字节流为:')
                        #print(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]+'发送请求')
                        self.txSocket.send(sendBytes)
                        #print(sendBytes.hex())
                        self.data = []
                        #print('发送成功')
                        self.statusSignal.emit('发送成功')
                    self.finishedFlag = True
            pass
        except socket.error as e:
            print(e)
            #发送错误信息到图形界面线程
            self.statusSignal.emit('发送线程中发生错误\n'+str(e))
            pass
        finally:
            self.txSocket.close() 
            pass
    
    #终止线程运行
    def terminateThread(self):
        self.runFlag = False
    
    #构造发送的字节流
    def constractDataBytes(self):
        socketMsgHeader = self.start_bytes + \
                struct.pack('>1B',self.datalength) + \
                struct.pack('>1B',self.destinationAddress) + \
                struct.pack('>1B',self.sourceAddress) + \
                struct.pack('>1B',self.functionCode)
        #print('数据长度'+str(len(self.data)))
        if self.functionCode == 3:
            socketMsgData = struct.pack('>2B',self.data[0],self.data[1])
            return socketMsgHeader + socketMsgData
        elif self.functionCode == 6:
            socketMsgData = struct.pack('>1B',self.data[0])
            for _ in self.data[1:]:
                socketMsgData = socketMsgData + struct.pack('>1f',_)
            return socketMsgHeader + socketMsgData
        return None

#socket接收线程
class ReceiveMessageThread(QThread,MessageData):
    
    statusSignal = pyqtSignal(str)#传递线程状态
    resultSignal = pyqtSignal()#传递收到数据的消息
    def __init__(self,rxSocket,parent=None):
        super(ReceiveMessageThread,self).__init__(parent)
        self.ReceiveMessageSocket = rxSocket
        self.runFlag = True
        
    def terminateThread(self):
        self.runFlag = False

    def readData(self):
        data = []
        try:
            data.append(self.data[0])
            #print('解析功能码4')
            for i in range(1,len(self.data),4):
                #print(i)
                data.append(struct.unpack('>1f',self.data[i:4+i])[0])
            pass
        except IndexError as e:
            print('解析功能码4错误！！！')
            print(e)
            data = []
            pass
        finally:
            return data
    
    def run(self):
        try:
            print('开始接收线程')
            while self.runFlag:
                if self.finishedFlag:
                    self.datalength = 0
                    recvBytesHeader = self.ReceiveMessageSocket.recv(2)
                    if recvBytesHeader[0] == struct.unpack(">1B",self.start_bytes)[0]:
                        self.datalength = recvBytesHeader[1]
                        #print('数据长度为:{}'.format(self.datalength))
                        recvBytesData = self.ReceiveMessageSocket.recv(self.datalength-2)
                        self.setDestinationAddress(recvBytesData[0])
                        self.setSourceAddress(recvBytesData[1])
                        if self.setFunctionCode(recvBytesData[2]):
                            self.data = recvBytesData[3:]
                        self.statusSignal.emit('接收到数据帧')
                        self.resultSignal.emit()
                        pass
        except socket.error as e:
            print(e)
            self.statusSignal.emit('接收线程中发生错误\n'+str(e))
            pass

if __name__ == '__main__':
    print(app_path())
    ipAddress = '10.10.100.254'
    port = 8899
    tcpSocketClient = socket.socket()
    tcpSocketClient.connect((ipAddress,port))
    
    txThread = TransmitMessageThread(tcpSocketClient)
    rxThread = ReceiveMessageThread(tcpSocketClient)
    
    #txThread.start()
    rxThread.start()
    
    for i in range(100):
        if txThread.setFunctionCode(6):
            txThread.sendData([5,1.1,2.5,30.1+i,14000.5])
        time.sleep(1)
    tcpSocketClient.close()
    rxThread.terminateThread()
    txThread.terminateThread()
    print("客户端结束运行")
    pass