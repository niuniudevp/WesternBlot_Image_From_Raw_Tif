# 基本的功能函数##

from PyQt5.QtGui import QImage, QPixmap, QTransform
from PyQt5.QtCore import Qt
import cv2


def get_marker_pos(midpos):
    """Features
        获取marker的大小

        Args:

        Result:

    """
    w = 150
    h = 30
    w = w if w % 2 else w + 1
    h = h if h % 2 else h + 1
    p11 = 0 if (midpos[0] - (w - 1) / 2) < 0 else int(midpos[0] - (w - 1) / 2)
    p12 = 0 if (midpos[1] - (h - 1) / 2) < 0 else int(midpos[1] - (h - 1) / 2)
    p21 = 0 if (midpos[0] + (w - 1) / 2) < 0 else int(midpos[0] + (w - 1) / 2)
    p22 = 0 if (midpos[1] + (h - 1) / 2) < 0 else int(midpos[1] + (h - 1) / 2)
    return (p11, p12), (p21, p22)


def mapped_points_with_scale_factor(points, scale_factor):
    '''
    point: 要缩放的点 list or tuple
    scale_factor:缩放因子
    '''
    tp = type(points)
    ret = []
    for i in points:
        if type(i) == int or type(i) == float:
            # 四舍五入取最近的整数
            i_n = int(round(i * scale_factor))
        else:
            i_n = mapped_points_with_scale_factor(i, scale_factor)
        ret.append(i_n)
    return tp(ret)


def get_mouse_pos(mE):
    '''
    获取鼠标的位置
    x,y=get_mouse_pos(mE)
    '''
    t = mE.localPos()
    return int(t.x()), int(t.y())


def get_mouse_btn(mouse_event):
    '''
    获取鼠标的按键类型
    '''
    btn_code = mouse_event.button()
    if btn_code == Qt.LeftButton:
        return 'LEFT'
    if btn_code == Qt.RightButton:
        return 'RIGHT'
    if btn_code == Qt.MiddleButton:
        return 'MID'
    return None


def Get_Mouse_Parameter(mouse_event):
    """
    获取鼠标的按钮和位置
    btn,(x,y)=Get_Mouse_Parameter(event)
    """
    btn = get_mouse_btn(mouse_event)
    x, y = get_mouse_pos(mouse_event)
    return btn, (x, y)


def CV_Img_to_QImage(CV_Img,
                     Scale_Factor=1,
                     Angle=0,
                     Flap_H=False,
                     Flap_V=False):
    '''
    将opencv读取的图片转为QImage类型
    返回QPixmap,Rotated_Size
    '''
    height, width = CV_Img.shape[:2]
    currentFrame = cv2.cvtColor(CV_Img, cv2.COLOR_BGR2RGB)
    bytesPerline = 3 * width
    img = QImage(currentFrame, width, height, bytesPerline,
                 QImage.Format_RGB888)

    if Flap_H:
        # #上下翻转
        mt = QTransform()
        mt.setMatrix(1, 0, 0, 0, -1, 0, 0, 0, 1)
        img = img.transformed(mt)

    if Flap_V:
        # 左右翻转
        mt = QTransform()
        mt.setMatrix(-1, 0, 0, 0, 1, 0, 0, 0, 1)
        img = img.transformed(mt)

    if Angle != 0:
        mt = QTransform()
        mt.rotate(Angle)
        img = img.transformed(mt)

    width, height = img.width(), img.height()
    Im = QPixmap.fromImage(img)
    new_size_w, new_size_h = mapped_points_with_scale_factor((width, height),
                                                             Scale_Factor)
    Im = Im.scaled(new_size_w, new_size_h, Qt.KeepAspectRatio)
    return Im, (width, height)


def Get_Super_Parent(widget):
    """
    获取顶层Widget
    """
    t = widget.parentWidget()
    while not t.parentWidget() is None:
        t = t.parentWidget()
    return t


def Get_Parent_which_class_is(cls, wid):
    """
    获取父控件第一个是制定class
    """
    t = wid.parentWidget()
    while t and not t.__class__ == cls:
        t = t.parentWidget()
    return t


def Get_Pressed_Key(widget):
    """
    获取UI监听的keypress事件
    """

    UI = Get_Super_Parent(widget)
    return UI.PressedKey


def Rect_From_Two_Point(p1, p2):
    """
    根据给定的点返回以这两个点为对角线的矩形坐标
    x,y,w,h=Rect_from_two_point
    """
    LT_x = min(p1[0], p2[0])
    LT_y = min(p1[1], p2[1])
    w = abs(p1[0] - p2[0])
    h = abs(p1[1] - p2[1])
    return LT_x, LT_y, w, h


def Get_Mouse_Edge_Status(widget, point, Tolerance=12):
    """
    获取鼠标在widget内部是否靠近边框的状态
    [L,T,R,B]=Get_Mouse_Edge_Status
    """
    p0 = point[0]
    p1 = point[1]
    x1 = widget.width()
    y1 = widget.height()
    L, T, R, B = p0, p1, p0 - x1, p1 - y1
    L, T, R, B = [abs(i) < Tolerance for i in [L, T, R, B]]
    #print([L,T,R,B])
    return [L, T, R, B]


def Set_Mouse_Cursor(widget, Edge_array, default=Qt.ArrowCursor):
    """
    根据鼠标在widget内部的边框状态设置鼠标形状
    Edge_array 四个方向的状态
    default 四个方向都是False的情况
    return None
    """
    Cases = Edge_array
    Cursor = [
        Qt.SizeHorCursor, Qt.SizeVerCursor, Qt.SizeHorCursor, Qt.SizeVerCursor
    ]
    #print(Edge_array)
    if sum(Cases):
        for i in range(len(Cases)):
            if Cases[i]:
                widget.setCursor(Cursor[i])
    else:
        widget.setCursor(default)


def hierarchy(widget, padd='*', loop=0):
    padd = padd * loop
    print(padd + str(widget))

    for i in widget.children():
        hierarchy(i, '*', loop + 1)
