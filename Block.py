# 各种自定义Widgets
from PyQt5.QtWidgets import QMainWindow, QDockWidget, QTreeView, QMenu, QAction, QTreeWidget, QListWidget, QAbstractItemView, QTreeWidgetItem, QDirModel, QPushButton, QFrame, QLineEdit, QLabel, QCheckBox, QHBoxLayout, QGridLayout, QVBoxLayout, QScrollArea,QFileDialog , QInputDialog
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QRect, QRectF, QSize, QDir
from PyQt5.QtGui import QFont, QPainter, QColor, QPen, QImage, QCursor, QGuiApplication
from Utils import *
import cv2
import time


class LabeledInPut(QFrame):
    Listen_KEY = Qt.Key_Shift
    Changed_Signal = pyqtSignal()

    def __init__(self, label, value, *args, **kwargs):
        QFrame.__init__(self, *args, **kwargs)
        self.Label = QLabel(self)
        self.Label.setText(label)
        self.Input = QLineEdit(self)
        self.Input.setText(str(value))
        self.Layout = QGridLayout(self)
        self.Layout.addWidget(self.Label, 0, 0)
        self.Layout.addWidget(self.Input, 0, 1)
        self.setLayout(self.Layout)
        self.Value = self.__get_value
        self.Text = self.Input.text
        self.SetText = self.__set_value
        self.Caption = self.Label.text
        self.Set_Caption = self.__set_caption
        self.PressedKey = None
        self.Mini_value = 0
        self.style_set()
        self.Input.textEdited.connect(self.Send_Signal)

    def Set_Mini_value(self, Value):
        self.Mini_value = Value

    def Set_Max_value(self, Value):
        self.Max_value = Value

    def style_set(self):
        self.Layout.setSpacing(0)
        self.Layout.setContentsMargins(2, 0, 0, 0)
        self.Layout.setColumnStretch(1, 3)
        self.Layout.setAlignment(Qt.AlignRight)

    def Send_Signal(self, event):

        print(self.Label.text() + " Send_TextEditor_signal!")
        print(self.sender())
        self.Changed_Signal.emit()

    def __get_value(self):
        '''
        获取input的value
        '''
        try:
            v = float(self.Input.text())
        except ValueError:
            v = 0
        return v

    def __set_caption(self, Caption):
        '''
        设置显示的Label文本
        '''
        self.Label.setText(Caption)

    def __set_value(self, value):

        if 'Mini_value' in self.__dict__.keys():
            value = self.Mini_value if value < self.Mini_value else value
        if 'Max_value' in self.__dict__.keys():
            value = self.Max_value if value > self.Max_value else value
        self.Input.setText(str(value))

    def keyPressEvent(self, event):
        self.PressedKey = event.key()
        QFrame.keyPressEvent(self, event)

    def keyReleaseEvent(self, event):
        self.PressedKey = None
        QFrame.keyReleaseEvent(self, event)

    def wheelEvent(self, event):
        s = self.Value()
        if s is not None:
            # s是数字的时候
            v = self.Text()
            S_is_Int = True if str(s).split('.')[0] == v.strip() else False
            # 没有按下shift时按照2%改变
            if S_is_Int:
                change_rate = 5 if self.PressedKey == self.Listen_KEY and S_is_Int else 1
            else:
                change_rate = 0.5 if self.PressedKey == self.Listen_KEY and S_is_Int else 0.2
            # 如果同时按下了shift键就按照乘法改变
            driction = 1 if event.angleDelta().y() > 0 else -1
            s = s + change_rate * driction
            s = int(round(s)) if S_is_Int else round(s, 3)
            self.SetText(s)
            print(self.Label.text() + "Send_wheelEvent signal!")
            print(self.sender())
            self.Changed_Signal.emit()


class Box(QFrame):

    Changed_Signal = pyqtSignal()

    def __init__(self, label, paras_labels, *args, **kwargs):

        QFrame.__init__(self, *args, **kwargs)
        Gd = QGridLayout(self)
        self.Label = QLabel(label, self)
        paras_labels = list(paras_labels)
        Gd.addWidget(self.Label, 0, 0, 2, 1)
        for i in paras_labels:
            self.__dict__.update({"Input_" + i: LabeledInPut(i, 10, self)})
        lt = len(paras_labels)
        col = lt // 2 + 1 if lt % 2 else lt // 2
        col = col + 1
        for col in range(1, col):
            for row in range(0, 2):
                try:
                    s = paras_labels.pop(0)
                    l = eval("self.Input_" + s)
                    Gd.addWidget(l, row, col)
                except IndexError:
                    print("Nothong")
        self.setLayout(Gd)
        self.Layout = Gd
        self.style_set()
        self.Signal_connection()

    def style_set(self):
        self.Layout.setSpacing(0)
        self.Layout.setContentsMargins(2, 0, 0, 0)
        # self.setStyleSheet("border: 1px solid red")

    def Signal_connection(self):
        for i in self.findChildren(LabeledInPut):
            i.Changed_Signal.connect(self.Send_Signal)

    def Send_Signal(self):
        print(self.Label.text() + "[Box] Send_Changed_Signal1")
        print(self.sender())
        self.Changed_Signal.emit()


