from PyQt5.QtWidgets import QMainWindow, QLabel, QTabWidget, QDockWidget, QFileSystemModel, QListWidget, QAction, QFileDialog, QDirModel, QTreeView
from PyQt5.QtGui import QPixmap, QTransform, QImage

from Block import *
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
        """
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
        """
        QMainWindow.keyPressEvent(self, event)

    def keyReleaseEvent(self, event):
        self.PressedKey = None
        QMainWindow.keyReleaseEvent(self, event)

    def resizeEvent(self, event):
        pass
        #self.ImgB.AutoreSize()
        #self.Pre.setGeometry(10, self.ImgB.y()+ self.ImgB.height() + 10 , self.width() - 20, 150)

    def Test(self):
        self.D = Demo(self)

    def Set_Dir(self):
        dir = QFileDialog.getExistingDirectory(self, "Choose a Directory", "~")
        self.Select_Dir = dir
        self.Dir_content = os.listdir(dir)
        for i in self.Dir_content:
            self.File_list.addItem(i)

    def Main(self):
        self.Tb = ToolBar(self)
        toobar = self.addToolBar("gongju")
        opdir = QAction('Open Dir', self)
        opdir.triggered.connect(self.Set_Dir)
        toobar.addAction(opdir)
        toobar.addWidget(self.Tb)
        #toobar.move(0, 0)

        self.Files = QDockWidget('Loaded Image Files')
        model = QDirModel(self)
        home_path = QDir.currentPath()
        #model.setRootPath(home_path)
        model.setSorting(QDir.DirsFirst | QDir.IgnoreCase | QDir.Name)
        model.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs | QDir.AllEntries)

        #home_index = model.index(home_path)
        #self.treeSpace = My_Tree_View(self)
        #self.treeSpace.expand(home_index)
        #self.treeSpace.scrollTo(home_index)
        files = [{
            'wb': 'AAAAAAAA',
            'bkgd': 'BBBBB'
        }, {
            'wb': 'CCCCC',
            'bkgd': 'DDDDD'
        }, {
            'wb': 'EEE',
            'bkgd': 'FFF'
        }]
        self.load = Img_Tree(files, self)
        self.load.enable_bottom_btn(True)
        self.load.enable_contextmenu(True)
        self.Files.setWidget(self.load)

        #self.Files.setFloating(False)
        self.Files.setFeatures(QDockWidget.NoDockWidgetFeatures)

        self.addDockWidget(Qt.LeftDockWidgetArea, self.Files)

        Img_list = ['blot.tif', 'background.tif']
        Frame1 = Img_Block_Pre(Img_list, self)
        self.Current = Frame1
        Tab = QTabWidget(self)
        Tab.addTab(self.Current, 'Main')
        Tab.addTab(QFrame(), 'Final')
        self.setCentralWidget(Tab)
        self.Tb.Changed.connect(self.Syncing_Tb_to_Imgb)

    #@Sig_log
    def Syncing_Imgb_to_Tb(self):
        print("GuI Start Syncing Imgb to Tb")
        self.Tb.Toolbar_Sync_From_Img_Block([self.Current.ImgB])
        print("Gui End")

    #@Sig_log
    def Syncing_Tb_to_Imgb(self):
        print("GUI Syncing Tb to Imgb")
        self.Current.ImgB.Sync_from_toobar(self.Tb)


class Demo(QLabel):
    def __init__(self, *args, **kwargs):
        QLabel.__init__(self, *args, **kwargs)
        WB = 'OET.jpeg'
        self.setStyleSheet("border:1px solid blue")
        #self.setGeometry(0, 0, 800, 800)
        #self.setPixmap(QPixmap('OET.jpeg'))
        self.setFont(QFont('Arial', 20))
        self.setText("ABCEDF")
        self.adjustSize()
        print(self.geometry())

    def paintEvents(self, event):
        pt = QPainter()
        pt.begin(self)
        pt.setFont(QFont('Arial', 20))
        pt.setPen(QPen(QColor(0, 0, 0), 5))
        pt.drawText(22, 150, 'AAVVVFFDD')
        pt.drawRect(QRect(100, 100, 100, 100))
        pt.end()
        self.setFont(QFont('Arial', 20))
        self.setText("ABCEDF")
