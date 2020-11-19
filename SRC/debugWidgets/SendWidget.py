# coding=gbk
'''
Created on 2019年1月13日
@author: yujie
Edited on 2020年11月09日
@author: yujie
'''

# Form implementation generated from reading ui file 'SendWidget.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class SendWidget(QtWidgets.QWidget):

    def __init__(self,sendMessage,parent = None,num = 0):
        super(SendWidget,self).__init__(parent)
        self.number = num
        self.sendMessage = sendMessage#回调的发送信息的函数
        self.setupUi(parent)
        
    def setupUi(self,parent = None):
        parent.setObjectName("SendWidget")

        self.gridLayout = QtWidgets.QGridLayout(self)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        
        self.lineEditName = QtWidgets.QLineEdit(self)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEditName.sizePolicy().hasHeightForWidth())
        self.lineEditName.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("黑体")
        font.setPointSize(12)
        font.setBold(False)
        font.setWeight(50)
        
        self.lineEditName.setFont(font)
        self.lineEditName.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.lineEditName.setAutoFillBackground(True)
        self.lineEditName.setPlaceholderText("变量名"+str(self.number))
        self.lineEditName.setMaxLength(80)
        self.lineEditName.setObjectName("lineEditName")
        self.lineEditName.returnPressed.connect(self.setVariableName)
        
        self.gridLayout.addWidget(self.lineEditName, 0, 0, 1, 1)
        
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        
        self.lineEditValue = QtWidgets.QLineEdit(self)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEditValue.sizePolicy().hasHeightForWidth())
        self.lineEditValue.setSizePolicy(sizePolicy)
        self.lineEditValue.setBaseSize(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.lineEditValue.setFont(font)
        self.lineEditValue.setInputMethodHints(QtCore.Qt.ImhPreferNumbers)
        self.lineEditValue.setValidator(QtGui.QDoubleValidator(self))
        self.lineEditValue.setMaxLength(80)
        self.lineEditValue.setPlaceholderText("变量值")
        self.lineEditValue.setObjectName("lineEditValue")
        
        self.horizontalLayout_2.addWidget(self.lineEditValue)
        
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.verticalLayout.setObjectName("verticalLayout")
        
        self.pushButtonadd = QtWidgets.QPushButton(self)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButtonadd.sizePolicy().hasHeightForWidth())
        self.pushButtonadd.setSizePolicy(sizePolicy)
        self.pushButtonadd.setMaximumSize(QtCore.QSize(30, 30))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.pushButtonadd.setFont(font)
        self.pushButtonadd.setCheckable(False)
        self.pushButtonadd.setObjectName("pushButtonadd")
        
        self.verticalLayout.addWidget(self.pushButtonadd)
        
        self.pushButtonsub = QtWidgets.QPushButton(self)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButtonsub.sizePolicy().hasHeightForWidth())
        self.pushButtonsub.setSizePolicy(sizePolicy)
        self.pushButtonsub.setMaximumSize(QtCore.QSize(30, 30))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.pushButtonsub.setFont(font)
        self.pushButtonsub.setCheckable(False)
        self.pushButtonsub.setObjectName("pushButtonsub")
    
        self.verticalLayout.addWidget(self.pushButtonsub)
        self.horizontalLayout_2.addLayout(self.verticalLayout)
        
        self.pushButtonSend = QtWidgets.QPushButton(self)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButtonSend.sizePolicy().hasHeightForWidth())
        self.pushButtonSend.setSizePolicy(sizePolicy)
        self.pushButtonSend.setMaximumSize(QtCore.QSize(60, 100))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.pushButtonSend.setFont(font)
        self.pushButtonSend.setCheckable(False)
        self.pushButtonSend.setObjectName("pushButtonSend")
        
        self.horizontalLayout_2.addWidget(self.pushButtonSend)
        self.gridLayout.addLayout(self.horizontalLayout_2, 1, 0, 1, 1)

        self.retranslateUi()
        self.pushButtonadd.clicked.connect(self.ButtonAddClicked)
        self.pushButtonsub.clicked.connect(self.ButtonSubClicked)
        self.pushButtonSend.clicked.connect(self.ButtonSendClicked)

        QtCore.QMetaObject.connectSlotsByName(parent)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.pushButtonadd.setText(_translate("Form", "+"))
        self.pushButtonsub.setText(_translate("Form", "-"))
        self.pushButtonSend.setText(_translate("Form", "发送"))


    def ButtonAddClicked(self):
        #print('add'+str(self.number))
        tmp = self.lineEditValue.text()
        if tmp == "":
            self.lineEditValue.setText(str(1))
        else:
            index = tmp.find(".")
            if index == -1:
                self.lineEditValue.setText(str(int(tmp)+1))
            else:
                i = len(tmp) - index -1
                num = float('%.10f'%(float(tmp)+1/10**i))
                reg = '{:.'+str(i)+'f}'
                self.lineEditValue.setText(reg.format(num))
        
    def ButtonSubClicked(self):
        #print('sub'+str(self.number))
        tmp = self.lineEditValue.text()
        if tmp == "":
            self.lineEditValue.setText(str(1))
        else:
            index = tmp.find(".")
            if index == -1:
                self.lineEditValue.setText(str(int(tmp)-1))
            else:
                i = len(tmp) - index -1
                num = float('%.10f'%(float(tmp)-1/10**i))
                reg = '{:.'+str(i)+'f}'
                self.lineEditValue.setText(reg.format(num))
                
    def ButtonSendClicked(self):
        print('send'+str(self.number))
        print("变量名为："+self.lineEditName.text())
        print("输入值为："+self.lineEditValue.text())
        self.sendMessage(self.number,self.lineEditName.text(),self.lineEditValue.text())

    def setVariableName(self):
        print('设置变量名为：'+self.lineEditName.text())
        self.lineEditName.setText(str(self.number)+':'+self.lineEditName.text())