class ToolBar(QFrame):

    Changed = pyqtSignal()

    def __init__(self, *args, **kwargs):
        QFrame.__init__(self, *args, **kwargs)
        self.Init_UI()

    def Init_UI(self):
        self.Rotation = LabeledInPut('Rotation:', 0.00, self)
        self.Rotation.Set_Mini_value(-90)
        self.Rotation.Set_Max_value(90)
        self.Flip_H = QCheckBox('Flap_H', self)
        self.Flip_V = QCheckBox('Flap_V', self)
        self.Crop = Box('Crop: ', 'xywh', self)
        self.Marker = Box('Marker: ', 'wh', self)
        self.Marker.Input_w.SetText(50)
        self.Marker.Input_h.SetText(20)
        self.Hv = QGridLayout(self)
        self.blk = QLabel('', self)
        v = QVBoxLayout()
        v.addWidget(self.Flip_H)
        v.addWidget(self.Flip_V)
        self.Hv.addWidget(self.Rotation, 0, 1)
        self.Hv.addLayout(v, 0, 2)
        self.Hv.addWidget(self.Crop, 0, 3)
        self.Hv.addWidget(self.blk, 0, 4)
        self.Hv.addWidget(self.Marker, 0, 5)
        self.Hv.setColumnStretch(4, 2)
        self.setLayout(self.Hv)
        self.Signal_connection()

    def Signal_connection(self):
        self.Rotation.Changed_Signal.connect(self.Toolbar_Send_Signal)
        self.Flip_H.stateChanged.connect(self.Toolbar_Send_Signal)
        self.Flip_V.stateChanged.connect(self.Toolbar_Send_Signal)
        self.Crop.Changed_Signal.connect(self.Toolbar_Send_Signal)
        self.Marker.Changed_Signal.connect(self.Toolbar_Send_Signal)

    def Toolbar_Send_Signal(self):
        print("Toolbar send signal!")
        print(self.sender())
        self.Changed.emit()

    # 从Img_Block进行同步
    @pyqtSlot(list)
    def Toolbar_Sync_From_Img_Block(self, Imgb):
        print("Toolbar Syncing from ImgB")
        Imgb = Imgb[0]
        #Imgb = Img_Block()
        self.Rotation.SetText(Imgb.WB.Img.Angle)
        if len(Imgb.WB.Img.Indicator) > 0:
            t = Imgb.WB.Img.Indicator[0]
            if t.isVisible():
                x, y, w, h = t.Acture_Pos()
            else:
                x, y, w, h = 0, 0, 0, 0
            self.Crop.Input_x.SetText(x)
            self.Crop.Input_y.SetText(y)
            self.Crop.Input_w.SetText(w)
            self.Crop.Input_h.SetText(h)


class Reference_Line(QFrame):
    """
    竖直和水平参考线
    """
    Moved_Signal = pyqtSignal(list)

    def __init__(self, Type, Position, *args, **kwargs):
        """
        Type:参考线的类型 H:水平,V:竖直
        Position:添加的位置 H的时候是y位置,V的时候是x的位置
        """
        QFrame.__init__(self, *args, **kwargs)
        self.Type = Type
        self.Color = 'green'
        self.Position = Position
        self.Label = MyLabel(self.Type, self)
        self.Label.Can_Move_with_Mouse = True
        self.Label.Anchor_In_Parent = True
        self.Line = QFrame(self)
        self.Update_Appearance()
        self.id = ""

    def Update_Appearance(self):
        try:
            factor = self.parentWidget().Scale_Factor
        except:
            factor = 1
        self.P_Factor = factor
        self.Label.setStyleSheet("color:white;background:" + self.Color)
        self.Label.setMinimumSize(50, 20)
        self.Label.setAlignment(Qt.AlignHCenter)
        P = self.parentWidget()
        if self.Type == "H":
            self.resize(P.width(), self.height())
            self.Line.setStyleSheet("border: 2px solid " + self.Color)
            self.Line.resize(P.width(), 1)
            self.move(-P.x(), int(round(self.Position * factor)))

        if self.Type == "V":
            self.resize(self.width(), P.height())
            self.Line.setStyleSheet("color:white;border: 2px solid " +
                                    self.Color)
            self.Line.resize(1, P.height())
            self.move(int(round(self.Position * factor)), -P.y())
        #print(self.Type + " Reference Line Send Move Signal")
        print(self.sender())
        self.Moved_Signal.emit([self.x(), self.y()])

    @pyqtSlot(list)
    def Refer_Sync_From_Point(self, p):
        print(self.id + " Syncing from Point " + str(p))
        self.move(p[0], p[1])

    def moveEvent(self, event):
        if self.Type == "H":
            self.Position = int(round(self.y() / self.P_Factor))
        if self.Type == "V":
            self.Position = int(round(self.x() / self.P_Factor))
        #print(self.id + " Refernce moveevent! Send " +
        #     str([self.x(), self.y()]))
        if self.hasFocus():
            print(self.Type + " Reference_Line Send Move Signal")
            print(self.sender())
            self.Moved_Signal.emit([self.x(), self.y()])

    def resizeEvents(self, event):
        #print(self.id + " Refernce resizeevent! Send " +
        #    str([self.x(), self.y()]))
        print(self.Type + " Reference_Line Send resize Signal")
        print(self.sender())
        self.Moved_Signal.emit([self.x(), self.y()])


