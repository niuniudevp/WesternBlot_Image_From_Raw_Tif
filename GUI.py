from PyQt5.QtWidgets import QMainWindow, QLabel, QTabWidget, QDockWidget, QListWidget, QAction, QFileDialog
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from Base import ToolBar
from Image_Tree import Img_Tree
from Image_Editor import Image_Editor
import os


class UI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.Select_Dir = '~'
        self.Dir_content = None
        self.File_list = QListWidget()

        self.init_UI()

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
        QMainWindow.keyPressEvent(self, event)

    def keyReleaseEvent(self, event):
        self.PressedKey = None
        QMainWindow.keyReleaseEvent(self, event)

    def resizeEvent(self, event):
        pass
        #self.ImgB.AutoreSize()
        #self.Pre.setGeometry(10, self.ImgB.y()+ self.ImgB.height() + 10 , self.width() - 20, 150)

    def Test(self):
        pass

    def Set_Dir(self):
        dir = QFileDialog.getExistingDirectory(self, "Choose a Directory", "~")
        self.Select_Dir = dir
        self.Dir_content = os.listdir(dir)
        for i in self.Dir_content:
            self.File_list.addItem(i)

    def Main(self):
        self.Tb = ToolBar(self)
        toobar = self.addToolBar("gongju")
        self.opdir = QAction('Open', self)
        self.exprt = QAction('Export', self)
        self.svprj = QAction('Save', self)

        toobar.addAction(self.opdir)
        toobar.addAction(self.svprj)
        toobar.addAction(self.exprt)
        toobar.addWidget(self.Tb)

        self.Files = QDockWidget('Loaded Image Files')
        file2 = [{'wb': '/mnt/LENOVO/YQ,WWY/2020-实验/wb/Source_Data/ChemiDoc Images 2020-03-06_12.16.39/20200306-stambpl1-in-8cells_1(Chemiluminescence).tif', 'bkgd': '/mnt/LENOVO/YQ,WWY/2020-实验/wb/Source_Data/ChemiDoc Images 2020-03-06_12.16.39/20200306-stambpl1-in-8cells_7(Colorimetric).tif'}, {'wb': '/mnt/LENOVO/YQ,WWY/2020-实验/wb/Source_Data/ChemiDoc Images 2020-03-06_12.16.39/20200306-otub2-in-8cells_1(Chemiluminescence).tif', 'bkgd': '/mnt/LENOVO/YQ,WWY/2020-实验/wb/Source_Data/ChemiDoc Images 2020-03-06_12.16.39/20200306-otub2-in-8cells_8(Colorimetric).tif'}]
        self.Selected_Imgs = Img_Tree(file2, self)
        self.Selected_Imgs.enable_bottom_btn(True)
        self.Selected_Imgs.enable_contextmenu(True)
        self.Files.setWidget(self.Selected_Imgs)
        self.Files.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.Files)
        self.Selected_Imgs.Tree_Click_Signal.connect(self.Connect_Tree_To_Tab)

        Frame1 = QLabel('Add files to left Dock to Beign!',self)
        Frame1.setFont(QFont('Arial',20))
        Frame1.setAlignment(Qt.AlignCenter)
        self.Current = Frame1
        self.Tab = QTabWidget(self)
        self.Tab.addTab(self.Current, 'Main')
        #self.Preview = QFrame(self.Tab)
        self.Preview = Image_Editor(self.Tab)
        self.Tab.addTab(self.Preview, 'Final')
        self.setCentralWidget(self.Tab)
        #self.Tab.currentChanged.connect(self.Prev)


        self.Tab.currentChanged.connect(self.Prev_Slot)
        self.Tb.Changed.connect(self.Syncing_Tb_to_Imgb)
        self.opdir.triggered.connect(lambda: print(""))
        self.svprj.triggered.connect(lambda: print(""))
        self.exprt.triggered.connect(self.Selected_Imgs.Export_Raw)
        

    # Connect Tree_Click to Tab Panel
    def Connect_Tree_To_Tab(self, img_block_pre):
        self.Current = img_block_pre[0]
        self.Tab.removeTab(0)
        self.Tab.insertTab(0, self.Current, 'Current')
        self.Tab.setCurrentIndex(0)

    def Prev_Slot(self, index):
        if index == 1:
            self.Preview.display_img(self.Selected_Imgs.Tree)
            print(self.Selected_Imgs.imgs)
    # Preview function
    #@Sig_log
    
    def Syncing_Imgb_to_Tb(self):
        print("GuI Start Syncing Imgb to Tb")
        self.Tb.Toolbar_Sync_From_Img_Block([self.Current.ImgB])
        print("Gui End")

    #@Sig_log
    def Syncing_Tb_to_Imgb(self):
        print("GUI Syncing Tb to Imgb")
        self.Current.ImgB.Sync_from_toobar(self.Tb)
