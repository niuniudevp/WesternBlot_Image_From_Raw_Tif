from PyQt5.QtWidgets import QFrame, QLabel, QLineEdit, QGridLayout, QCheckBox, QVBoxLayout, QHBoxLayout, QInputDialog, QDialog, QFormLayout, QDialogButtonBox
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QFont
from Utils import *
import cv2
from Config import *


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

    def __init__(self, label, paras_labels,style='QGrid', *args, **kwargs):

        QFrame.__init__(self, *args, **kwargs)
        if style == 'QGrid':
            Gd = QGridLayout(self)
        if style == 'QHBoxLayout':
            Gd=QHBoxLayout(self)
        if style == 'QVBoxLayout':
            Gd=QVBoxLayout(self)
        self.Label = QLabel(label, self)
        paras_labels = list(paras_labels)
        if style=='QGrid':
            Gd.addWidget(self.Label, 0, 0, 2, 1)
        else:
            Gd.addWidget(self.Label)
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
                    if style=='QGrid':
                        Gd.addWidget(l, row, col)
                    else:
                        Gd.addWidget(l)
                except IndexError:
                    print("Nothing")
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
        self.Flip_H = QCheckBox('Flip_H', self)
        self.Flip_V = QCheckBox('Flip_V', self)
        self.Crop = Box('Crop: ', 'whxy','QHBoxLayout', self)
        self.Marker = Box('Marker: ', 'wh','QHBoxLayout', self)
        self.Marker.Input_w.SetText(70)
        self.Marker.Input_h.SetText(15)
        self.Hv = QGridLayout(self)
        self.blk = QLabel('', self)
        v = QHBoxLayout()
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
        w,h=self.Crop.Input_w.Value(), self.Crop.Input_h.Value()
        Pre_Crop['w']=w
        Pre_Crop['h']=h
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
                Pre_Crop['w']=w
                Pre_Crop['h']=h
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
        self.Active = True
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
            self.Active = False
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


class Indicator_Config(object):
    def __init__(self):
        self.Name = ""
        self.x = 0
        self.y = 0
        self.w = 0
        self.h = 0


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
            font = QFont('Arial',C_Font_Size['UI']-2)
            inputDialog = QInputDialog(None)
            inputDialog.setInputMode(QInputDialog.TextInput)
            inputDialog.setWindowTitle('Input a name')
            inputDialog.setLabelText('Enter the name for this Indicator')
            inputDialog.setTextValue(self.Name.text())
            inputDialog.setFont(font)
            okPressed = inputDialog.exec_() 

            if okPressed:
                self.Name.setText(inputDialog.textValue())
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

    def Load_Config(self, Ind: Indicator_Config):
        self.Name.setText(Ind.Name)
        self.setGeometry(Ind.x, Ind.y, Ind.w, Ind.h)


