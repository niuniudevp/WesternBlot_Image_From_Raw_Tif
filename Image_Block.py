from PyQt5.QtWidgets import QScrollArea, QFrame, QLabel, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt
from Base import Img
from Utils import Get_Pressed_Key, mapped_points_with_scale_factor


class MyScrollArea(QScrollArea):

    Changed_Signal = pyqtSignal(list)

    def __init__(self, *args, **kwargs):
        QScrollArea.__init__(self, *args, **kwargs)
        self.Scale_Factor = 1
        self.horizontalScrollBar().valueChanged.connect(self.Send_Signal)
        self.verticalScrollBar().valueChanged.connect(self.Send_Signal)

    def __str__(self):
        return ("Scroll_" + self.widget().Action_Type)

    def wheelEvent(self, event):
        print(">>>SSS whelled")
        PressedBtn = Get_Pressed_Key(self)
        p1, p2 = event.x(), event.y()
        if PressedBtn and PressedBtn == Qt.Key_Control:
            print("Contrled")
            driction_v = -0.05 if event.angleDelta().y() < 0 else 0.05
            New_Scale_Factor = self.Scale_Factor + driction_v
            if New_Scale_Factor < 0.2:
                New_Scale_Factor = 0.2
            if New_Scale_Factor > 4:
                New_Scale_Factor = 4
            wid = self.widget()
            x, y, w, h = wid.x(), wid.y(), wid.width(), wid.height()
            # #P1,P2映射在widget上的位置
            p1_w, p2_w = p1 - x, p2 - y
            # #经过坐标转换后的新的位置
            p1_n, p2_n, w_n, h_n = mapped_points_with_scale_factor(
                [p1_w, p2_w, w, h], New_Scale_Factor / self.Scale_Factor)
            wid.resize(w_n, h_n)
            # #把p点调整到原来的坐标出
            wid_dx = p1 - p1_n
            wid_dy = p2 - p2_n
            self.horizontalScrollBar().setSliderPosition(-wid_dx)
            self.verticalScrollBar().setSliderPosition(-wid_dy)
            self.Scale_Factor = New_Scale_Factor
        else:
            QScrollArea.wheelEvent(self, event)

    def Send_Signal(self):
        print(str(self) + " Send signal")
        self.Changed_Signal.emit([self])

    @pyqtSlot(list)
    def MyScroollSync_From(self, src):
        src = src[0]
        print("Do Scroll Syncling to " + self.parentWidget().Img.Action_Type)
        w_w, w_h = src.widget().width(), src.widget().height()
        print(str(self) + " resized a widgets")
        self.widget().resize(w_w, w_h)

        self.horizontalScrollBar().setMaximum(
            src.horizontalScrollBar().maximum())
        self.horizontalScrollBar().setSliderPosition(
            src.horizontalScrollBar().sliderPosition())
        self.verticalScrollBar().setMaximum(src.verticalScrollBar().maximum())
        self.verticalScrollBar().setSliderPosition(
            src.verticalScrollBar().sliderPosition())
        self.Scale_Factor = src.Scale_Factor


class LabeledImg(QFrame):
    """
    给Img添加上标签
    """
    # 定义信号
    Syncing = pyqtSignal(list)

    def __init__(self, Filename, *args, **kwargs):
        QFrame.__init__(self, *args, **kwargs)
        # self.setMouseTracking(True)
        self.FileName = Filename
        self.Img = Img(self.FileName, self)
        self.Label = QLabel(self.FileName, self)
        self.Label.setWordWrap(True)
        self.scoller = MyScrollArea(self)
        self.scoller.setWidget(self.Img)
        self.scoller.setWidgetResizable(False)

        self.scoller.Changed_Signal.connect(
            self.Img.H_Refer_Line.Update_Appearance)
        self.scoller.Changed_Signal.connect(
            self.Img.V_Refer_Line.Update_Appearance)
        self.scoller.Changed_Signal.connect(self.Send_Sync_info)

        self.Img.Changed_Signal.connect(self.Send_Sync_info)

        self.Label.setAlignment(Qt.AlignHCenter)
        #self.Label.setMaximumHeight(30)
        hv = QVBoxLayout(self)
        hv.addWidget(self.Label)
        hv.addWidget(self.scoller)

    def Send_Sync_info(self):
        print(self.FileName + " LabeledImg Send Signal")
        print(self.sender())
        self.Syncing.emit([self])

    @pyqtSlot(list)
    def LabeledImg_Sync(self, LI):
        LI = LI[0]
        #LI = LabeledImg()
        print(self.Img.Action_Type + " 同步scoller")
        self.scoller.MyScroollSync_From([LI.scoller])
        print(self.Img.Action_Type + "# 同步Img")
        self.Img.ImgSync_From([LI.Img])
        print("End Syncing")


