#coding=gbk
'''
Created on 2019年1月17日

@author: yujie
'''
from PyQt5 import QtWidgets,QtGui

class RecieverWidget(QtWidgets.QWidget):
    number = 0
    def __init__(self,parent = None,num = 0):
        super(RecieverWidget,self).__init__(parent)
        self.number =num
        self.label = QtWidgets.QLabel(str(self.number))
        
        self.lineEdit = QtWidgets.QLineEdit(self)
        self.lineEdit.setMaximumWidth(100)
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(12)
        font.setBold(True)
        self.lineEdit.setFont(font)
        
        self.lineEdit.setPlaceholderText("变量"+str(num))
        self.label.setBuddy(self.lineEdit) 
        self.layout = QtWidgets.QHBoxLayout() 
        
        self.layout.addWidget(self.lineEdit)
        self.layout.addWidget(self.label)
         
        self.setLayout(self.layout)
