from PyQt5.QtWidgets import QFrame, QPushButton, QVBoxLayout, QTextEdit, QHBoxLayout, QLabel, QInputDialog, QLineEdit
from Anotation import Text_Act_Btn, Anotation, Magic_Input
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen, QColor


class Image_Editor(QFrame):
    # 整合注释功能和图片预览功能
    def __init__(self, *args, **kwargs):
        QFrame.__init__(self, *args, **kwargs)
        self.Preview_Btn = QPushButton("Preview", self)
        self.Add_Anon_Btn = QPushButton("Add Anotation", self)
        self.Action_Btns = Text_Act_Btn(self)
        self.Core = QFrame(self)
        self.Anotation = QVBoxLayout()
        self.Anotation.setAlignment(Qt.AlignCenter)
        self.Anotation_Frame = QFrame(self.Core)
        #self.Anotation_Frame.Can_Move_with_Mouse = True
        #self.Anotation_Frame.Can_Adjust_Edge = True
        self.Anotation_Frame.setStyleSheet("border:1px solid green")
        self.Anotation_Frame.setLayout(self.Anotation)
        self.Imgs = QVBoxLayout()
        self.Imgs.setAlignment(Qt.AlignCenter)
        self.Imgs_Frame = QFrame(self.Core)
        self.Imgs_Frame.setLayout(self.Imgs)
        #self.Imgs_Frame.setStyleSheet("border:1px solid red")
        self.DrawRect = []
        self.Info = QTextEdit(self.Core)
        hv = QVBoxLayout()
        hv.addWidget(self.Preview_Btn)
        hv.addWidget(self.Add_Anon_Btn)
        hv.addWidget(self.Action_Btns)
        core = QVBoxLayout()
        core.addWidget(self.Anotation_Frame)
        core.addWidget(self.Imgs_Frame)
        core.addWidget(self.Info)
        self.Core.setLayout(core)
        #self.Core.setStyleSheet("border:1px solid green")
        hv.addWidget(self.Core)
        # 顶层Layout
        main = QHBoxLayout()
        # 整体预览Frame
        self.Preview = QLabel(self)
        self.Preview.setStyleSheet("border:1px solid red")
        main.addLayout(hv)
        main.addWidget(self.Preview)
        main.setStretch(0, 1)
        main.setStretch(1, 1)
        self.setLayout(main)
        self.signal_connections()
        self.setMinimumSize(500, 800)

    def signal_connections(self):
        self.Add_Anon_Btn.clicked.connect(self.Add_Anotation)
        self.Action_Btns.Action_Signal.connect(self.Adjust_Response)
        self.Preview_Btn.clicked.connect(self.Gene_Preview)

    def Add_Anotation(self):
        an = Anotation(self)
        # 后面添加split_str的验证
        split_str = "1"
        split_str, okPressed = QInputDialog.getText(
            None, "Input Grid Mode", "Input grid mode(split by \",\")",
            QLineEdit.Normal, split_str)
        an.SetColumn(split_str)
        x, y, w, h = self.DrawRect
        an.setMaximumSize(w, h)
        self.Anotation.addWidget(an)

    def display_img(self, Tree_obj):
        max_height = 0
        max_width = 0
        for i in range(Tree_obj.topLevelItemCount()):
            t = Tree_obj.topLevelItem(i)
            img = t.Img_Block_Pre.Pre.PreView_Img
            self.DrawRect = t.Img_Block_Pre.Pre.draw_rec[0]['rect']
            try:
                q = self.Imgs.itemAt(i).widget()
            except AttributeError:
                q = QLabel(self.Imgs_Frame)
                self.Imgs.addWidget(q)
                q.setAlignment(Qt.AlignCenter)
            q.setPixmap(QPixmap.fromImage(img))

            #q.setMaximumSize(img.width(),img.height())
            #q.setMaximumHeight(img.height() + 4)
            max_height += img.height()
            max_width = max(max_width, img.width())
        #self.Imgs_Frame.setMaximumSize(max_width + self.Imgs.spacing() * 2, self.Imgs.spacing() * (i + 2) + max_height)

    # @pyqtSlot()
    def Adjust_Response(self, par):
        def get_Current_Focus_cell():
            for i in range(self.Anotation.count()):
                row = self.Anotation.itemAt(i).widget()
                for j in range(row.layout().count()):
                    cell = row.layout().itemAt(j).widget()
                    if cell.Actived:
                        return row, cell
            return None, None

        row, cell = get_Current_Focus_cell()
        if type(par) == str:
            if "0" in par:
                target = row
            else:
                target = cell
            if target is not None:
                x, y, w, h = target.x(), target.y(), target.width(
                ), target.height()
                if '>' in par:
                    target.setGeometry(x + 1, y, w, h)
                    target.setFixedSize(w, h)
                if '<' in par:
                    target.setGeometry(x - 1, y, w, h)
                    target.setFixedSize(w, h)
                if '+' in par:
                    target.setGeometry(x - 1, y, w + 2, h)
                    target.setFixedSize(w + 2, h)
                if '-' in par:
                    target.setGeometry(x + 1, y, w - 2, h)
                    target.setFixedSize(w - 2, h)
        if type(par) == int:
            pass

    def Gene_Preview(self):
        # 寻找self.core里面所有的
        # Magic_Input, QLabel, QTextEdit
        anotations = self.Core.findChildren(Magic_Input)
        Imgs = self.Core.findChildren(QLabel)
        Info = [self.Info]

        Img = QImage(self.Core.size(), QImage.Format_ARGB32)
        Img.fill(Qt.transparent)
        # Img.fill('white')
        pt = QPainter()
        pt.begin(Img)

        # 修正嵌套引起的坐标差异
        def Get_Pos_relative_to(t, a_parent_widget):
            x, y = t.x(), t.y()
            p = t.parent()
            while p != self.Core:
                x += p.x()
                y += p.y()
                p = p.parent()
            return x, y

        for img in Imgs:
            im = img.pixmap()
            x, y = Get_Pos_relative_to(img, self.Core)
            w, h = im.width(), im.height()
            pt.drawPixmap(x, y, w, h, im)

        for t in anotations:
            pt.setPen(QPen(QColor(0, 0, 0), 3))
            #pt.setFont(i['font'])
            x, y = Get_Pos_relative_to(t, self.Core)
            w, h = t.width(), t.height()
            pt.drawText(QRectF(x, y, w, h), Qt.AlignCenter, t.text())

        pt.end()
        self.Preview.setPixmap(QPixmap.fromImage(Img))