class MyLabel(QLabel):
    """
    # 重写QLabel
    可以鼠标move,可以鼠标调整大小,可以Arrow move
    左键激活,邮件取消激活
    """
    Changed_Signal = pyqtSignal(list)

    def __init__(self, *args, **kwargs):
        QLabel.__init__(self, *args, **kwargs)
        # 定义功能块
        self.setMouseTracking(True)
        self.Can_Move_with_Mouse = False  # 可以使用鼠标
        self.Only_Move_H = False  # 仅仅可以沿着X移动
        self.Only_Move_V = False  # 仅仅可以沿着y移动
        self.Can_move_with_Arrow_Key = False  # 可以使用键盘上下左右移动
        self.Can_Adjust_Edge = False  # 可以通过鼠标调整边缘
        self.Can_Set_Cursor = False  # 可以设置鼠标形状
        self.Can_Action_Change_Style = False  # 可以根据动作改变Style
        self.Anchor_In_Parent = False  # 设置是否在父控件中相对固定,即移动父控件
        self.Listen_Key = []  # 监听的Key
        self.Mouse_Press_Btn = None
        self.Scale_Factor = 1
        self.clearFocus()
        print("Label send init Signal")
        print(self.sender())
        #self.Changed_Signal.emit([self])

    def Scaled(self, Scale_Factor):
        """
        自身的缩放功能
        """
        print(self.Acture_Pos())
        x, y, w, h = mapped_points_with_scale_factor(
            [self.x(), self.y(),
             self.width(), self.height()], Scale_Factor / self.Scale_Factor)
        self.setGeometry(x, y, w, h)
        self.Scale_Factor = Scale_Factor
        print(self.Acture_Pos())

    def Acture_Pos(self):
        """
        返回真实的大小和在图片上的坐标
        x,y,w,h= Acture_Pos
        """
        x, y, w, h = mapped_points_with_scale_factor(
            [self.x(), self.y(),
             self.width(), self.height()], 1 / self.Scale_Factor)
        return (x, y, w, h)

    def Set_Acture_Pos(self, x, y, w, h):
        x, y, w, h = mapped_points_with_scale_factor([x, y, w, h],
                                                     self.Scale_Factor)
        self.setGeometry(x, y, w, h)

    def Set_Acture_Size(self, w, h):
        n_w, n_h = mapped_points_with_scale_factor([w, h], self.Scale_Factor)
        ###Keep Centered
        x, y, w, h = self.x(), self.y(), self.width(), self.height()
        n_x = x + (w - n_w) / 2
        n_y = y + (h - n_h) / 2
        self.setGeometry(n_x, n_y, n_w, n_h)

    def mousePressEvent(self, event):

        btn, (x, y) = Get_Mouse_Parameter(event)
        # print("Mouse_Pressed "+btn)
        self.Mouse_Press_Point = (x, y)
        self.Mouse_Press_Btn = btn
        if self.Can_move_with_Arrow_Key and not self.hasFocus():
            # pass
            # self.OldStyle=self.styleSheet()
            self.setFocus()
            # self.setStyleSheet("border:2px solid green")

        if self.Can_Adjust_Edge:
            L, T, R, B = Get_Mouse_Edge_Status(self, (x, y))
            if self.Can_Move_with_Mouse:
                Set_Mouse_Cursor(self, [L, T, R, B], Qt.ClosedHandCursor)
            else:
                Set_Mouse_Cursor(self, [L, T, R, B], Qt.ArrowCursor)
        else:
            if self.Can_Move_with_Mouse:
                self.setCursor(Qt.ClosedHandCursor)
        # QLabel.mousePressEvent(self,event)

    def mouseMoveEvent(self, event):
        _, (x, y) = Get_Mouse_Parameter(event)
        # print("" + "Mouse_Moved")
        L, T, R, B = Get_Mouse_Edge_Status(self, (x, y))
        # 左键移动

        if self.Mouse_Press_Btn == "LEFT":
            move_x = x - self.Mouse_Press_Point[0]
            move_y = y - self.Mouse_Press_Point[1]
            if self.Only_Move_V:
                move_x = 0
                self.Can_Adjust_Edge = False
            if self.Only_Move_H:
                move_y = 0
                self.Can_Adjust_Edge = False

        if self.Can_Adjust_Edge:

            def Edge_Action(x, y):
                if sum([L, T, R, B]):
                    # 边缘Move
                    ori_w = self.width()
                    ori_h = self.height()
                    loc_x = self.x()
                    loc_y = self.y()

                    if L:
                        # x改变,y不变,w改变,h不变
                        fixed_p = (loc_x + ori_w, loc_y + ori_h)
                        TL = (loc_x + move_x, loc_y)
                        x, y, w, h = Rect_From_Two_Point(TL, fixed_p)
                    if T:
                        # x不变,y变,w不变,h变
                        fixed_p = (loc_x + ori_w, loc_y + ori_h)
                        TL = (loc_x, loc_y + move_y)
                        x, y, w, h = Rect_From_Two_Point(TL, fixed_p)
                    if R:
                        # x不变,y不变,w改变,h不变
                        p_l_distance = x - ori_w
                        fixed_p = (loc_x, loc_y)
                        TL = (loc_x + x, loc_y + ori_h)
                        x, y, w, h = Rect_From_Two_Point(TL, fixed_p)
                    if B:
                        # x不变,y不变,w不变,h变
                        p_l_distance = ori_h - y
                        fixed_p = (loc_x, loc_y)
                        TL = (loc_x + ori_w, y + loc_y)
                        x, y, w, h = Rect_From_Two_Point(TL, fixed_p)
                    self.setGeometry(x, y, w, h)

            if self.Can_Move_with_Mouse:
                if self.Mouse_Press_Btn == "LEFT":
                    Set_Mouse_Cursor(self, [L, T, R, B], Qt.ClosedHandCursor)
                    if sum([L, T, R, B]):
                        Edge_Action(x, y)
                    else:
                        if self.Anchor_In_Parent:
                            p = self.parentWidget()
                            p.move(p.x() + move_x, p.y() + move_y)
                        else:
                            self.move(self.x() + move_x, self.y() + move_y)
                else:
                    Set_Mouse_Cursor(self, [L, T, R, B], Qt.SizeAllCursor)
            else:
                Set_Mouse_Cursor(self, [L, T, R, B], Qt.ArrowCursor)
                if self.Mouse_Press_Btn == "LEFT":
                    Edge_Action(x, y)
        else:
            if self.Can_Move_with_Mouse:
                self.setCursor(Qt.SizeAllCursor)
                if self.Mouse_Press_Btn == "LEFT":
                    if self.Anchor_In_Parent:
                        p = self.parentWidget()
                        p.move(p.x() + move_x, p.y() + move_y)
                    else:
                        self.move(self.x() + move_x, self.y() + move_y)
            else:
                self.setCursor(Qt.ArrowCursor)
        # QLabel.mouseMoveEvent(self,event)

    def mouseReleaseEvent(self, event):
        # print("Mouse_Released")
        btn, (x, y) = Get_Mouse_Parameter(event)
        self.Mouse_Release_Point = (x, y)
        self.Mouse_Release_Btn = btn
        self.Mouse_Press_Btn = None
        self.setCursor(Qt.ArrowCursor)

        if self.Can_move_with_Arrow_Key and btn == "RIGHT":
            # self.clearFocus()
            pass
        QLabel.mouseReleaseEvent(self, event)

    def keyPressEvent(self, event):
        # print("Key_Pressed")
        self.PressedKey = event.key()
        # 如果监听键盘移动事件
        if self.Can_move_with_Arrow_Key:
            Action_keys = [Qt.Key_Right, Qt.Key_Left, Qt.Key_Up, Qt.Key_Down]
            Action = [[1, 0], [-1, 0], [0, -1], [0, 1]]
            if self.Only_Move_H:
                Action[2:4] = [[0, 0], [0, 0]]
            if self.Only_Move_V:
                Action[0:2] = [[0, 0], [0, 0]]
            if self.PressedKey in Action_keys:
                K_ind = Action_keys.index(self.PressedKey)
                dx, dy = Action[K_ind]
                self.move(self.x() + dx, self.y() + dy)
        event.accept()
        #QLabel.keyPressEvent(self, event)

    def keyReleaseEvent(self, event):
        # print("KeyReleased!")
        self.PressedKey = None
        if event.key() == Qt.Key_Delete:
            self.setVisible(False)
            ###删除时也发出change信号
            print("MyLabel send delete Signal")
            print(self.sender())
            self.Changed_Signal.emit([self])
        QLabel.keyReleaseEvent(self, event)

    def focusInEvent(self, event):
        # print("Focus In")
        self.OldStyle = self.styleSheet()
        self.setStyleSheet("border:2px solid green")
        QLabel.focusInEvent(self, event)

    def focusOutEvent(self, event):
        # print("Focus Out")
        self.setStyleSheet(self.OldStyle)
        QLabel.focusOutEvent(self, event)

    def moveEvent(self, event):
        print(str(self) + " send Move Signal")
        self.Changed_Signal.emit([self])
        QLabel.moveEvent(self, event)

    def resizeEvent(self, event):
        print(str(self) + " send resize signal")
        self.Changed_Signal.emit([self])
        QLabel.resizeEvent(self, event)

    def showEvent(self, event):
        print("show event of %s" % self)
        self.Changed_Signal.emit([self])
        QLabel.showEvent(self, event)

    @pyqtSlot(list)
    def Sync_From(self, src):
        src = src[0]
        x, y, w, h = src.x(), src.y(), src.width(), src.height()
        self.setGeometry(x, y, w, h)
        self.setVisible(src.isVisible())


