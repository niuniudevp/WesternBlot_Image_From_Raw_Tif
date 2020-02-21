##基本的功能函数##

from PyQt5.QtGui import QImage,QPixmap
from PyQt5.QtCore import Qt
import cv2

def get_marker_pos(midpos):
        """Features 
        获取marker的大小
        
        Args:

        Result:

        """
        w=150
        h=30
        w=w if w%2 else w+1
        h=h if h%2 else h+1
        p11=0 if (midpos[0]-(w-1)/2)<0 else int(midpos[0]-(w-1)/2)
        p12=0 if (midpos[1]-(h-1)/2)<0 else int(midpos[1]-(h-1)/2)
        p21=0 if (midpos[0]+(w-1)/2)<0 else int(midpos[0]+(w-1)/2)
        p22=0 if (midpos[1]+(h-1)/2)<0 else int(midpos[1]+(h-1)/2)
        return (p11,p12),(p21,p22)

def mapped_points_with_scale_factor(points,scale_factor):
    '''
    point: 要缩放的点 list or tuple
    scale_factor:缩放因子
    '''
    tp=type(points)
    ret=[]
    for i in points:
        if type(i) == int:
            ###四舍五入取最近的整数
            i_n=int(round(i*scale_factor))
        else:
            i_n=mapped_points_with_scale_factor(i,scale_factor)               
        ret.append(i_n)
    return tp(ret)

def get_mouse_pos(mE):
    '''
    获取鼠标的位置
    '''
    n = mE.button()
    t=mE.localPos()
    return t.x(),t.y()

def get_mouse_btn(mouse_event):
    '''
    获取鼠标的按键类型
    '''
    btn_code=mouse_event.button()
    if btn_code==Qt.LeftButton:
        return 'LEFT'
    if btn_code==Qt.RightButton:
        return 'RIGHT'
    if btn_code == Qt.MiddleButton:
        return 'MID'
    return None


RUN_ON_CHANGE="RUN_ON_CHANGE"
def FUNC_RUN_ON_CHANGE(widgets):

    P=widgets.parentWidget()
    if P and RUN_ON_CHANGE in P.__dict__.keys():
        print(P)
        P.__dict__[RUN_ON_CHANGE](P)


def CV_Img_to_QImage(CV_Img,Scale_Factor=1):
    '''
    将opencv读取的图片转为QImage类型
    返回QPixmap,Size
    '''
    height, width = CV_Img.shape[:2]
    currentFrame = cv2.cvtColor(CV_Img, cv2.COLOR_BGR2RGB)    
    bytesPerline = 3 * width
    img = QImage(currentFrame, width, height, bytesPerline, QImage.Format_RGB888)    
    Im=QPixmap.fromImage(img)
    #new_size_w,new_size_h=int(round(width*Scale_Factor)),int(round(height*Scale_Factor))
    new_size_w,new_size_h=mapped_points_with_scale_factor((width,height),Scale_Factor)
    Im=Im.scaled(new_size_w,new_size_h,Qt.KeepAspectRatio)
    return Im

def Get_Super_Parent(widget):
    """
    获取顶层Widget
    """
    t=self.parentWidget()
    while not t.parentWidget() is None:
        t=t.parentWidget()
    return t

def Get_Pressed_Key(widget):
    """
    获取UI监听的keypress事件
    """

    UI=Get_Super_Parent(widget)
    return UI.PressedKey

