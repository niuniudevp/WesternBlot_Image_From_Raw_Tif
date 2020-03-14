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

        self.Files = QDockWidget('Loaded Image Files')
        file2 = [{'wb': '/media/nzt/LENOVO1/YQ,WWY/2020-实验/wb/ChemiDoc Images 2020-03-06_12.16.39/20200306-stambpl1-in-8cells_1(Chemiluminescence).tif', 'bkgd': '/media/nzt/LENOVO1/YQ,WWY/2020-实验/wb/ChemiDoc Images 2020-03-06_12.16.39/20200306-stambpl1-in-8cells_7(Colorimetric).tif'}, {'wb': '/media/nzt/LENOVO1/YQ,WWY/2020-实验/wb/ChemiDoc Images 2020-03-06_12.16.39/20200306-otub2-in-8cells_1(Chemiluminescence).tif', 'bkgd': '/media/nzt/LENOVO1/YQ,WWY/2020-实验/wb/ChemiDoc Images 2020-03-06_12.16.39/20200306-otub2-in-8cells_8(Colorimetric).tif'}]
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
        self.Preview = QFrame(self.Tab)
        self.Tab.addTab(self.Preview, 'Final')
        self.setCentralWidget(self.Tab)
        self.Tab.currentChanged.connect(self.Prev)
        self.Tb.Changed.connect(self.Syncing_Tb_to_Imgb)

    # Connect Tree_Click to Tab Panel
    def Connect_Tree_To_Tab(self, img_block_pre):
        self.Current = img_block_pre[0]
        self.Tab.removeTab(0)
        self.Tab.insertTab(0, self.Current, 'Current')
        self.Tab.setCurrentIndex(0)

    # Preview function
    def Prev(self, index):
        if index == 1:
            layout = self.Preview.layout()
            if layout is None:
                ly = QVBoxLayout()
                ly.setSpacing(10)
                self.Preview.setLayout(ly)
                layout = self.Preview.layout()
            tree = self.Selected_Imgs.Tree
            max_height = 0
            max_width = 0
            for i in range(tree.topLevelItemCount()):
                t = tree.topLevelItem(i)
                img = t.Img_Block_Pre.Pre.PreView_Img
                try:
                    q = layout.itemAt(i).widget()
                except AttributeError:
                    q = QLabel(self.Preview)
                    layout.addWidget(q)
                    q.setAlignment(Qt.AlignCenter)
                q.setPixmap(QPixmap.fromImage(img))
                q.setMaximumHeight(img.height() + 4)
                max_height += img.height()
                max_width = max(max_width, img.width())
            self.Preview.setMaximumSize(max_width + layout.spacing() * 2, layout.spacing() * (i + 2) + max_height)
            #self.Preview.setStyleSheet("border: 1px solid red")
                
        pass
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
