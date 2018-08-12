# coding = utf-8

# 从资源文件夹加载前端和后端文件
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton,
                             QLineEdit, QHBoxLayout, QVBoxLayout,
                             QTextBrowser, QSlider, QLabel,
                             QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCursor

from resources import front_end, back_end, protocol
from multiprocessing.dummy import Lock, current_process
import sys
from math import cos, pi
# Pipe 用于前后端之间通讯 以及下载进程通报下载进度
# Pipe 应当在后续版本进行优化以实现分辨命令类型
# Lock 用于进程加锁，实际应用主要是实现不被打断地打印调试信息
# current_process 这个只是multiprocessing 实例化时必须要知道自己的_parent 是谁
# 真是奇怪的特性

class AppWindow(QWidget):

    def __init__(self, title, size=None):
        super().__init__()
        self.style = """ 
                QPushButton{ background:#222222;color:white;border-radius:0px; }
                QLabel{ color:#00ccff; }
                #window{ background:black;border-radius:4; }
                #close{ background-color:#660000;color:white; }
                #text{ background-color:black;color:#44ff00; }
                #editor{ background-color:#222222;color:#ff8800;border-radius:3; }
            """
        self.QPushButton = QPushButton
        self.title = title
        self.size = size if size else (800, 400)
        self.setStyleSheet(self.style)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.initUI()
        pipe = protocol.ProtocolPipe()
        (front_communicator, back_communicator) = pipe.connections()
        t_lock = Lock()
        process = current_process()
        self.Front = front_end.FrontEnd(front_communicator, t_lock, process)
        self.Back = back_end.BackEnd(back_communicator, t_lock, process)
        self.Front.lock_print = self.update_text
        thread_list = [self.Front, self.Back]
        for t in thread_list:
            t.start()

    def initUI(self):
        self.resize(*self.size)
        self.setWindowTitle(self.title)
        self.setObjectName("window")

        button_size = (25, 20)
        slider_size = (100, 20)
        label1 = QLabel()
        label1.setFixedHeight(20)

        label1.setText(self.title)
        label1.setAlignment(Qt.AlignLeft)

        btn1 = QPushButton("-", self)
        btn1.setFixedSize(*button_size)
        btn1.clicked.connect(self.showMinimized)
        self.window_button = QPushButton("□", self)
        self.window_button.setFixedSize(*button_size)
        self.window_button.clicked.connect(self._showMaximized)
        btn3 = QPushButton("×", self)
        btn3.setFixedSize(*button_size)
        btn3.setObjectName("close")
        btn3.clicked.connect(self.close)

        self.slider = QSlider(Qt.Horizontal, self)
        self.slider.setFixedSize(*slider_size)
        self.slider.setObjectName("slide")
        self.slider.setValue(75)
        self.slider.valueChanged.connect(self.change_transparent)

        self.Text = QTextBrowser()
        self.Text.setObjectName("text")
        self.Text.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.Text.setFrameShape(QFrame.NoFrame)

        self.Editor = QLineEdit("")
        self.Editor.setObjectName("editor")
        self.Editor.returnPressed.connect(self.send_text)

        hbox1 = QHBoxLayout()  # 水平布局
        hbox1.setSpacing(0)
        hbox1.addWidget(label1)
        hbox1.addStretch(1)
        hbox1.addWidget(self.slider)
        hbox1.addSpacing(10)
        hbox1.addWidget(btn1)
        hbox1.addWidget(self.window_button)
        hbox1.addWidget(btn3)

        vbox = QVBoxLayout()  # 垂直布局
        vbox.setSpacing(0)
        vbox.addLayout(hbox1)
        vbox.addWidget(self.Text)
        vbox.addWidget(self.Editor)
        self.setLayout(vbox)
        self.setWindowOpacity(0.75)

    def update_text(self, text):
        self.Text.append(">>> " + text)
        self.Text.moveCursor(QTextCursor.EndOfBlock)

    def send_text(self):
        text = self.Editor.text()
        self.Front.receive_info(text)
        self.Editor.setText("")

    def _showMaximized(self):
        self.showMaximized()
        self.window_button.clicked.disconnect()
        self.window_button.clicked.connect(self._showNormal)
        self.window_button.setText("■")

    def _showNormal(self):
        self.showNormal()
        self.window_button.clicked.disconnect()
        self.window_button.clicked.connect(self._showMaximized)
        self.window_button.setText("□")

    def change_transparent(self, slide_value):
        trans = slide_value*0.008 + 0.2
        self.setWindowOpacity(trans)

    # 重写三个方法使我们的Example窗口支持拖动,上面参数window就是拖动对象
    #############################################################
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.m_drag = True
            self.m_DragPosition = event.globalPos() - self.pos()
            event.accept()

    def mouseMoveEvent(self, QMouseEvent):
        if Qt.LeftButton and self.m_drag:
            self.move(QMouseEvent.globalPos() - self.m_DragPosition)
            QMouseEvent.accept()

    def mouseReleaseEvent(self, QMouseEvent):
        self.m_drag = False
    #############################################################


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AppWindow("Pixiv Downloader")
    window.show()
    sys.exit(app.exec_())

