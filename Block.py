# 各种自定义Widgets
from PyQt5.QtWidgets import QFrame, QLineEdit, QLabel, QHBoxLayout, QGridLayout, QVBoxLayout, QScrollArea
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from Utils import *
import cv2, time


class LabeledInPut(QFrame):
    Listen_KEY = Qt.Key_Shift

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
        self.Input.textChanged.connect(self.run_on_change)

    def Set_Mini_value(self, Value):
        self.Mini_value = Value

    def Set_Max_value(self, Value):
        self.Max_value = Value

    def style_set(self):
        self.Layout.setSpacing(0)
        self.Layout.setContentsMargins(2, 0, 0, 0)
        self.Layout.setColumnStretch(1, 3)
        self.Layout.setAlignment(Qt.AlignRight)

    def __get_value(self):
        '''
        获取input的value
        '''
        try:
            v = float(self.Input.text())
        except ValueError:
            v = None
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

    def run_on_change(self):
        print(self.Caption() + " Changed")
        FUNC_RUN_ON_CHANGE(self)


class Box(QFrame):
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
                except IndexError as e:
                    print("Nothong")
        self.setLayout(Gd)
        self.Layout = Gd
        self.style_set()
        self.__dict__.update({RUN_ON_CHANGE: FUNC_RUN_ON_CHANGE})

    def style_set(self):
        self.Layout.setSpacing(0)
        self.Layout.setContentsMargins(2, 0, 0, 0)
        # self.setStyleSheet("border: 1px solid red")


class ToolBar(QFrame):
    def __init__(self, *args, **kwargs):
        QFrame.__init__(self, *args, **kwargs)
        self.Init_UI()
        self.__dict__.update({RUN_ON_CHANGE: FUNC_RUN_ON_CHANGE})

    def Init_UI(self):
        Scale = LabeledInPut('Scale:', 0, self)
        Rotation = LabeledInPut('Rotation:', 0, self)
        Crop = Box('Crop: ', 'xywh', self)
        Marker = Box('Marker: ', 'wh', self)
        Hv = QGridLayout(self)
        blk = QLabel('', self)
        Hv.addWidget(Scale, 0, 0)
        Hv.addWidget(Rotation, 0, 1)
        Hv.addWidget(Crop, 0, 2)
        Hv.addWidget(blk, 0, 3)
        Hv.addWidget(Marker, 0, 4)
        Hv.setColumnStretch(3, 4)
        self.setLayout(Hv)


class Reference_Line(QFrame):
    """
    竖直和水平参考线
    """
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

    def Update_Appearance(self):
        try:
            factor = self.parentWidget().Scale_Factor
        except:
            factor = 1
        self.P_Factor = factor
        self.Label.setStyleSheet("color:white;background:" + self.Color)
        self.Label.setMinimumSize(40, 20)
        self.Label.setAlignment(Qt.AlignHCenter)

        if self.Type == "H":
            self.resize(self.parentWidget().width(), self.height())
            self.Line.setStyleSheet("border: 2px solid " + self.Color)
            self.Line.resize(self.parentWidget().width(), 2)
            self.move(0, int(round(self.Position * factor)))
        if self.Type == "V":
            self.resize(self.width(), self.parentWidget().height())
            self.Line.setStyleSheet("color:white;border: 2px solid " +
                                    self.Color)
            self.Line.resize(2, self.parentWidget().height())
            self.move(int(round(self.Position * factor)), 0)

    def moveEvent(self, event):
        P = Get_Parent_which_class_is(LabeledImg, self)
        self.addAction
        if self.Type == "H":
            self.Position = int(round(self.y() / self.P_Factor))
        if self.Type == "V":
            self.Position = int(round(self.x() / self.P_Factor))