class Indicator(MyLabel):
    def __init__(self, Type, *args, **kwargs):
        MyLabel.__init__(self, *args, **kwargs)
        self.Can_Move_with_Mouse = True
        self.Can_move_with_Arrow_Key = True
        if Type == "WB":
            self.Can_Adjust_Edge = True
        self.Type = Type
        self.show()
        self.Name = QLabel(self.parentWidget())
        self.Changed_Signal.connect(self.Attach_Name_Label)

    def mouseDoubleClickEvent(self, event):
        if self.hasFocus():
            text, okPressed = QInputDialog.getText(None, "Add Name",
                                                   "Input a name:",
                                                   QLineEdit.Normal,
                                                   self.Name.text())
            if okPressed:
                self.Name.setText(text)
                self.Name.show()
                self.Attach_Name_Label()
                print("%s Send text change Signal" % self)
                self.Changed_Signal.emit([self])

    # 铆定Label
    def Attach_Name_Label(self):
        if self.Name.isVisible():
            x, y, w = self.x(), self.y(), self.width()
            self.Name.setStyleSheet("color:white;background:blue")
            self.Name.move(x + w, y)


class Img(QLabel):
    """
    自定义Img类
    """
    Changed_Signal = pyqtSignal(list)
    # Indicators 添加时候的动作
    Indicator_Add = pyqtSignal(list)
    # Indicator 改变时的动作
    Indicator_Change_Signal = pyqtSignal()

    Listen_KEY = Qt.Key_Control

    def __init__(self, Filename, *args, **kwargs):
        """
        Filename是要加载的文件名称
        """
        QLabel.__init__(self, *args, **kwargs)
        self.setMouseTracking(True)
        self.Action_Type = 'WB'
        self.Allowed_Indicator_Num = 1
        self.FileName = Filename
        self.Indicator = []
        self.Angle = 0
        self.Src_Img = None
        self.Img_Width = 0
        self.Img_Height = 0
        self.Displayed_Img = None
        self.Scale_Factor = 1.0
        self.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.Pressed_Mouse = None
        self.Mouse_Press_Loc = []
        self.H_Refer_Line = Reference_Line("H", 924, self)
        self.H_Refer_Line.Label.Only_Move_V = True
        self.V_Refer_Line = Reference_Line("V", 300, self)
        self.V_Refer_Line.Label.Only_Move_H = True
        self.Temp_Indicator = []
        self.Indicator_Add.connect(self.Link_Indicator_Add_to_Change)

        self.__Init_UI(Filename)

    def __Init_UI(self, Filename):
        self.__Load_Img(Filename)
        self.Display_Img()
        # self.setStyleSheet("border: 2px solid red")

    def __Load_Img(self, Filename):
        Cv_Img = cv2.imread(Filename)
        self.Src_Img = Cv_Img

    def Display_Img(self, Scale_Factor=1, Angle=0, Flap_H=False, Flap_V=False):
        CV_Img = self.Src_Img
        QPix, (width, height) = CV_Img_to_QImage(CV_Img, Scale_Factor, Angle,
                                                 Flap_H, Flap_V)
        self.Scale_Factor = Scale_Factor
        self.Angle = Angle
        self.Img_Width = width
        self.Img_Height = height
        self.Flap_H = Flap_H
        self.Flap_V = Flap_V
        self.setPixmap(QPix)
        self.Displayed_Img = QPix
        # Scale Factor 改变的时候也要更新参考线
        self.H_Refer_Line.Update_Appearance()
        self.V_Refer_Line.Update_Appearance()

    def mousePressEvent(self, event):
        btn, (x, y) = Get_Mouse_Parameter(event)
        self.Pressed_Mouse = btn
        self.Mouse_Press_Loc = (x, y)
        self.setFocus()

        if btn == "LEFT" and self.Action_Type == 'WB':
            print("WB_LEFT")
            if self.Indicator:
                indicator = self.Indicator[0]
                if not indicator.isVisible():
                    indicator.setGeometry(x, y, 0, 0)
                    indicator.setVisible(True)
                    indicator.Scale_Factor = self.Scale_Factor
            else:
                # 需要新建
                indicator = Indicator("WB", self)
                indicator.Scale_Factor = self.Scale_Factor
                self.Indicator.append(indicator)
                print(self.Action_Type + " 新建 Indicator 发送信号!")
                self.Indicator_Add.emit(self.Indicator)

                indicator.setStyleSheet("border:2px solid red")
                indicator.setGeometry(x, y, 0, 0)

        if btn == "LEFT" and self.Action_Type == 'BKGD':
            print("BKGD_LEFT")
            indicator = None
            PressedBtn = Get_Pressed_Key(self)
            # Box是空的时候直接添加
            if not self.Indicator:
                indicator = Indicator(self.Action_Type, self)
                indicator.Scale_Factor = self.Scale_Factor
                self.Indicator.append(indicator)
                print(self.Action_Type + " 新建 Indicator 发送信号!")
                self.Indicator_Add.emit(self.Indicator)

            else:
                visible_count = sum([i.isVisible() for i in self.Indicator])
                if PressedBtn == Qt.Key_Control or visible_count == 0:
                    if 0 < len(self.Indicator) < self.Allowed_Indicator_Num:
                        # 遍历box看有没有没有用的#
                        for b in self.Indicator:
                            if not b.isVisible():
                                indicator = b
                                indicator.setVisible(True)
                                break

                        # 如果遍历后还是没有
                        if not indicator:
                            indicator = Indicator(self.Action_Type, self)
                            indicator.Scale_Factor = self.Scale_Factor
                            self.Indicator.append(indicator)
                            print(self.Action_Type + " 新建 Indicator 发送信号!")
                            self.Indicator_Add.emit(self.Indicator)

                    else:
                        print("Box is Full")
                        # indicator 依然是None
            #
            Marker_w = 70
            Marker_h = 15
            #
            if indicator:
                indicator.setVisible(True)
                indicator.setStyleSheet("border:2px solid red")
                indicator.setGeometry(x - Marker_w / 2, y - Marker_h / 2,
                                      Marker_w, Marker_h)
                indicator.Scale_Factor = self.Scale_Factor
                #print(" Img Send change indicator Signal")
                #indicator.Changed_Signal.emit()

        QLabel.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        self.show_stat_bar_info(event)
        btn, (x, y) = Get_Mouse_Parameter(event)

        # 鼠标画框
        if self.Action_Type == "WB" and self.Pressed_Mouse == "LEFT":
            indicator = self.Indicator[0]
            x, y, w, h = Rect_From_Two_Point(self.Mouse_Press_Loc, [x, y])
            indicator.setGeometry(x, y, w, h)
            #print("Img 画框 Indicator 改变 Signal")
            #indicator.Changed_Signal.emit()
        QLabel.mouseMoveEvent(self, event)

    def mouseReleaseEvent(self, event):
        btn = get_mouse_btn(event)
        self.Pressed_Mouse = None
        self.Mouse_Press_Loc = []
        QLabel.mouseReleaseEvent(self, event)

    def resizeEvent(self, event):
        New_Scale_Factor = self.width() / self.Img_Width
        for F in range(20, 405, 5):
            if abs(F - New_Scale_Factor * 100) < 2.5:
                New_Scale_Factor = F / 100
                break
        #New_Scale_Factor = round(New_Scale_Factor,2)
        print(self.Action_Type + " Resized from " + str(self.Scale_Factor) +
              " to " + str(New_Scale_Factor))
        self.Display_Img(New_Scale_Factor, self.Angle, self.Flap_H,
                         self.Flap_V)

        self.Scale_Factor = New_Scale_Factor
        # Indicator也要缩放
        for i in self.Indicator:
            i.Scaled(self.Scale_Factor)

        print(self.Action_Type + "> Img Resized and Send Changed Signal!")
        print(self.sender())
        self.Changed_Signal.emit([self])

        self.show_stat_bar_info(event)
        event.accept()
        QLabel.resizeEvent(self, event)

    def moveEvent(self, event):
        print(self.Action_Type + " Moved!")
        QLabel.moveEvent(self, event)

    def show_stat_bar_info(self, event):
        x = '-'
        y = '-'
        try:
            _, (x, y) = Get_Mouse_Parameter(event)
        except:
            pass
        mes = "Image Pointer (x:%s y:%s) |Scale: %s" % (
            str(x), str(y), str(round(self.Scale_Factor, 2)))
        t = Get_Super_Parent(self)
        t.statusbar.showMessage("Ready " + mes)

    @pyqtSlot()
    def Link_Indicator_Add_to_Change(self):
        self.Indicator[-1].Changed_Signal.connect(
            lambda: self.Indicator_Change_Signal.emit())

    @pyqtSlot()
    def Send_Signal(self):
        print(self.Action_Type + " Img Send Change Signal")
        #self.Changed_Signal.emit()

    @pyqtSlot(list)
    def Connection_SRC_Indicator_to_Temp(self, src):
        print("Indicator Connectioning From %s to %s" % (src, self))
        #Indicator 添加的时候就会触发Change事件,所以只需要判断两者的长度是否一致,不一致就连接
        #新建的Indicator和src的最后一个
        if len(src) > 0 and len(src) > len(self.Temp_Indicator):
            m = MyLabel('', self)
            print("连接新建的Indicator")
            if self.Action_Type == "WB":
                m.setStyleSheet("background:red")
            else:
                m.setStyleSheet("border:2px dashed red")
            src[-1].Changed_Signal.connect(m.Sync_From)
            self.Temp_Indicator.append(m)

    def Syncing_Indicator_to_Temp(self, src, targ):
        """
        将一方的Indicator同步到另一方的Temp_Indicator里
        """
        # 同步Indicator===>Temp_Indicator
        print("Syncing %s I-> %s T" % (src.Action_Type, targ.Action_Type))
        if len(src.Indicator) > 0:
            for i in targ.Temp_Indicator:
                i.setVisible(False)
            SS = [j for j in src.Indicator if j.isVisible()]
            for i in range(len(SS)):
                try:
                    m = targ.Temp_Indicator[i]
                except IndexError:
                    m = MyLabel('', targ)
                    targ.Temp_Indicator.append(m)

                m.setGeometry(SS[i].x(), SS[i].y(), SS[i].width(),
                              SS[i].height())
                m.Scale_Factor = SS[i].Scale_Factor
                m.show()
                # 判断当前Labeled_Img的类型
                if targ.Action_Type == "WB":  # 应该添加Marker类型的Indicator
                    m.setStyleSheet("background:red")
                if targ.Action_Type == "BKGD":  # 应该添加Box类型的Indicator
                    m.setStyleSheet("border:2px dashed red")

    @pyqtSlot(list)
    def ImgSync_From(self, src):
        src = src[0]
        print("[Img] Syncing " + self.Action_Type + " From " + src.Action_Type)
        self.Scale_Factor = src.Scale_Factor
        self.Angle = src.Angle
        print("[Img] Syncing # 同步图片")
        self.Display_Img(self.Scale_Factor, self.Angle, self.Flap_H,
                         self.Flap_V)
        #print("[Img] Syncing # 更新自身的Indicators")
        #for i in self.Indicator:
        #    i.Scaled(self.Scale_Factor)
        #print("[Img] Syncing # 同步Indicator===>Temp_Indicator")
        #self.Syncing_Indicator_to_Temp(src, self)
        #self.Syncing_Indicator_to_Temp(self, src)
        print("[Img] Syncing End")


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
        self.Label.setMaximumHeight(30)
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
        Flap_H = Tb.Flip_H.isChecked()
        Flap_V = Tb.Flip_V.isChecked()
        Scale_Factor = self.WB.Img.Scale_Factor
        self.WB.Img.Display_Img(Scale_Factor, Angle, Flap_H, Flap_V)
        self.BG.Img.Display_Img(Scale_Factor, Angle, Flap_H, Flap_V)

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
        info['Flap_h'] = self.WB.Img.Flap_H
        info['Flap_v'] = self.WB.Img.Flap_V
        info['crop'] = []
        info['markers'] = []
        crops = self.WB.Img.Indicator
        markers = self.BG.Img.Indicator
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


