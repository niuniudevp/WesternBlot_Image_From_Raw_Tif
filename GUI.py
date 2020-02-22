from PyQt5.QtWidgets import QMainWindow,QLabel
from PyQt5.QtGui import QPixmap
from Block import *
from Utils import FUNC_RUN_ON_CHANGE,RUN_ON_CHANGE


class UI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_UI()
        self.__dict__.update({RUN_ON_CHANGE:self.universe_func})
    
    def init_UI(self):
        self.statusbar = self.statusBar()
        self.statusbar.showMessage('Ready')
        self.setGeometry(300, 300, 1500, 750)
        self.setWindowTitle('Auto My Western Blot')
        self.setMouseTracking(True)
        self.PressedKey=None
        
        #Ls.setGeometry(0,0,260,60)
        Tb=ToolBar(self)
        toobar=self.addToolBar("gongju")
        toobar.addWidget(Tb)
        toobar.move(0,0)
        self.ImgB=Img_Block(self)
        #self.ImgB.setGeometry(0,60,1000,600)
        #Hv=QHBoxLayout(self)
        #Hv.addWidget(Tb)
        #Hv.addWidget(ImgB)
        #self.setLayout(Hv)
        #print("SS")
        #self.Test()
        print("SS")




    def mousePressEvent(self,event):
        print("UI click!")
    
    def keyPressEvent(self,event):
        self.PressedKey=event.key()
        QMainWindow.keyPressEvent(self,event)
    def keyReleaseEvent(self,event):
        self.PressedKey=None
        QMainWindow.keyReleaseEvent(self,event)       
    
    def resizeEvent(self,event):
        #pass
        self.ImgB.AutoreSize()

    def universe_func(self,X=None):
        print("UNIVERSE_Working!")


    def Test(self):
        Demo(self)
        #lb=QLabel('AA',self)
        #lb.setPixmap(QPixmap('OET.jpeg'))
        #lb.setScaledContents(True)



class Demo(QLabel):
    def __init__(self,*args,**kwargs):
        QLabel.__init__(self,*args,**kwargs)
        WB='OET.jpeg'    
        self.setScaledContents(True)
        self.Box=QLabel(self)
        self.Box.setStyleSheet("border:1px solid red")
        self.Box.resize(100,100)
        self.setStyleSheet("border:1px solid blue")
        self.setGeometry(0,0,800,800)
        self.setPixmap(QPixmap('OET.jpeg'))
        
        #self.ui()
        #self.setText("ABCD")

    def ui(self):
        wb='OET.jpeg'
        self.setPixmap(QPixmap(wb))

    def mousePressEvent(self,event):
        pos=event.localPos()
        x=int(pos.x())
        y=int(pos.y())
        self.Box.move(x,y)

    

