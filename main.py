import ctypes
import sys
import time

import cv2
import numpy as np
import qdarkstyle
from PIL import Image
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.Qt import QThread
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from custom.graphicsView import GraphicsView
from custom.listWidgets import *
from custom.stackedWidget import *
from custom.treeView import FileSystemTreeView
from yolo import YOLO

ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")

# 多线程实时检测
class DetectThread(QThread):
    Send_signal = pyqtSignal(np.ndarray, int)

    def __init__(self, fileName):
        super(DetectThread, self).__init__()
        self.capture = cv2.VideoCapture(fileName)
        self.count = 0
        self.warn = False  # 是否发送警告信号

    def run(self):
        ret, self.frame = self.capture.read()
        while ret:
            ret, self.frame = self.capture.read()
            self.detectCall()

    def detectCall(self):
        fps = 0.0
        t1 = time.time()
        # 读取某一帧
        frame = self.frame
        # 格式转变，BGRtoRGB
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # 转变成Image
        frame = Image.fromarray(np.uint8(frame))
        # 进行检测
        frame_new, predicted_class = yolo.detect_image(frame)
        frame = np.array(frame_new)
        if predicted_class == "face":
            self.count = self.count+1
        else:
            self.count = 0
        # RGBtoBGR满足opencv显示格式
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        fps = (fps + (1./(time.time()-t1))) / 2
        print("fps= %.2f" % (fps))
        frame = cv2.putText(frame, "fps= %.2f" % (
            fps), (0, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        if self.count > 30:
            self.count = 0
            self.warn = True
        else:
            self.warn = False
        # 发送pyqt信号
        self.Send_signal.emit(frame, self.warn)

class MyApp(QMainWindow):
    def __init__(self):
        super(MyApp, self).__init__()

        self.cap = cv2.VideoCapture()
        self.CAM_NUM = 0
        self.thread_status = False  # 判断识别线程是否开启
        self.tool_bar = self.addToolBar('工具栏')
        self.action_right_rotate = QAction(
            QIcon("icons/右旋转.png"), "向右旋转90", self)
        self.action_left_rotate = QAction(
            QIcon("icons/左旋转.png"), "向左旋转90°", self)
        self.action_opencam = QAction(QIcon("icons/摄像头.png"), "开启摄像头", self)
        self.action_video = QAction(QIcon("icons/video.png"), "加载视频", self)
        self.action_image = QAction(QIcon("icons/图片.png"), "加载图片", self)
        self.action_right_rotate.triggered.connect(self.right_rotate)
        self.action_left_rotate.triggered.connect(self.left_rotate)
        self.action_opencam.triggered.connect(self.opencam)
        self.action_video.triggered.connect(self.openvideo)
        self.action_image.triggered.connect(self.openimage)
        self.tool_bar.addActions((self.action_left_rotate, self.action_right_rotate,
                                  self.action_opencam, self.action_video, self.action_image))
        self.stackedWidget = StackedWidget(self)
        self.fileSystemTreeView = FileSystemTreeView(self)
        self.graphicsView = GraphicsView(self)
        self.dock_file = QDockWidget(self)
        self.dock_file.setWidget(self.fileSystemTreeView)
        self.dock_file.setTitleBarWidget(QLabel('目录'))
        self.dock_file.setFeatures(QDockWidget.NoDockWidgetFeatures)

        self.dock_attr = QDockWidget(self)
        self.dock_attr.setWidget(self.stackedWidget)
        self.dock_attr.setTitleBarWidget(QLabel('上报数据'))
        self.dock_attr.setFeatures(QDockWidget.NoDockWidgetFeatures)

        self.setCentralWidget(self.graphicsView)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dock_file)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock_attr)

        self.setWindowTitle('口罩佩戴检测')
        self.setWindowIcon(QIcon('icons/mask.png'))
        self.src_img = None
        self.cur_img = None

    def update_image(self):
        if self.src_img is None:
            return
        img = self.process_image()
        self.cur_img = img
        self.graphicsView.update_image(img)

    def change_image(self, img):
        self.src_img = img
        img = self.process_image()
        self.cur_img = img
        self.graphicsView.change_image(img)

    def process_image(self):
        img = self.src_img.copy()
        for i in range(self.useListWidget.count()):
            img = self.useListWidget.item(i)(img)
        return img

    def right_rotate(self):
        self.graphicsView.rotate(90)

    def left_rotate(self):
        self.graphicsView.rotate(-90)

    def add_item(self, image):
        # 总Widget
        wight = QWidget()
        # 总体横向布局
        layout_main = QHBoxLayout()
        map_l = QLabel()  # 图片显示
        map_l.setFixedSize(60, 40)
        map_l.setPixmap(image.scaled(60, 40))
        # 右边的纵向布局
        layout_right = QVBoxLayout()
        # 右下的的横向布局
        layout_right_down = QHBoxLayout()  # 右下的横向布局
        layout_right_down.addWidget(
            QLabel(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))

        # 按照从左到右, 从上到下布局添加
        layout_main.addWidget(map_l)  # 最左边的图片
        layout_right.addWidget(QLabel('警告！检测到未佩戴口罩'))  # 右边的纵向布局
        layout_right.addLayout(layout_right_down)  # 右下角横向布局
        layout_main.addLayout(layout_right)  # 右边的布局
        wight.setLayout(layout_main)  # 布局给wight
        item = QListWidgetItem()  # 创建QListWidgetItem对象
        item.setSizeHint(QSize(300, 80))  # 设置QListWidgetItem大小
        self.stackedWidget.addItem(item)  # 添加item
        self.stackedWidget.setItemWidget(item, wight)  # 为item设置widget

    def openvideo(self):
        print(self.thread_status)
        if self.thread_status == False:

            fileName, filetype = QFileDialog.getOpenFileName(
                self, "选择视频", "D:/", "*.mp4;;*.flv;;All Files(*)")

            flag = self.cap.open(fileName)
            if flag == False:
                msg = QtWidgets.QMessageBox.warning(self, u"警告", u"请选择视频文件",
                                                    buttons=QtWidgets.QMessageBox.Ok,
                                                    defaultButton=QtWidgets.QMessageBox.Ok)
            else:
                self.detectThread = DetectThread(fileName)
                self.detectThread.Send_signal.connect(self.Display)
                self.detectThread.start()
                self.action_video.setText('关闭视频')
                self.thread_status = True
        elif self.thread_status == True:
            self.detectThread.terminate()
            if self.cap.isOpened():
                self.cap.release()
            self.action_video.setText('打开视频')
            self.thread_status = False

    def openimage(self):
        if self.thread_status == False:
            fileName, filetype = QFileDialog.getOpenFileName(
                self, "选择图片", "D:/", "*.jpg;;*.png;;All Files(*)")
            if fileName != '':
                src_img = Image.open(fileName)
                r_image, predicted_class = yolo.detect_image(src_img)
                r_image = np.array(r_image)
                showImage = QtGui.QImage(
                    r_image.data, r_image.shape[1], r_image.shape[0], QtGui.QImage.Format_RGB888)
                self.graphicsView.set_image(QtGui.QPixmap.fromImage(showImage))

    def opencam(self):
        if self.thread_status == False:
            flag = self.cap.open(self.CAM_NUM)
            if flag == False:
                msg = QtWidgets.QMessageBox.warning(self, u"警告", u"请检测相机与电脑是否连接正确",
                                                    buttons=QtWidgets.QMessageBox.Ok,
                                                    defaultButton=QtWidgets.QMessageBox.Ok)
            else:
                self.detectThread = DetectThread(self.CAM_NUM)
                self.detectThread.Send_signal.connect(self.Display)
                self.detectThread.start()
                self.action_video.setText('关闭视频')
                self.thread_status = True
        else:
            self.detectThread.terminate()
            if self.cap.isOpened():
                self.cap.release()
            self.action_video.setText('打开视频')
            self.thread_status = False

    def Display(self, frame, warn):

        im = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        showImage = QtGui.QImage(
            im.data, im.shape[1], im.shape[0], QtGui.QImage.Format_RGB888)
        self.graphicsView.set_image(QtGui.QPixmap.fromImage(showImage))

    def closeEvent(self, event):
        ok = QtWidgets.QPushButton()
        cacel = QtWidgets.QPushButton()
        msg = QtWidgets.QMessageBox(
            QtWidgets.QMessageBox.Warning, u"关闭", u"确定退出？")
        msg.addButton(ok, QtWidgets.QMessageBox.ActionRole)
        msg.addButton(cacel, QtWidgets.QMessageBox.RejectRole)
        ok.setText(u'确定')
        cacel.setText(u'取消')
        if msg.exec_() == QtWidgets.QMessageBox.RejectRole:
            event.ignore()
        else:
            if self.thread_status == True:
                self.detectThread.terminate()
            if self.cap.isOpened():
                self.cap.release()
            event.accept()


if __name__ == "__main__":
    # 初始化yolo模型
    yolo = YOLO()
    app  = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    window = MyApp()
    window.show()
    sys.exit(app.exec_())
