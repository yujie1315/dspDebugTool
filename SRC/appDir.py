# coding=gbk
'''
Created on 2019��2��27��

@author: yujie
'''
import sys,os
 
def app_path():
    """Returns the base application path."""
    if hasattr(sys, 'frozen'):
        # Handles PyInstaller
        return os.path.dirname(sys.executable)
    return os.path.dirname(__file__)