class MyLabel(QLabel):
    """
    # 重写QLabel
    可以鼠标move,可以鼠标调整大小,可以Arrow move
    左键激活,邮件取消激活
    """
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
        self.clearFocus()

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
        QLabel.keyPressEvent(self, event)

    def keyReleaseEvent(self, event):
        # print("KeyReleased!")
        self.PressedKey = None
        if event.key() == Qt.Key_Delete:
            self.setVisible(False)

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


class Indicator(MyLabel):
    def __init__(self, Type, *args, **kwargs):
        MyLabel.__init__(self, *args, **kwargs)
        self.Can_Move_with_Mouse = True
        self.Can_move_with_Arrow_Key = True
        if Type == "WB":
            self.Can_Adjust_Edge = True
        self.Type = Type
        self.show()


class Indicators(QLabel):
    """
    区域指示器
    """
    def __init__(self, *args, **kwargs):
        QLabel.__init__(self, *args, **kwargs)
        self.setMouseTracking(True)
        self.Fill = False  # 是否填充
        self.Press_Point = None
        self.Focused = False
        self.show()

    def Set_Active(self):
        UI = Get_Super_Parent(self)
        Inds = UI.findChildren(Indicator)
        for i in Inds:
            i.Set_Disactive()
        self.Focused = True
        UI.Active_Indicator = self
        self.setStyleSheet("border:2px solid green")

    def Set_Disactive(self):
        UI = Get_Super_Parent(self)
        self.Focused = False
        UI.Active_Indicator = None
        self.setStyleSheet("border:2px solid red")

    def mouseMoveEvent(self, event):
        print("Moving")
        print(self.__dict__)
        x, y = get_mouse_pos(event)
        L, T, R, B = Get_Mouse_Edge_Status(self, (x, y))
        # 如果激活的时候根据鼠标位置设置鼠标形状
        if self.Focused:
            Set_Mouse_Cursor(self, [L, T, R, B])

        if self.Press_Point and not self.Fill:
            # 移动改变情况
            move_x = x - self.Press_Point[0]
            move_y = y - self.Press_Point[1]

            if sum([L, T, R, B]) and not self.Fill:
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
                    p_l_distance = ori_w - x
                    fixed_p = (loc_x, loc_y)
                    TL = (loc_x + x - p_l_distance, loc_y + ori_h)
                    x, y, w, h = Rect_From_Two_Point(TL, fixed_p)
                if B:
                    # x不变,y不变,w不变,h变
                    p_l_distance = ori_h - y
                    fixed_p = (loc_x, loc_y)
                    TL = (loc_x + ori_w, y - p_l_distance + loc_y)
                    x, y, w, h = Rect_From_Two_Point(TL, fixed_p)
                self.setGeometry(x, y, w, h)

            else:
                # 整体位置Move
                self.move(self.x() + move_x, self.y() + move_y)
                self.setCursor(Qt.ClosedHandCursor)
            self.Focused = False

        # QLabel.mouseMoveEvent(self,event)

    def mousePressEvent(self, event):
        print("press_down")
        btn = get_mouse_btn(event)
        x, y = get_mouse_pos(event)
        if btn == 'LEFT':
            Edge = Get_Mouse_Edge_Status(self, (x, y))
            if not sum(Edge):
                self.setCursor(Qt.ClosedHandCursor)
            self.Press_Point = [x, y]
            self.setStyleSheet("border:2px solid green")

    def mouseReleaseEvent(self, event):
        # 在Fill情况下当右键按下抬起后删除点击的box# 
        btn = get_mouse_btn(event)
        x, y = get_mouse_pos(event)
        if btn == "RIGHT":
            self.setGeometry(0, 0, 0, 0)
            self.setStyleSheet("")

        if self.Focused:
            self.Set_Disactive()
        else:
            self.Set_Active()

        print("relase")
        self.Press_Point = None
        self.setCursor(Qt.ArrowCursor)
        # self.setStyleSheet("border:1px solid blue")
        QLabel.mouseReleaseEvent(self, event)


