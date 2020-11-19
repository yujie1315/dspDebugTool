# coding=gbk
'''
Created on 2020��11��08��

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
        self.start_bytes = b'\x3a'#��ʼ��־��
        self.datalength = 0 #���ݳ���,��λ��byte
        self.destinationAddress = 0 #����Ŀ�ĵ�ַ
        self.sourceAddress = 254 #����Դ��ַ��Ĭ����λ������ĵ�ַ
        self.functionCode = 0  #������
        self.data = []  #�������ݡ�

    def setSourceAddress(self,Addr):
        self.sourceAddress = Addr

    def setDestinationAddress(self,Addr):
        #print('����Ŀ�ĵ�ַΪ��'+str(Addr))
        self.destinationAddress = Addr
    
    def setFunctionCode(self,code):
        if self.finishedFlag:
            #print('���ù�����Ϊ��'+str(code))
            self.functionCode = code
            self.finishedFlag = False
            return True
        else:
            return False
    
    #�������ݸ�ʽΪ[�Ĵ�����ʼ��ַ �Ĵ���ֵ �Ĵ���ֵ ......]
    def sendData(self,data=[1,1]):
        for i in range(len(data)):
            self.data.append(data[i])
        if self.functionCode == 6:
            self.datalength = 4*(len(data)-1)+6
        elif self.functionCode == 3:
            self.datalength = 7

#socket�����߳�
class TransmitMessageThread(QThread,MessageData):
    
    statusSignal = pyqtSignal(str)#���ݴ����ź�
    def __init__(self,txSocket,parent=None):
        super(TransmitMessageThread,self).__init__(parent)
        self.txSocket = txSocket
        self.runFlag = True

    def run(self):
        try:
            print('��ʼ�����߳�')
            timeLast = time.time()
            while self.runFlag:
                time.sleep(0.01)
                
                if (time.time() - timeLast)>0.5:#ÿ���500ms����һ�ζ�ָ��
                    #print(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]+'���ͼ����ʱ')
                    timeLast = time.time()
                    if self.setFunctionCode(3):
                        self.sendData([12,0])
                
                #�ж��Ƿ�����Ҫ���͵�����M
                if not self.finishedFlag:
                    sendBytes = self.constractDataBytes()
                    if not sendBytes==None:
                        #print('���ݵ��ֽ���Ϊ:')
                        #print(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]+'��������')
                        self.txSocket.send(sendBytes)
                        #print(sendBytes.hex())
                        self.data = []
                        #print('���ͳɹ�')
                        self.statusSignal.emit('���ͳɹ�')
                    self.finishedFlag = True
            pass
        except socket.error as e:
            print(e)
            #���ʹ�����Ϣ��ͼ�ν����߳�
            self.statusSignal.emit('�����߳��з�������\n'+str(e))
            pass
        finally:
            self.txSocket.close() 
            pass
    
    #��ֹ�߳�����
    def terminateThread(self):
        self.runFlag = False
    
    #���췢�͵��ֽ���
    def constractDataBytes(self):
        socketMsgHeader = self.start_bytes + \
                struct.pack('>1B',self.datalength) + \
                struct.pack('>1B',self.destinationAddress) + \
                struct.pack('>1B',self.sourceAddress) + \
                struct.pack('>1B',self.functionCode)
        #print('���ݳ���'+str(len(self.data)))
        if self.functionCode == 3:
            socketMsgData = struct.pack('>2B',self.data[0],self.data[1])
            return socketMsgHeader + socketMsgData
        elif self.functionCode == 6:
            socketMsgData = struct.pack('>1B',self.data[0])
            for _ in self.data[1:]:
                socketMsgData = socketMsgData + struct.pack('>1f',_)
            return socketMsgHeader + socketMsgData
        return None

#socket�����߳�
class ReceiveMessageThread(QThread,MessageData):
    
    statusSignal = pyqtSignal(str)#�����߳�״̬
    resultSignal = pyqtSignal()#�����յ����ݵ���Ϣ
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
            #print('����������4')
            for i in range(1,len(self.data),4):
                #print(i)
                data.append(struct.unpack('>1f',self.data[i:4+i])[0])
            pass
        except IndexError as e:
            print('����������4���󣡣���')
            print(e)
            data = []
            pass
        finally:
            return data
    
    def run(self):
        try:
            print('��ʼ�����߳�')
            while self.runFlag:
                if self.finishedFlag:
                    self.datalength = 0
                    recvBytesHeader = self.ReceiveMessageSocket.recv(2)
                    if recvBytesHeader[0] == struct.unpack(">1B",self.start_bytes)[0]:
                        self.datalength = recvBytesHeader[1]
                        #print('���ݳ���Ϊ:{}'.format(self.datalength))
                        recvBytesData = self.ReceiveMessageSocket.recv(self.datalength-2)
                        self.setDestinationAddress(recvBytesData[0])
                        self.setSourceAddress(recvBytesData[1])
                        if self.setFunctionCode(recvBytesData[2]):
                            self.data = recvBytesData[3:]
                        self.statusSignal.emit('���յ�����֡')
                        self.resultSignal.emit()
                        pass
        except socket.error as e:
            print(e)
            self.statusSignal.emit('�����߳��з�������\n'+str(e))
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
    print("�ͻ��˽�������")
    pass