class PreView_Img(QScrollArea):
    def __init__(self, *args, **kwargs):
        QScrollArea.__init__(self, *args, **kwargs)
        self.View_Info = None
        self.View_Scale = 1
        self.Add_Border = True
        self.Info_L_Most = 0
        self.Info_T_Most = 0
        self.Info_R_Most = 0
        self.Info_B_Most = 0
        self.draw_text = []  #{'text':#,'font':#,'rect':#}
        self.draw_marker = []  # {'rect':#}
        self.draw_Img = []  #{'rect':#}
        self.draw_rec = []  #{'rect':#}
        self.Temp = QLabel(self)
        self.PreView_Img = None
        self.View = QLabel(self)
        self.View.setAlignment(Qt.AlignCenter)
        self.View.setScaledContents(False)
        self.setWidget(self.View)
        self.setAlignment(Qt.AlignCenter)
        self.View.setStyleSheet("border:2px solid red")

    def Load_info(self, Info):
        self.View_Info = Info
        self.Pre_set()
        self.Rearange()

    def Pre_set(self):
        if 'src_img' not in self.View_Info.keys():
            self.View_Info['src_img'] = cv2.imread(self.View_Info['filename'])

        self.Gene_Font = QFont('Arial', 20)
        self.Marker_Font = QFont('Arial', 14)

        ###单独只有一项的时候默认将文字标签放在右边
        if len(self.View_Info['crop']) > 0 and len(
                self.View_Info['markers']) > 0:
            if self.View_Info['crop'][0]['pos'][0] > self.View_Info['markers'][
                    0]['pos'][0]:
                self.Postion_Type = 1  # Marker >> Strip >> Gene
            else:
                self.Postion_Type = 2  # Gene >> Strip >> Marker
        else:
            self.Postion_Type = 0  #默认情况统一放在右边

    def Text_size(self, text, font):
        """
        获取 text设置为相应字体时候的大小
        w,h=Text_size
        """
        self.Temp.setVisible(False)
        self.Temp.setFont(font)
        self.Temp.setText(text)
        self.Temp.adjustSize()
        return self.Temp.width(), self.Temp.height()

    def Rearange(self):
        self.draw_text = []  #{'text':#,'font':#,'rect':#}
        self.draw_marker = []  # {'rect':#}
        self.draw_Img = []  #{'rect':#}
        self.draw_rec = []  #{'rect':#}
        self.Spacer = '  '
        for m in self.View_Info['markers']:
            text = m['name']
            text_w, text_h = self.Text_size(text + self.Spacer,
                                            self.Marker_Font)
            m_x, m_y, m_w, m_h = m['pos']
            if self.Postion_Type == 1:  # Marker >> Strip >> Gene
                text_pos = (m_x - text_w - 8, m_y - int(
                    (text_h - m_h) / 2), text_w, text_h)
                align = Qt.AlignRight
                text = text + self.Spacer
            else:
                text_pos = (m_x + m_w + 8, m_y - int(
                    (text_h - m_h) / 2), text_w, text_h)
                align = Qt.AlignLeft
                text = self.Spacer + text
            self.draw_text.append({
                'text': text,
                'font': self.Marker_Font,
                'rect': text_pos,
                'align': align
            })
            self.draw_marker.append({'rect': m['pos']})

        for c in self.View_Info['crop']:
            text = c['name']
            text_w, text_h = self.Text_size(text + self.Spacer, self.Gene_Font)
            m_x, m_y, m_w, m_h = c['pos']
            if self.Postion_Type == 2:  # Gene >> Strip >> Marker
                text_pos = (m_x - text_w - 8, m_y - int(
                    (text_h - m_h) / 2), text_w, text_h)
                align = Qt.AlignRight
                text = text + self.Spacer
            else:
                text_pos = (m_x + m_w + 8, m_y - int(
                    (text_h - m_h) / 2), text_w, text_h)
                align = Qt.AlignLeft
                text = self.Spacer + text
            self.draw_text.append({
                'text': text,
                'font': self.Gene_Font,
                'rect': text_pos,
                'align': align
            })
            self.draw_Img.append({'rect': c['pos']})
            self.draw_rec.append(
                {'rect': (m_x - 2, m_y - 2, m_w + 3, m_h + 3)})

        l, t, r, b = [], [], [], []
        for i in self.draw_marker + self.draw_rec + self.draw_text + self.draw_Img:
            l.append(i['rect'][0])
            t.append(i['rect'][1])
            r.append(i['rect'][0] + i['rect'][2])
            b.append(i['rect'][1] + i['rect'][3])

        self.Info_L_Most = min(l) - 5 if len(l) > 0 else 0
        self.Info_T_Most = min(t) - 5 if len(t) > 0 else 0
        self.Info_R_Most = max(r) if len(r) > 0 else 0
        self.Info_B_Most = max(b) if len(b) > 0 else 0
        self.dx = -self.Info_L_Most
        self.dy = -self.Info_T_Most

    def rect_fix(self, rect):
        x, y, w, h = rect
        return x + self.dx, y + self.dy, w, h

    def PreView(self):
        print("Patining")

        Img = QImage(
            QSize(self.Info_R_Most - self.Info_L_Most + 5,
                  self.Info_B_Most - self.Info_T_Most + 5),
            QImage.Format_ARGB32)
        Img.fill(Qt.transparent)
        # Img.fill('white')
        pt = QPainter()
        pt.begin(Img)

        # 绘制文字
        for i in self.draw_text:
            pt.setPen(QPen(QColor(0, 0, 0), 3))
            pt.setFont(i['font'])
            x, y, w, h = self.rect_fix(i['rect'])
            pt.drawText(QRectF(x, y, w, h), i['align'], i['text'])
            #pt.drawRect(QRect(x,y,w,h))

        for r in self.draw_rec:
            x, y, w, h = self.rect_fix(r['rect'])
            pt.drawRect(QRect(x, y, w, h))

        for m in self.draw_marker:
            pt.setBrush(QColor(0, 0, 0))
            x, y, w, h = self.rect_fix(m['rect'])
            pt.fillRect(x, y, w, h, QColor(0, 0, 0))

        for p in self.draw_Img:
            im, _ = CV_Img_to_QImage(self.View_Info['src_img'], 1,
                                     self.View_Info['rotation'],
                                     self.View_Info['Flap_h'],
                                     self.View_Info['Flap_v'])
            x, y, w, h = p['rect']
            im = im.copy(x, y, w, h)
            x, y, w, h = self.rect_fix(p['rect'])
            pt.drawPixmap(x, y, im)
        pt.end()
        return Img

    @pyqtSlot(list)
    def Sync_From(self, Imgb):
        Img = Imgb[0]
        info = Img.Pack_Info()
        self.Load_info(info)
        Img = self.PreView()
        self.View.setPixmap(QPixmap.fromImage(Img))
        #print(self.PreView_Img.size())
        self.View.adjustSize()


