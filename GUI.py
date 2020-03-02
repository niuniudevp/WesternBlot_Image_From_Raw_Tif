from PyQt5.QtWidgets import QMainWindow, QLabel
from PyQt5.QtGui import QPixmap,QTransform,QImage

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

        #self.Test()
        self.Main()
        print("SS")
        #hierarchy(self)

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
        pass
        #self.ImgB.AutoreSize()
        #self.Pre.setGeometry(10, self.ImgB.y()+ self.ImgB.height() + 10 , self.width() - 20, 150)

    def universe_func(self, X=None):
        print("UNIVERSE_Working!")

    def Test(self):
        self.D=Demo(self)


    def Main(self):
        self.Tb = ToolBar(self)
        toobar = self.addToolBar("gongju")
        toobar.addWidget(self.Tb)
        #toobar.move(0, 0)
        self.ImgB = Img_Block(self)
        self.Pre = PreView_Img(self)
        #self.Pre.setGeometry(10,self.ImgB.y()+self.ImgB.height()+10,self.width()-20,100)
        #self.ImgB.WB.Syncing.connect(self.Syncing_Imgb_to_Tb)
        #self.move()
        layout=QGridLayout()
        layout.addWidget(toobar,0,0)
        layout.addWidget(self.ImgB,1,0)
        layout.addWidget(self.Pre,2,0)
        layout.setRowStretch(1,6)
        layout.setRowStretch(2,3)
        self.setLayout(layout)
        self.ImgB.WB.Img.Changed_Signal.connect(lambda : print("Img Change Fired!"))
        self.ImgB.WB.Img.Indicator_Change_Signal.connect(self.Syncing_Imgb_to_Tb)
        self.ImgB.WB.Img.Indicator_Change_Signal.connect(lambda : self.Pre.Sync_From([self.ImgB]))
        self.ImgB.BG.Img.Indicator_Change_Signal.connect(lambda : self.Pre.Sync_From([self.ImgB]))
        
        self.Tb.Changed.connect(self.Syncing_Tb_to_Imgb)
    #@Sig_log
    def Syncing_Imgb_to_Tb(self):
        print("GuI Start Syncing Imgb to Tb")
        self.Tb.Toolbar_Sync_From_Img_Block([self.ImgB])
        print("Gui End")
    #@Sig_log
    def Syncing_Tb_to_Imgb(self):
        print("GUI Syncing Tb to Imgb")
        self.ImgB.Sync_from_toobar(self.Tb)


class Demo(QLabel):
    def __init__(self, *args, **kwargs):
        QLabel.__init__(self, *args, **kwargs)
        WB = 'OET.jpeg'
        self.setStyleSheet("border:1px solid blue")
        #self.setGeometry(0, 0, 800, 800)
        #self.setPixmap(QPixmap('OET.jpeg'))
        self.setFont(QFont('Arial',20))
        self.setText("ABCEDF")
        self.adjustSize()
        print(self.geometry())
    
    def paintEvents(self,event):
        pt=QPainter()
        pt.begin(self)
        pt.setFont(QFont('Arial',20))
        pt.setPen(QPen(QColor(0,0,0),5))
        pt.drawText(22,150,'AAVVVFFDD')
        pt.drawRect(QRect(100,100,100,100))
        pt.end()
        self.setFont(QFont('Arial',20))
        self.setText("ABCEDF")
