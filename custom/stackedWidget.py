from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


class MyListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.mainwindow = parent
        self.setDragEnabled(True)
        # 选中不显示虚线
        # self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setFocusPolicy(Qt.NoFocus)

class StackedWidget(MyListWidget):
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.setAcceptDrops(True)
        self.setFlow(QListView.TopToBottom)  # 设置列表方向
        self.setDefaultDropAction(Qt.MoveAction)  # 设置拖放为移动而不是复制一个
        self.setDragDropMode(QAbstractItemView.InternalMove)  # 设置拖放模式, 内部拖放
        self.setMinimumWidth(300)

        self.move_item = None