class Img_Block_Pre(QFrame):
    """
    将Img Block 和PreView_Img
    合并起来
    """
    def __init__(self, Img_list, *args, **kwargs):
        QFrame.__init__(self, *args, **kwargs)
        # Img_Block
        self.ImgB = Img_Block(Img_list, self)
        # Preview
        self.Pre = PreView_Img(self)
        self.init_UI()
        self.Signal_Connection()

    def init_UI(self):
        Gd = QGridLayout(self)
        Gd.addWidget(self.ImgB, 0, 0)
        Gd.addWidget(self.Pre, 1, 0)
        Gd.setRowStretch(0, 4)
        Gd.setRowStretch(1, 2)
        self.setLayout(Gd)

    def Signal_Connection(self):
        UI = Get_Super_Parent(self)
        self.ImgB.WB.Img.Changed_Signal.connect(
            lambda: self.Pre.Sync_From([self.ImgB]))
        self.ImgB.WB.Img.Indicator_Change_Signal.connect(UI.Syncing_Imgb_to_Tb)
        self.ImgB.WB.Img.Indicator_Change_Signal.connect(
            lambda: self.Pre.Sync_From([self.ImgB]))
        self.ImgB.BG.Img.Indicator_Change_Signal.connect(
            lambda: self.Pre.Sync_From([self.ImgB]))

