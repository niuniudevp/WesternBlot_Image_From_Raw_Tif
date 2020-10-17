from PyQt5.QtWidgets import QFrame, QComboBox, QDialog, QScrollArea, QDialogButtonBox, QFormLayout, QPushButton, QVBoxLayout, QTextEdit, QHBoxLayout, QLabel, QFileDialog, QInputDialog, QLineEdit
from Anotation import Text_Act_Btn, Anotation, Magic_Input
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen, QColor
from Utils import File_path, CV_Img_to_QImage, QImage_to_CV_Img
from bound_detect import bound_from_cv_img
from Base import Muliti_Input_Dialog
import cv2


class Bound_Split_Dialog_Preview(Muliti_Input_Dialog):
    def __init__(self, *args, **kwargs):
        Muliti_Input_Dialog.__init__(self, *args, **kwargs)
        self.Split = QLineEdit(self)
        self.Split.setText("1")
        self.Ref = QComboBox(self)
        self.Preview = QLabel(self)
        self.Preview.setStyleSheet("background:white")
        self.Preview.setAlignment(Qt.AlignCenter)
        self.Add_row('Input Grid Mode:', self.Split)
        self.Add_row('Choose Bound Refer:', self.Ref)
        self.Derivate_cutoff_x = QLineEdit(self)
        self.Derivate_cutoff_x.setText("1")
        self.Add_row('Derivate cutoff x:', self.Derivate_cutoff_x)
        self.Derivate_cutoff_y = QLineEdit(self)
        self.Derivate_cutoff_y.setText("1")
        self.Add_row('Derivate cutoff y:', self.Derivate_cutoff_y)
        self.Add_row(self.Preview)

        self.Split.textEdited.connect(self.update_preview)
        self.Ref.currentIndexChanged.connect(self.update_preview)
        self.Derivate_cutoff_x.textEdited.connect(self.update_preview)
        self.Derivate_cutoff_y.textEdited.connect(self.update_preview)
        self.Split_Width = []

    def update_preview(self):
        data = self.Ref.currentData()
        img = data['img']
        x, y, w, h = data['rec']
        wb_img = img.copy(x + 2, y, w - 4, h)
        cv_img = QImage_to_CV_Img(wb_img)
        if self.Derivate_cutoff_x.text():
            cutoff_x = float(self.Derivate_cutoff_x.text())
        else:
            cutoff_x = 1

        if self.Derivate_cutoff_x.text():
            cutoff_y = float(self.Derivate_cutoff_x.text())
        else:
            cutoff_y = 1

        bounds_x, bounds_y = bound_from_cv_img(cv_img, cutoff_x, cutoff_y)
        bounds_x_fixed = bounds_x + x + 2
        self.bounds_x = bounds_x_fixed
        bounds_y_fixed = bounds_y + y + 2
        cv_img = QImage_to_CV_Img(img)
        ih = cv_img.shape[0]
        iw = cv_img.shape[1]
        for split in bounds_x_fixed:
            cv_img = cv2.line(cv_img, (split, 0), (split, ih), (255, 0, 0), 1)
        for split in bounds_y_fixed:
            cv_img = cv2.line(cv_img, (0, split), (iw, split), (255, 0, 0), 1)

        # 补充根据split_str 来分割框框
        split_str = self.Split.text().split(',')
        split_str = [int(i) for i in split_str if len(i) > 0]
        ll = min(len(split_str), len(bounds_x_fixed))
        current = 0
        self.Split_str = split_str[0:ll]
        self.Split_Width = []
        for i in range(ll):
            sp = split_str[i]
            start = current
            end = current + sp
            self.Split_Width.append(bounds_x_fixed[end] -
                                    bounds_x_fixed[start])
            cv_img = cv2.line(cv_img,
                              (bounds_x_fixed[start] + 10, bounds_y_fixed[0]),
                              (bounds_x_fixed[end] - 10, bounds_y_fixed[1]),
                              (0, 0, 255), 2)
            current = end
        qimg, _ = CV_Img_to_QImage(cv_img)
        self.Preview.setPixmap(qimg)


