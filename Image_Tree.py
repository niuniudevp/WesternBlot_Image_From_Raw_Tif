from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QAction, QMenu, QFrame, QAbstractItemView, QVBoxLayout, QPushButton
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt
from PyQt5.QtGui import QCursor, QGuiApplication
from Image_Block_Realtime_PreView import Img_Block_Pre


import os

class My_TreeItem(QTreeWidgetItem):
    """
    自定义TreeWidgetItem, 添加右键菜单项目
    """
    def __init__(self, *args, **kwargs):
        QTreeWidgetItem.__init__(self, *args, **kwargs)
        self.Type = 'WB'
        self.Path = ''
        self.Img_Block_Pre = None
        self.act_change = QAction('Change')
        self.act_delete = QAction('Delete')

    def show_menu(self):
        menu = QMenu()
        menu.addAction(self.act_change)
        if self.Type == 'WB':
            menu.addAction(self.act_delete)
        menu.exec(QCursor.pos())


class Img_Tree(QFrame):
    """
    本class实现将加载的dict 转化为列表tree（Wb_Img|_background_img）视图
    """
    Tree_Click_Signal = pyqtSignal(list)

    def __init__(self, img_dict, *args, **kwargs):
        QFrame.__init__(self, *args, **kwargs)
        self.Tree = QTreeWidget(self)
        self.Tree.setDropIndicatorShown(True)
        self.Tree.setDragEnabled(True)
        self.Tree.viewport().acceptDrops()
        self.Tree.setDragDropMode(QAbstractItemView.InternalMove)
        self.img_dict = img_dict
        self.Tree.setHeaderHidden(True)
        self.imgs = []
        self.Add_top_Level_Item(self.img_dict)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.Tree)
        self.setLayout(self.layout)
        self.Tree.clicked.connect(self.Tree_click)


    def Add_top_Level_Item(self, img_dict):
        if img_dict:
            for img in img_dict:
                c = My_TreeItem()
                _, File = os.path.split(img['wb'])
                c.setText(0, File)
                c.Path = img['wb']
                # 设置不可以被Drop
                c.setFlags(c.flags() & ~Qt.ItemIsDropEnabled)
                c.act_delete.triggered.connect(self.menu_delete)
                c.act_change.triggered.connect(self.menu_change)

                cc = My_TreeItem(c)
                cc.Type = 'BKGD'
                cc.act_change.triggered.connect(self.menu_change)
                _, File = os.path.split(img['bkgd'])
                cc.setText(0, File)
                cc.Path = img['bkgd']
                # 设置不可以被Drop
                cc.setFlags(cc.flags() & ~Qt.ItemIsDropEnabled)
                # 设置不可以被Drag
                cc.setFlags(cc.flags() & ~ Qt.ItemIsDragEnabled)
                self.Tree.addTopLevelItem(c)
            self.imgs = self.imgs + img_dict

    def enable_bottom_btn(self, bool):
        if bool:
            self.Add_Btn = QPushButton('Add New', self)
            self.Add_Btn.clicked.connect(self.Open_Pop_Wid)
            self.layout.addWidget(self.Add_Btn)

    def enable_contextmenu(self, bool):
        if bool:
            self.Tree.itemPressed.connect(self.show_menu)
    
    @pyqtSlot(list)
    def connect_pop_wid(self, list):
        """
        将Pop_Wid选择的图片传递给左侧的文件树
        """
        self.Add_top_Level_Item(list)

    def Open_Pop_Wid(self):
        """
        显示弹窗事件
        """
        from Broswer_Image import Broswer_Img
        Pop = Broswer_Img(self)
        Pop.Close_Signal.connect(self.connect_pop_wid)
        Pop.show()

    def Tree_click(self, Index):
        t = self.Tree.currentItem()
        # 是顶层元素的时候
        if t.parent() is None and t.child(0) is not None:
            list = [t.Path, t.child(0).Path]
            if t.Img_Block_Pre is None:
                t.Img_Block_Pre = Img_Block_Pre(list, self)
            self.Tree_Click_Signal.emit([t.Img_Block_Pre])

    @pyqtSlot(list)
    def update_img_list(self, new_img_list):
        self.Tree.clear()
        self.Add_top_Level_Item(new_img_list)

    # 添加右键菜单事项
    def show_menu(self, item, int):
        if (QGuiApplication.mouseButtons() & Qt.RightButton):
            item.show_menu()
    
    # 右键菜单Action响应
    def menu_delete(self):
        self.Tree.takeTopLevelItem(self.Tree.currentIndex().row())
    
    def menu_change(self):
        item = self.Tree.currentItem()
        if item.Type == 'WB':
            # 调用增加窗口，同时显示WB 和 BKGD
            pass
        if item.Type == 'BKGD':
            # 只显示BKGD
            pass