"""
class My_Tree_View(QFrame):
    def __init__(self, *args, **kwargs):
        QFrame.__init__(self, *args, **kwargs)
        self.Current_Path = QDir.home().absolutePath()
        self.Path_Input = QLineEdit(self)
        self.Go_Btn = QPushButton('Go', self)
        self.Go_Btn.clicked.connect(self.Change_Dir)
        
        self.Tree.setAnimated(True)
        self.Tree.setSortingEnabled(True)
        self.Tree.setAlternatingRowColors(True)
        Gd = QGridLayout(self)
        Gd.addWidget(self.Path_Input, 0, 0)
        self.Path_Input.setMaximumHeight(50)
        Gd.addWidget(self.Go_Btn, 0, 1)
        self.Go_Btn.setMaximumHeight(50)
        Gd.addWidget(self.Tree, 1, 0, 0, 2)
        Gd.setRowStretch(1, 10)
        self.setLayout(Gd)
        self.setStyleSheet("border: 2px solid red")

    def Change_Dir(self):
        self.Current_Path = self.Path_Input.text()
        self.Tree.setRootIndex(self.model.index(self.Current_Path))

    def resizeEvent(self, event):
        #self.Tree.resize(self.Tree.width(), self.height()-50)
        QFrame.resizeEvent(self, event)
"""

