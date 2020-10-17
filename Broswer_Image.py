from PyQt5.QtWidgets import QMainWindow, QFrame, QFileSystemModel, QFileDialog, QTreeView, QPushButton, QDockWidget, QVBoxLayout, QGridLayout, QLabel, QHBoxLayout
from PyQt5.QtCore import pyqtSignal, QDir, Qt, QSize
from Utils import CV_Img_to_QImage
from Image_Tree import Img_Tree
from Factory import BioRad_Imgs
import cv2
import os
from Config import *


class Broswer_Img(QMainWindow):
    """
    选择图片文件并且预览，自动匹配多图的情况和背景图片
    """
    Close_Signal = pyqtSignal(list)

    def __init__(self, *args, **kwargs):
        QMainWindow.__init__(self, *args, **kwargs)
        self.Current_Dir = QDir.home().absolutePath()
        #self.Current_Dir = Wk_Dir
        self.setWindowTitle("Select Imags")
        self.setWindowModality(Qt.ApplicationModal)
        self.Left_Dock_Code()
        self.Central_Frame_Code()
        self.Right_Dock_Code()
        self.connect_Signals()

        self.wb_nav_left.setEnabled(False)
        self.wb_nav_right.setEnabled(False)
        self.bkgd_nav_left.setEnabled(False)
        self.bkgd_nav_right.setEnabled(False)

        #self.setGeometry(200, 200, 1000, 600)
        #self.setMaximumSize(QSize(1000, 600))

    def Left_Dock_Code(self):
        self.Left_Frame = QFrame(self)
        self.Model = QFileSystemModel()
        self.Model.setNameFilterDisables(False)
        self.Model.setRootPath(self.Current_Dir)
        #self.Model.setSorting(QDir.DirsFirst | QDir.IgnoreCase | QDir.Name)
        self.Model.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs
                             | QDir.AllEntries)
        self.Model.setNameFilters(['*.tif'])
        self.Tree = QTreeView(self.Left_Frame)
        self.Tree.setModel(self.Model)
        self.Tree.setRootIndex(self.Model.index(self.Current_Dir))
        self.Tree.expandAll()
        self.Dir_Select = QPushButton("Select a Folder", self.Left_Frame)
        layout = QVBoxLayout()
        layout.addWidget(self.Tree)
        layout.addWidget(self.Dir_Select)
        self.Left_Frame.setLayout(layout)
        self.Left_Dock = QDockWidget('Broswer Images', self)
        self.Left_Dock.setWidget(self.Left_Frame)
        self.Left_Dock.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.Dir_Select.clicked.connect(self.dir_selection)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.Left_Dock)

    def Central_Frame_Code(self):
        self.Central_Frame = QFrame(self)
        layout = QGridLayout()
        self.wb_label = QLabel(self.Central_Frame)
        self.bkgd_label = QLabel(self.Central_Frame)
        #self.wb_label.setMaximumHeight(30)
        self.wb_label.setWordWrap(True)

        self.wb = QLabel(self.Central_Frame)
        self.wb.setScaledContents(True)
        self.bkgd = QLabel(self.Central_Frame)
        self.bkgd.setScaledContents(True)
        self.wb.setMaximumSize(QSize(300, 300))
        self.bkgd.setMaximumSize(QSize(300, 300))

        self.wb_navigator = QFrame(self.Central_Frame)
        self.wb_nav_left = QPushButton('<--', self.wb_navigator)
        self.wb_nav_right = QPushButton('-->', self.wb_navigator)
        nav_layout = QHBoxLayout()
        nav_layout.addWidget(self.wb_nav_left)
        nav_layout.addWidget(self.wb_nav_right)
        self.wb_navigator.setLayout(nav_layout)
        self.wb_navigator.setMaximumHeight(60)

        self.bkgd_navigator = QFrame(self.Central_Frame)
        self.bkgd_nav_left = QPushButton('<--', self.bkgd_navigator)
        self.bkgd_nav_right = QPushButton('-->', self.bkgd_navigator)
        nav_layout2 = QHBoxLayout()
        nav_layout2.addWidget(self.bkgd_nav_left)
        nav_layout2.addWidget(self.bkgd_nav_right)
        self.bkgd_navigator.setLayout(nav_layout2)
        self.bkgd_navigator.setMaximumHeight(60)

        self.btns = QFrame(self.Central_Frame)
        self.btns.setMaximumHeight(60)
        self.Btn_Add = QPushButton('Add', self.btns)
        self.Btn_Close = QPushButton('Close', self.btns)
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.Btn_Add)
        btn_layout.addWidget(self.Btn_Close)
        self.btns.setLayout(btn_layout)

        # 根据具体的传入参数构建不同的视图
        layout.addWidget(self.wb_label, 0, 0)
        layout.addWidget(self.bkgd_label, 0, 1)

        layout.addWidget(self.wb, 1, 0)
        layout.addWidget(self.bkgd, 1, 1)

        layout.addWidget(self.wb_navigator, 2, 0)
        layout.addWidget(self.bkgd_navigator, 2, 1)

        layout.addWidget(self.btns, 3, 0, 2, 0)
        layouts = QVBoxLayout()
        layouts.addLayout(layout)
        self.Central_Frame.setLayout(layouts)
        self.setCentralWidget(self.Central_Frame)
        #self.setStyleSheet('border:1px solid red')

    def Right_Dock_Code(self):
        self.Added_Img_tree = Img_Tree([], self)
        self.Right_Dock = QDockWidget('Selected Images', self)
        self.Right_Dock.setWidget(self.Added_Img_tree)
        self.Right_Dock.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.addDockWidget(Qt.RightDockWidgetArea, self.Right_Dock)

    def connect_Signals(self):
        self.Tree.clicked.connect(self.Load_Img_to_Central_Frame)
        self.wb_nav_left.clicked.connect(self.change_img_index)
        self.wb_nav_right.clicked.connect(self.change_img_index)
        self.bkgd_nav_left.clicked.connect(self.change_img_index)
        self.bkgd_nav_right.clicked.connect(self.change_img_index)
        self.Btn_Add.clicked.connect(self.Add_Btn_Action)
        self.Btn_Close.clicked.connect(self.Close_Btn_Action)

    def Load_Img_to_Central_Frame(self, Index):
        select_file = self.Tree.model().filePath(Index)
        _, ext = os.path.splitext(select_file)
        if ext in ['.tif', '.jpeg', '.png', '.jpg']:
            self.Related_Imgs = BioRad_Imgs(select_file)
        self.set_Central_Frame()

    def set_Central_Frame(self):
        self.wb_nav_left.setEnabled(False)
        self.wb_nav_right.setEnabled(False)
        self.bkgd_nav_left.setEnabled(False)
        self.bkgd_nav_right.setEnabled(False)

        self.current_wb = self.Related_Imgs.WB_list[self.Related_Imgs.wb_index]
        self.current_bkgd = self.Related_Imgs.BKGD_list[
            self.Related_Imgs.bkgd_index]
        self.wb_label.setText(
            self.current_wb.replace(self.Related_Imgs.Dir, '.'))
        self.bkgd_label.setText(
            self.current_bkgd.replace(self.Related_Imgs.Dir, '.'))
        wb, _ = CV_Img_to_QImage(cv2.imread(self.current_wb))
        bkgd, _ = CV_Img_to_QImage(cv2.imread(self.current_bkgd))
        self.wb.setPixmap(wb)
        self.wb.setScaledContents(True)
        self.bkgd.setPixmap(bkgd)
        wb_len = len(self.Related_Imgs.WB_list)
        bkgd_len = len(self.Related_Imgs.BKGD_list)
        if self.Related_Imgs.wb_index > 0:
            self.wb_nav_left.setEnabled(True)
        if wb_len - self.Related_Imgs.wb_index > 1:
            self.wb_nav_right.setEnabled(True)

        if self.Related_Imgs.bkgd_index > 0:
            self.bkgd_nav_left.setEnabled(True)
        if bkgd_len - self.Related_Imgs.bkgd_index > 1:
            self.bkgd_nav_right.setEnabled(True)

    def change_img_index(self):
        sender = self.sender()
        if sender == self.wb_nav_left:
            self.Related_Imgs.wb_index = self.Related_Imgs.wb_index - 1
        if sender == self.wb_nav_right:
            self.Related_Imgs.wb_index = self.Related_Imgs.wb_index + 1
        if sender == self.bkgd_nav_left:
            self.Related_Imgs.bkgd_index = self.Related_Imgs.bkgd_index - 1
        if sender == self.bkgd_nav_right:
            self.Related_Imgs.bkgd_index = self.Related_Imgs.bkgd_index + 1
        self.set_Central_Frame()

    def Add_Btn_Action(self):
        list = [{'wb': self.current_wb, 'bkgd': self.current_bkgd}]
        self.Added_Img_tree.Add_top_Level_Item(list)
        print(self.Added_Img_tree.imgs)

    def Close_Btn_Action(self):
        self.close()

    def closeEvent(self, event):
        self.Close_Signal.emit(self.Added_Img_tree.imgs)

    def dir_selection(self):
        global Wk_Dir
        dir = QFileDialog.getExistingDirectory(self, "Choose a Directory", Wk_Dir)
        self.Current_Dir = dir
        Wk_Dir=dir
        self.Tree.setRootIndex(self.Model.index(self.Current_Dir))
        self.Left_Dock.setWindowTitle(dir)