class Img_Block(QFrame):
    """
    Assign two picture
    同步两个图片的设置情况
    """
    def __init__(self, Img_list, *args, **kwargs):
        QFrame.__init__(self, *args, **kwargs)
        hv = QHBoxLayout(self)
        self.Imgs = Img_list
        WB = Img_list[0]
        BG = Img_list[1]
        self.WB = LabeledImg(WB, self)
        self.BG = LabeledImg(BG, self)
        self.BG.Img.Action_Type = "BKGD"
        self.BG.Img.Allowed_Indicator_Num = 5
        hv.addWidget(self.WB)
        hv.addWidget(self.BG)
        self.layout = hv
        self.Single_Connect()

    def Single_Connect(self):
        # #连接LabeledImg图片
        self.WB.Syncing.connect(self.BG.LabeledImg_Sync)
        self.BG.Syncing.connect(self.WB.LabeledImg_Sync)
        # 连接Img的Indicators
        self.WB.Img.Indicator_Add.connect(
            self.BG.Img.Connection_SRC_Indicator_to_Temp)
        self.BG.Img.Indicator_Add.connect(
            self.WB.Img.Connection_SRC_Indicator_to_Temp)

    def Sync_from_toobar(self, Tb):
        print("Syncing from Toolbar")
        x, y, w, h = Tb.Crop.Input_x.Value(), Tb.Crop.Input_y.Value(
        ), Tb.Crop.Input_w.Value(), Tb.Crop.Input_h.Value()
        mw, mh = Tb.Marker.Input_w.Value(), Tb.Marker.Input_h.Value()
        Angle = Tb.Rotation.Value()
        Flip_H = Tb.Flip_H.isChecked()
        Flip_V = Tb.Flip_V.isChecked()
        Scale_Factor = self.WB.Img.Scale_Factor
        self.WB.Img.Display_Img(Scale_Factor, Angle, Flip_H, Flip_V)
        self.BG.Img.Display_Img(Scale_Factor, Angle, Flip_H, Flip_V)

        for i in self.WB.Img.Indicator:
            i.Set_Acture_Pos(x, y, w, h)
        for i in self.BG.Img.Indicator:
            i.Set_Acture_Size(mw, mh)

    def Pack_Info(self):
        """
        封装Img信息以供传递
        返回  dict
        """
        info = {}
        info['filename'] = self.WB.Img.FileName
        info['rotation'] = self.WB.Img.Angle
        info['Flip_h'] = self.WB.Img.Flip_H
        info['Flip_v'] = self.WB.Img.Flip_V
        info['crop'] = []
        info['markers'] = []
        crops = [i for i in self.WB.Img.Indicator if i.isVisible()] # 确保只有可见的Indicator
        markers = [i for i in self.BG.Img.Indicator if i.isVisible()] # 确保只有可见的Indicator
        for i in crops:
            info['crop'].append({'name': i.Name.text(), 'pos': i.Acture_Pos()})
        for i in markers:
            info['markers'].append({
                'name': i.Name.text(),
                'pos': i.Acture_Pos()
            })
        info['src_img'] = self.WB.Img.Src_Img
        return info

    def mousePressEvent(self, event):
        print("Img_Box is clicked")