class My_TreeItem(QTreeWidgetItem):
    """
    自定义TreeWidgetItem, 添加右键菜单项目
    """
    def __init__(self, *args, **kwargs):
        QTreeWidgetItem.__init__(self, *args, **kwargs)
        self.Type = 'WB'
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
        self.init_ui(self.img_dict)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.Tree)
        self.setLayout(self.layout)
        

    def init_ui(self, img_dict):
        if img_dict:
            for img in img_dict:
                c = My_TreeItem()
                c.setText(0, img['wb'])
                # 设置不可以被Drop
                c.setFlags(c.flags() & ~Qt.ItemIsDropEnabled)
                c.act_delete.triggered.connect(self.menu_delete)
                c.act_change.triggered.connect(self.menu_change)

                cc = My_TreeItem(c)
                cc.Type = 'BKGD'
                cc.act_change.triggered.connect(self.menu_change)
                cc.setText(0, img['bkgd'])
                # 设置不可以被Drop
                cc.setFlags(cc.flags() & ~Qt.ItemIsDropEnabled)
                # 设置不可以被Drag
                cc.setFlags(cc.flags() & ~ Qt.ItemIsDragEnabled)
                self.Tree.addTopLevelItem(c)
                self.imgs.append(c)

    def enable_bottom_btn(self, bool):
        if bool:
            self.Add_Btn = QPushButton('Add New', self)
            self.Add_Btn.clicked.connect(Broswer_Img(self).show)
            self.layout.addWidget(self.Add_Btn)
        
    
    def enable_contextmenu(self, bool):
        if bool:
            self.Tree.itemPressed.connect(self.show_menu)



    @pyqtSlot(list)
    def update_img_list(self, new_img_list):
        self.Tree.clear()
        self.init_ui(new_img_list)

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


class Broswer_Img(QMainWindow):
    """
    选择图片文件并且预览，自动匹配多图的情况和背景图片
    """
    def __init__(self, *args, **kwargs):
        QMainWindow.__init__(self, *args, **kwargs)
        self.Current_Dir = QDir.home().absolutePath()
        self.setWindowTitle("Select Imags")
        self.setWindowModality(Qt.ApplicationModal)
        self.Left_Dock_Code()
        self.Central_Frame_Code()
        self.Right_Dock_Code()
        self.setGeometry(200, 200, 800, 500)
    
    def Left_Dock_Code(self):
        self.Left_Frame = QFrame(self)
        self.Model = QDirModel(self)
        self.Model.setSorting(QDir.DirsFirst | QDir.IgnoreCase | QDir.Name)
        self.Model.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs
                             | QDir.AllEntries)
        self.Tree = QTreeView(self.Left_Frame)
        self.Tree.setModel(self.Model)
        self.Tree.setRootIndex(self.Model.index(self.Current_Dir))
        #self.Tree.expandAll()
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
        self.wb_label.setMaximumHeight(30)
        
        self.wb = QLabel(self.Central_Frame)
        self.bkgd = QLabel(self.Central_Frame)
        
        self.navigator = QFrame(self.Central_Frame)
        self.nav_left = QPushButton(self.navigator)
        self.nav_right = QPushButton(self.navigator)
        nav_layout = QHBoxLayout()
        nav_layout.addWidget(self.nav_left)
        nav_layout.addWidget(self.nav_right)
        self.navigator.setLayout(nav_layout)
        self.navigator.setMaximumHeight(40)

        self.btns = QFrame(self.Central_Frame)
        self.btns.setMaximumHeight(40)
        self.Btn_Add = QPushButton(self.btns)
        self.Btn_Close = QPushButton(self.btns)
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.Btn_Add)
        btn_layout.addWidget(self.Btn_Close)
        self.btns.setLayout(btn_layout)

        # 根据具体的传入参数构建不同的视图
        layout.addWidget(self.wb_label, 0, 0)
        layout.addWidget(self.bkgd_label, 0, 1)
        
        layout.addWidget(self.wb, 1, 0)
        layout.addWidget(self.bkgd, 1, 1)
        
        layout.addWidget(self.navigator, 2, 0)
        
        layout.addWidget(self.btns, 3, 0, 2, 0)
        layouts = QVBoxLayout()
        layouts.addLayout(layout)
        self.Central_Frame.setLayout(layouts)
        self.setCentralWidget(self.Central_Frame)
        self.setStyleSheet('border:1px solid red')


    def Right_Dock_Code(self):
        files=[{'wb':'AAAAAAAA', 'bkgd':'BBBBB'}, {'wb':'CCCCC', 'bkgd':'DDDDD'},{'wb':'EEE','bkgd':'FFF'}]
        self.Added_Img_tree = Img_Tree(files, self)
        self.Right_Dock = QDockWidget('Selected Images', self)
        self.Right_Dock.setWidget(self.Added_Img_tree)
        self.Right_Dock.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.addDockWidget(Qt.RightDockWidgetArea, self.Right_Dock)




    def dir_selection(self):
        dir = QFileDialog.getExistingDirectory(self, "Choose a Directory", "~")
        self.Current_Dir = dir
        self.Tree.setRootIndex(self.Model.index(self.Current_Dir))
        self.Left_Dock.setWindowTitle(dir)
    