# -*- coding: utf-8 -*-
"""
Created on Wed Jan 13 17:51:21 2021

@author: YeZixun
"""


import time # 需要导入时间模块设置延时

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import QtCore, QtGui, QtWidgets
import pygame

class MediaPlayer(QThread):
  # 自定义信号对象。参数str就代表这个信号可以传一个字符串
  trigger = pyqtSignal(str)
  def __init__(self,parent=None):
    # 初始化函数
    super(MediaPlayer, self).__init__(parent=parent)

     
  def run(self):
      print("播放警告")
      pygame.init()
      sound = pygame.mixer.Sound(r"custom/warn.mp3")
      sound.set_volume(1)
      sound.play()