class Img(QLabel):
    """
    自定义Img类
    """

    Listen_KEY = Qt.Key_Control

    def __init__(self, Filename, *args, **kwargs):
        """
        Filename是要加载的文件名称
        """
        QLabel.__init__(self, *args, **kwargs)
        self.setMouseTracking(True)
        self.Action_Type = 'WB'
        self.Allowed_Indicator_Num = 1
        self.Indicator = []
        self.Angle = 0
        self.Src_Img = None
        self.Displayed_Img = None
        self.Scale_Factor = 1.0
        self.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.Pressed_Mouse = None
        self.Mouse_Press_Loc = []
        self.H_Refer_Line = Reference_Line("H", 924, self)
        self.H_Refer_Line.Label.Only_Move_V = True
        self.V_Refer_Line = Reference_Line("V", 300, self)
        self.V_Refer_Line.Label.Only_Move_H = True

        self.__Init_UI(Filename)

    def __Init_UI(self, Filename):
        self.__Load_Img(Filename)
        self.Display_Img(self.Src_Img)
        # self.setStyleSheet("border: 2px solid red")

    def __Load_Img(self, Filename):
        Cv_Img = cv2.imread(Filename)
        self.Src_Img = Cv_Img
        height, width = Cv_Img.shape[:2]
        self.Img_Width = width
        self.Img_Height = height

    def Display_Img(self, CV_Img, Scale_Factor=1):
        QPix = CV_Img_to_QImage(CV_Img, Scale_Factor)
        self.setPixmap(QPix)
        self.Displayed_Img = CV_Img
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
            else:
                # 需要新建
                indicator = Indicator("WB", self)
                self.Indicator.append(indicator)
                indicator.setStyleSheet("border:2px solid red")
                indicator.setGeometry(x, y, 0, 0)

        if btn == "LEFT" and self.Action_Type == 'BKGD':
            print("BKGD_LEFT")
            indicator = None
            PressedBtn = Get_Pressed_Key(self)
            # Box是空的时候直接添加
            if not self.Indicator:
                indicator = Indicator(self.Action_Type, self)
                self.Indicator.append(indicator)
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
                            self.Indicator.append(indicator)

                    else:
                        print("Box is Full")
                        # indicator 依然是None
            # 
            Marker_w = 80
            Marker_h = 20
            # 
            if indicator:
                indicator.setVisible(True)
                indicator.setStyleSheet("border:2px solid red")
                indicator.setGeometry(x - Marker_w / 2, y - Marker_h / 2,
                                      Marker_w, Marker_h)
        QLabel.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        self.show_stat_bar_info(event)
        btn, (x, y) = Get_Mouse_Parameter(event)

        # 鼠标画框
        if self.Action_Type == "WB" and self.Pressed_Mouse == "LEFT":
            indicator = self.Indicator[0]
            x, y, w, h = Rect_From_Two_Point(self.Mouse_Press_Loc, [x, y])
            indicator.setGeometry(x, y, w, h)
        QLabel.mouseMoveEvent(self, event)

    def mouseReleaseEvent(self, event):
        btn = get_mouse_btn(event)
        self.Pressed_Mouse = None
        self.Mouse_Press_Loc = []
        QLabel.mouseReleaseEvent(self, event)

    def wheelEvent(self, event):
        # 缩放# 
        Pressed_Key = Get_Pressed_Key(self)
        if Pressed_Key and Pressed_Key == self.Listen_KEY:
            old_Scale_Factor = self.Scale_Factor
            driction_v = -0.05 if event.angleDelta().y() < 0 else 0.05
            self.Scale_Factor = self.Scale_Factor + driction_v
            if self.Scale_Factor < 0.2:
                self.Scale_Factor = 0.2
            self.Display_Img(self.Src_Img, self.Scale_Factor)

            # Indicator也要缩放
            for i in self.Indicator:
                x, y, w, h = mapped_points_with_scale_factor(
                    [i.x(), i.y(), i.width(),
                     i.height()], self.Scale_Factor / old_Scale_Factor)
                i.setGeometry(x, y, w, h)

        self.show_stat_bar_info(event)

        # QLabel.wheelEvent(self,event)

    def resizeEvent(self, event):
        old_Scale_Factor = self.Scale_Factor
        # self.Scale_Factor=self.width()/self.Img_Width

        self.H_Refer_Line.Update_Appearance()
        self.V_Refer_Line.Update_Appearance()
        # self.resize(new_width,new_height)
        # self.Display_Img(self.Displayed_Img,self.Scale_Factor)
        QLabel.resizeEvent(self, event)

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
        self.scoller = QScrollArea(self)
        self.scoller.setWidget(self.Img)
        self.scoller.setWidgetResizable(True)
        self.scoller.horizontalScrollBar().valueChanged.connect(
            self.Send_Sync_info)
        self.scoller.horizontalScrollBar().sliderMoved.connect(
            self.Send_Sync_info)
        self.scoller.verticalScrollBar().valueChanged.connect(
            self.Send_Sync_info)
        # self.scoller.verticalScrollBar().sliderMoved.connect(self.Send_Sync_info)
        # self.scroll.horizontalScrollBar().sliderMoved.connect(self.do_Sync)
        # self.Label.setStyleSheet("background:blue")
        self.Label.setAlignment(Qt.AlignHCenter)
        self.Label.setMaximumHeight(30)
        hv = QVBoxLayout(self)
        hv.addWidget(self.Label)
        hv.addWidget(self.scoller)

    def Send_Sync_info(self):
        self.Syncing.emit([self])

    @pyqtSlot(list)
    def do_Sync(self, LI):
        LI = LI[0]
        self.Img.Scale_Factor = LI.Img.Scale_Factor
        print(str(time.time()) + " syncing from " + LI.Img.Action_Type)
        self.Img.Display_Img(self.Img.Displayed_Img, self.Img.Scale_Factor)
        self.Img.H_Refer_Line.Position = LI.Img.H_Refer_Line.Position
        self.Img.H_Refer_Line.Update_Appearance()
        self.Img.V_Refer_Line.Position = LI.Img.V_Refer_Line.Position
        self.Img.V_Refer_Line.Update_Appearance()
        self.scoller.horizontalScrollBar().setSliderPosition(
            LI.scoller.horizontalScrollBar().sliderPosition())
        self.scoller.verticalScrollBar().setSliderPosition(
            LI.scoller.verticalScrollBar().sliderPosition())

        self.resize(self.width(), self.height())

    def mousePressEvent(self, event):
        print("Labeled_Img Clicked!")
        # self.Syncing.emit([self])

    def mouseMoveEvent(self, event):
        print("Labeled_Img Moved")
        self.Syncing.emit([self])

    def mouseReleaseEvent(self, event):
        print("Labeled_Img Released!")
        self.Syncing.emit([self])

    def wheelEvent(self, event):
        print("Labeled_Img wheeled!")
        self.Syncing.emit([self])


class Img_Block(QFrame):
    """
    Assign two picture
    同步两个图片的设置情况
    """
    def __init__(self, *args, **kwargs):
        QFrame.__init__(self, *args, **kwargs)
        hv = QHBoxLayout(self)
        WB = 'blot.tif'
        BG = 'background.tif'
        self.WB = LabeledImg(WB, self)
        self.BG = LabeledImg(BG, self)
        self.BG.Img.Action_Type = "BKGD"
        self.BG.Img.Allowed_Indicator_Num = 5
        self.WB.Syncing.connect(self.BG.do_Sync)
        hv.addWidget(self.WB)
        hv.addWidget(self.BG)
        hv.setSpacing(20)
        self.AutoreSize()

    def AutoreSize(self):
        UI = self.parentWidget()
        self.setGeometry(10, 100, UI.width() - 20, UI.height() - 300)

    def mousePressEvent(self, event):
        print("Img_Box is clicked")
        print(self.event())

    def childEvent(self, event):
        print(event)
        self.changeEvent