class Image_Editor(QFrame):
    # 整合注释功能和图片预览功能
    def __init__(self, *args, **kwargs):
        QFrame.__init__(self, *args, **kwargs)
        #self.Preview_Btn = QPushButton("Preview", self)
        #self.Save_Preview_Btn = QPushButton("Save Preview", self)
        #self.Save_Raw_Btn = QPushButton("Save Raw Images", self)
        self.Save_To_Dir = ''
        #self.Add_Anon_Btn = QPushButton("Add Anotation", self)
        #self.Action_Btns = Text_Act_Btn(self)
        self.Core = QFrame(self)

        #self.Anotation_Ref_Gene_Index = 0
        #self.Anotation_Split_Mode = "1"
        #self.Anotation = QVBoxLayout()
        #self.Anotation.setAlignment(Qt.AlignCenter)
        #self.Anotation_Frame = QFrame(self.Core)
        #self.Anotation_Frame.setStyleSheet("border:1px solid green")
        #self.Anotation_Frame.setContentsMargins(0, 0, 0, 0)
        #self.Anotation_Frame.setLayout(self.Anotation)

        self.Imgs = QVBoxLayout()
        self.Imgs.setAlignment(Qt.AlignCenter|Qt.AlignTop)
        self.Imgs.setSpacing(10)
        self.Imgs_Frame = QFrame(self.Core)
        self.Imgs_Frame.setContentsMargins(0, 0, 0, 0)
        #self.Imgs_Frame.setStyleSheet("border:1px solid red")
        self.Imgs_Frame.setLayout(self.Imgs)
        
        self.Imgs_Gene_List = []

        #self.Imgs_Frame.setStyleSheet("border:1px solid red")
        self.Img_DrawRects = []

        #self.Info = QTextEdit(self.Core)
        #self.Info.setMaximumHeight(300)
        hv = QVBoxLayout()
        #hv.addWidget(self.Preview_Btn)
        #td = QHBoxLayout()
        #td.addWidget(self.Save_Preview_Btn)
        #td.addWidget(self.Save_Raw_Btn)
        #hv.addLayout(td)
        #hv.addWidget(self.Add_Anon_Btn)
        #hv.addWidget(self.Action_Btns)
        core = QVBoxLayout()
        #core.setSpacing(0)
        core.setAlignment(Qt.AlignCenter)
        #core.addWidget(self.Anotation_Frame)
        core.addWidget(self.Imgs_Frame)
        #core.addWidget(self.Info)
        Sc = QScrollArea(self)

        self.Core.setLayout(core)
        Sc.setWidget(self.Core)
        Sc.setWidgetResizable(True)
        #Sc.setGeometry(Sc.parentWidget().geometry())
        #self.Core.setStyleSheet("border:1px solid yellow")
        hv.addWidget(Sc)
        # 顶层Layout
        main = QHBoxLayout()
        # 整体预览Frame
        #self.Preview = QLabel(self)
        #self.Preview.setStyleSheet("border:1px solid red")
        main.addLayout(hv)
        #main.addWidget(self.Preview)
        main.setStretch(0, 1)
        #main.setStretch(1, 1)
        
        self.setLayout(main)
        self.signal_connections()
        #self.setMinimumSize(500, 800)

    def signal_connections(self):
        #self.Add_Anon_Btn.clicked.connect(self.Add_Anotation)
        #self.Action_Btns.Action_Signal.connect(self.Adjust_Response)
        #self.Preview_Btn.clicked.connect(self.Gene_Preview)
        #self.Save_Preview_Btn.clicked.connect(self.Save_Img)
        #self.Save_Raw_Btn.clicked.connect(self.Save_Raw)
        pass

    def Add_Anotation(self):
        an = Anotation(self)
        # 后面添加split_str的验证
        #split_str = "1"
        # 改写使其能够同时接受参照Gene条带

        mt = Bound_Split_Dialog_Preview(self)
        for i in range(len(self.Imgs_Gene_List)):
            mt.Ref.addItem(self.Imgs_Gene_List[i], self.Img_DrawRects[i])
        if self.Anotation_Ref_Gene_Index == -1:
            mt.Ref.setCurrentIndex(len(self.Imgs_Gene_List) - 1)
        else:
            mt.Ref.setCurrentIndex(self.Anotation_Ref_Gene_Index)

        if mt.exec() == QDialog.Accepted:
            self.Anotation_Split_Mode = mt.Split_Width
            self.Anotation_Ref_Gene_Index = mt.Ref.currentIndex()
            start_pos = mt.bounds_x[0]
            end_pos = mt.bounds_x[len(mt.Split_Width)]
            an.SetColumn([mt.Split_str, mt.Split_Width], start_pos, end_pos)
            self.Anotation.addWidget(an)
            #self.Adjust_Point()
    
    def Adjust_Point(self):
        Ref_Img = self.Imgs.itemAt(self.Anotation_Ref_Gene_Index).widget().pixmap()
        Ref_Img = Ref_Img.toImage()
        w = Ref_Img.width()
        diff = int((self.Imgs_Frame.width() - w) / 2)
        for i in range(self.Anotation.count()):
            an = self.Anotation.itemAt(i).widget()
            an.setContentsMargins(diff + an.start_pos, 0, w - an.end_pos + diff, 0)


    def display_img(self, Tree_obj):
        max_height = 0
        max_width = 0
        genes = []
        # 先清空self.Imgs中的图片
        for i in range(self.Imgs.count()):
            self.Imgs.itemAt(i).widget().clear()

        for i in range(Tree_obj.topLevelItemCount()):
            t = Tree_obj.topLevelItem(i)
            img = t.Img_Block_Pre.Pre.PreView_Img
            genes.append(t.Img_Block_Pre.ImgB.WB.Img.Indicator[0].Name.text())
            rect = t.Img_Block_Pre.Pre.rect_fix(
                t.Img_Block_Pre.Pre.draw_rec[0]['rect'])
            self.Img_DrawRects.append({'img': img, 'rec': rect})
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
        self.Imgs_Gene_List = genes

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
        #Info = [self.Info]

        Img = QImage(self.Core.size(), QImage.Format_ARGB32)
        Img.fill(Qt.transparent)
        # Img.fill('white')
        pt = QPainter()
        pt.begin(Img)

        # 修正嵌套引起的坐标差异
        def Get_Pos_relative_to(t, a_parent_widget):
            dx = (t.width() - t.pixmap().width())//2
            dy = (t.height() - t.pixmap().height())//2
            x, y = t.x() + dx, t.y() + dy
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
        #self.Preview.setPixmap(QPixmap.fromImage(Img))
        return Img

    def Save_Img(self):
        Img = self.Gene_Preview()
        Img = QPixmap.fromImage(Img)
        FileName = QFileDialog.getSaveFileName(self, 'Save as',
                                               self.Save_To_Dir, '*.png')[0]
        Img.save(FileName, 'png')
        dir, _, _ = File_path(FileName)
        self.Save_To_Dir = dir

    def Save_Raw(self):
        pass

    def resizeEvent(self, event):
        #self.Adjust_Point()
        #QFrame.resizeEvent(event)
        pass