class Img_Config(object):
    def __init__(self):
        self.FileName = ""
        self.Flip_H = False
        self.Flip_V = False
        self.Rotation = 0
        self.Indicators = []

    def addIndicator(self, Indicator):
        Ind_c = Indicator_Config()
        Ind_c.Name = Indicator.Name.text()
        Ind_c.x = Indicator.x()
        Ind_c.y = Indicator.y()
        Ind_c.w = Indicator.width()
        Ind_c.h = Indicator.height()
        self.Indicators.append(Ind_c)


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
        self.H_Refer_Line = Reference_Line("H", 200, self)
        self.H_Refer_Line.Label.Only_Move_V = True
        self.V_Refer_Line = Reference_Line("V", 200, self)
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

    def Display_Img(self, Scale_Factor=1, Angle=0, Flip_H=False, Flip_V=False):
        CV_Img = self.Src_Img
        QPix, (width, height) = CV_Img_to_QImage(CV_Img, Scale_Factor, Angle,
                                                 Flip_H, Flip_V)
        self.Scale_Factor = Scale_Factor
        self.Angle = Angle
        self.Img_Width = width
        self.Img_Height = height
        self.Flip_H = Flip_H
        self.Flip_V = Flip_V
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
                    indicator.setGeometry(x, y, Pre_Crop['w'], Pre_Crop['h'])
                    indicator.setVisible(True)
                    indicator.Active = True
                    indicator.Scale_Factor = self.Scale_Factor
            else:
                # 需要新建
                indicator = Indicator("WB", self)
                indicator.Scale_Factor = self.Scale_Factor
                self.Indicator.append(indicator)
                print(self.Action_Type + " 新建 Indicator 发送信号!")
                self.Indicator_Add.emit(self.Indicator)

                indicator.setStyleSheet("border:2px solid red")
                indicator.setGeometry(x, y, Pre_Crop['w'], Pre_Crop['h'])

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
                                indicator.Active = True
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
                indicator.Active = True
                indicator.setStyleSheet("border:2px solid red")
                # 当Wb已经选定的时候添加的Marker默认吸附到crop边框上
                if self.Temp_Indicator:
                    crop = self.Temp_Indicator[0]  #默认只有一个
                    if crop.isVisible():
                        c_x, c_w = crop.x(), crop.width()
                        if (c_x + c_w) < x:
                            # 右侧Marker的情况
                            indicator.setGeometry(c_x + c_w, y - Marker_h / 2,
                                                  Marker_w, Marker_h)
                        if x < c_x:
                            # 左侧Marker的情况
                            indicator.setGeometry(c_x - Marker_w,
                                                  y - Marker_h / 2, Marker_w,
                                                  Marker_h)
                else:
                    indicator.setGeometry(x - Marker_w / 2, y - Marker_h / 2,
                                          Marker_w, Marker_h)
                indicator.Scale_Factor = self.Scale_Factor

        QLabel.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        self.show_stat_bar_info(event)
        btn, (x, y) = Get_Mouse_Parameter(event)

        # 鼠标画框
        if self.Action_Type == "WB" and self.Pressed_Mouse == "LEFT":
            indicator = self.Indicator[0]
            x, y, w, h = Rect_From_Two_Point(self.Mouse_Press_Loc, [x, y])
            indicator.setGeometry(x, y, w, h)
            Pre_Crop['w']=w
            Pre_Crop['h']=h
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
        self.Display_Img(New_Scale_Factor, self.Angle, self.Flip_H,
                         self.Flip_V)

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

    def get_config(self):
        c = Img_Config()
        c.FileName = File_path(self.FileName)[1]
        c.FileName = self.FileName
        c.Flip_H = self.Flip_H
        c.Flip_V = self.Flip_V
        c.Rotation = self.Angle
        for Ind in self.Indicator:
            c.addIndicator(Ind)
        return c

    def Load_Config(self, Cfg: Img_Config):
        self.FileName = Cfg.FileName
        self.Flip_V = Cfg.Flip_V
        self.Flip_H = Cfg.Flip_H
        for Ind_c in Cfg.Indicators:
            Ind = Indicator(self.Action_Type, self)
            Ind.Load_Config(Ind_c)
            #self.Indicator_Add.emit(self.Indicator)
        self.__Init_UI(self.FileName)

    # signal links
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
        self.Display_Img(self.Scale_Factor, self.Angle, self.Flip_H,
                         self.Flip_V)
        #print("[Img] Syncing # 更新自身的Indicators")
        #for i in self.Indicator:
        #    i.Scaled(self.Scale_Factor)
        #print("[Img] Syncing # 同步Indicator===>Temp_Indicator")
        #self.Syncing_Indicator_to_Temp(src, self)
        #self.Syncing_Indicator_to_Temp(self, src)
        print("[Img] Syncing End")

class Muliti_Input_Dialog(QDialog):
    def __init__(self, *args, **kwargs):
        QDialog.__init__(self, *args, **kwargs)
        self.Form = QFormLayout()
        self.setLayout(self.Form)
        
    def Add_row(self, *args):
        self.Form.addRow(*args)
    
    def exec(self):
        self.btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal, self)
        self.Form.addRow(self.btn_box)
        self.btn_box.accepted.connect(self.accept)
        self.btn_box.rejected.connect(self.reject)
        return QDialog.exec(self)