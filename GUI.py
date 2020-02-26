from PyQt5.QtWidgets import QMainWindow, QLabel
from PyQt5.QtGui import QPixmap
from Block import *
from Utils import FUNC_RUN_ON_CHANGE, RUN_ON_CHANGE


class UI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_UI()
        self.__dict__.update({RUN_ON_CHANGE: self.universe_func})

    def init_UI(self):
        self.statusbar = self.statusBar()
        self.statusbar.showMessage('Ready')
        self.setGeometry(300, 300, 1500, 750)
        self.setWindowTitle('Auto My Western Blot')
        self.setMouseTracking(True)
        self.PressedKey = None
        self.Active_Indicator = None

        #Ls.setGeometry(0,0,260,60)

        #self.ImgB.setGeometry(0,60,1000,600)
        #Hv=QHBoxLayout(self)
        #Hv.addWidget(Tb)
        #Hv.addWidget(ImgB)
        #self.setLayout(Hv)
        #print("SS")
        #self.Test()
        self.Main()
        print("SS")
        hierarchy(self)

    def mousePressEvent(self, event):
        print("UI click!")

    def keyPressEvent(self, event):
        self.PressedKey = event.key()

        if self.PressedKey in [
                Qt.Key_Right, Qt.Key_Left, Qt.Key_Up, Qt.Key_Down
        ] and self.Active_Indicator:
            self.ImgB.setFocus()

        if self.Active_Indicator:
            i = self.Active_Indicator
            if self.PressedKey == Qt.Key_Up:
                i.move(i.x(), i.y() - 1)
            elif self.PressedKey == Qt.Key_Down:
                i.move(i.x(), i.y() + 1)
            elif self.PressedKey == Qt.Key_Left:
                i.move(i.x() - 1, i.y())
            elif self.PressedKey == Qt.Key_Right:
                i.move(i.x() + 1, i.y())

        QMainWindow.keyPressEvent(self, event)

    def keyReleaseEvent(self, event):
        self.PressedKey = None
        QMainWindow.keyReleaseEvent(self, event)

    def resizeEvent(self, event):
        #pass
        self.ImgB.AutoreSize()

    def universe_func(self, X=None):
        print("UNIVERSE_Working!")

    def Test(self):
        RL = Reference_Line('H', 200, self)
        RL.Label.Only_Move_V = True

        VL = Reference_Line('V', 200, self)
        VL.Label.Only_Move_H = True
        VL.Color = 'red'
        VL.Appearance()

        ML = MyLabel('AAAAAA', self)
        ML.resize(100, 100)
        #ML.setText('ABCD')
        ML.Can_Move_with_Mouse = True
        ML.Can_move_with_Arrow_Key = True
        ML.Can_Adjust_Edge = True
        ML.Only_Move_H = True

        ML.setStyleSheet("border:2px solid red")

    def Main(self):
        self.Tb = ToolBar(self)
        toobar = self.addToolBar("gongju")
        toobar.addWidget(self.Tb)
        toobar.move(0, 0)
        self.ImgB = Img_Block(self)


class Demo(QLabel):
    def __init__(self, *args, **kwargs):
        QLabel.__init__(self, *args, **kwargs)
        WB = 'OET.jpeg'
        self.setScaledContents(True)
        self.Box = QLabel(self)
        self.Box.setStyleSheet("border:1px solid red")
        self.Box.resize(100, 100)
        self.setStyleSheet("border:1px solid blue")
        self.setGeometry(0, 0, 800, 800)
        self.setPixmap(QPixmap('OET.jpeg'))

        #self.ui()
        #self.setText("ABCD")

    def ui(self):
        wb = 'OET.jpeg'
        self.setPixmap(QPixmap(wb))

    def mousePressEvent(self, event):
        pos = event.localPos()
        x = int(pos.x())
        y = int(pos.y())
        self.Box.move(x, y)
