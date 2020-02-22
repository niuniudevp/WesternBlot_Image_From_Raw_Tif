####各种自定义Widgets
from PyQt5.QtWidgets import QFrame,QLineEdit,QLabel,QHBoxLayout,QGridLayout,QVBoxLayout
from PyQt5.QtCore import Qt,QEvent
from Utils import *
import cv2

class LabeledInPut(QFrame):
    Listen_KEY=Qt.Key_Shift
    def __init__(self,label,value,*args,**kwargs):
        QFrame.__init__(self,*args,**kwargs)
        self.Label=QLabel(self)
        self.Label.setText(label)
        self.Input=QLineEdit(self)
        self.Input.setText(str(value))
        self.Layout=QGridLayout(self)        
        self.Layout.addWidget(self.Label,0,0)
        self.Layout.addWidget(self.Input,0,1)
        self.setLayout(self.Layout)
        self.Value=self.__get_value
        self.Text=self.Input.text
        self.SetText=self.__set_value
        self.Caption=self.Label.text
        self.Set_Caption=self.__set_caption
        self.PressedKey=None
        self.Mini_value=0
        self.style_set()
        self.Input.textChanged.connect(self.run_on_change)

    def Set_Mini_value(self,Value):
        self.Mini_value=Value
    def Set_Max_value(self,Value):
        self.Max_value=Value

    def style_set(self):
        self.Layout.setSpacing(0)
        self.Layout.setContentsMargins(2,0,0,0)
        self.Layout.setColumnStretch(1, 3)
        self.Layout.setAlignment(Qt.AlignRight)

    def __get_value(self):
        '''
        获取input的value
        '''
        try:
            v=float(self.Input.text())
        except ValueError as e:
            v=None
        return v
    def __set_caption(self,Caption):
        '''
        设置显示的Label文本
        '''
        self.Label.setText(Caption)
    
    def __set_value(self,value):

        if 'Mini_value' in self.__dict__.keys():
            value=self.Mini_value if value < self.Mini_value else value
        if 'Max_value' in self.__dict__.keys():
            value=self.Max_value if value > self.Max_value else value
        self.Input.setText(str(value))
    
    def keyPressEvent(self,event):
        self.PressedKey=event.key()
        QFrame.keyPressEvent(self,event)
    def keyReleaseEvent(self,event):
        self.PressedKey=None
        QFrame.keyReleaseEvent(self,event)
    
    def wheelEvent(self, event):
        s=self.Value()
        if not s is None :
            ##s是数字的时候
            v=self.Text()
            S_is_Int=True if str(s).split('.')[0]==v.strip() else False
            ###没有按下shift时按照2%改变
            if S_is_Int:
                change_rate= 5 if self.PressedKey==self.Listen_KEY and S_is_Int else 1
            else:
                change_rate= 0.5 if self.PressedKey==self.Listen_KEY and S_is_Int else 0.2
            ##如果同时按下了shift键就按照乘法改变
            driction= 1 if event.angleDelta().y() > 0 else -1
            s=s+change_rate*driction
            s=int(round(s)) if S_is_Int else round(s,3)
            self.SetText(s)

    def run_on_change(self):
        print(self.Caption() +" Changed")
        FUNC_RUN_ON_CHANGE(self)


class Box(QFrame):
    def __init__(self,label,paras_labels,*args,**kwargs):
        

        QFrame.__init__(self,*args,**kwargs)
        Gd=QGridLayout(self)
        self.Label=QLabel(label,self)
        paras_labels=list(paras_labels)
        Gd.addWidget(self.Label,0,0,2,1)
        for i in paras_labels:
            self.__dict__.update({"Input_"+i:LabeledInPut(i,10,self)})
        lt=len(paras_labels)
        col=lt//2+1 if lt%2 else lt//2
        col=col+1
        for col in range(1,col):
            for row in range(0,2):
                try:
                    s=paras_labels.pop(0)
                    l=eval("self.Input_"+s)
                    Gd.addWidget(l,row,col)
                except IndexError as e:
                    print ("Nothong")
        self.setLayout(Gd)
        self.Layout=Gd
        self.style_set()
        self.__dict__.update({RUN_ON_CHANGE:FUNC_RUN_ON_CHANGE})
    
    def style_set(self):
        self.Layout.setSpacing(0)
        self.Layout.setContentsMargins(2,0,0,0)            
        #self.setStyleSheet("border: 1px solid red")
    

class ToolBar(QFrame):
    def __init__(self,*args,**kwargs):
        QFrame.__init__(self,*args,**kwargs)
        self.Init_UI()
        self.__dict__.update({RUN_ON_CHANGE:FUNC_RUN_ON_CHANGE})

    def Init_UI(self):
        Scale=LabeledInPut('Scale:',0,self)
        Rotation=LabeledInPut('Rotation:',0,self)
        Crop=Box('Crop: ','xywh',self)
        Marker=Box('Marker: ','wh',self)
        Hv=QGridLayout(self)
        blk=QLabel('',self)
        Hv.addWidget(Scale,0,0)
        Hv.addWidget(Rotation,0,1)
        Hv.addWidget(Crop,0,2)
        Hv.addWidget(blk,0,3)
        Hv.addWidget(Marker,0,4)
        Hv.setColumnStretch(3,4)
        self.setLayout(Hv)


class Indicator(QLabel):
    """
    区域指示器
    """
    def __int__(self,*args,**kwargs):
        QLabel.__init__(self,*args,**kwargs)
        self.Fill=False ##是否填充
        self.Focus_Point=None
        self.Fcs=False

    def mouseMoveEvent(self,event):
        print("Moving")
        x,y=get_mouse_pos(event)
        move_x=x-self.Focus_Point[0]
        move_y=y-self.Focus_Point[1]
        self.move(self.x()+move_x,self.y()+move_y)
        

        QLabel.mouseMoveEvent(self,event)

    def mousePressEvent(self,event):
        print("press_down")
        btn=get_mouse_btn(event)
        x,y=get_mouse_pos(event)
        if btn=='LEFT':
            self.Focus_Point=[x,y]
            self.setCursor(Qt.ClosedHandCursor)
            self.setStyleSheet("border:2px solid green")

    
    def mouseReleaseEvent(self,event):
        ###在Fill情况下当右键按下抬起后删除点击的box###
        btn=get_mouse_btn(event)
        x,y=get_mouse_pos(event)
        if self.Fill:
            self.setGeometry(0,0,0,0)
            self.setStyleSheet("")
        
        if self.isFocused:
            self.isFocused=False
            self.setStyleSheet("border:1px solid blue")
        else:
            self.isFocused=True
            self.setStyleSheet("border:2px solid green")

        print("relase")
        self.Focus_Point=None
        self.setCursor(Qt.ArrowCursor)
        self.setStyleSheet("border:1px solid blue")

        QLabel.mouseReleaseEvent(self,event)




class Img(QLabel):
    Listen_KEY=Qt.Key_Control
    def __init__(self,Filename,*args, **kwargs):
        QLabel.__init__(self, *args, **kwargs)
        self.setMouseTracking(True)
        self.Action_Type='WB'
        self.Box=[]
        self.Allowed_Box_Num=1
        self.Indicator=[]
        self.Src_Img=None
        self.Displayed_Img=None
        self.Scale_Factor=1
        self.setAlignment(Qt.AlignTop|Qt.AlignLeft)
        self.Pressed_Mouse=None
        self.Mouse_Press_Loc=[]
        #self.Indicator_LayOut=QHBoxLayout(self)
        self.__Init_UI(Filename)

    def __Init_UI(self,Filename):
        self.__Load_Img(Filename)
        self.__Display_Img(self.Src_Img)
        self.setStyleSheet("border: 2px solid red")
    
    def __Load_Img(self,Filename):
        Cv_Img=cv2.imread(Filename)
        self.Src_Img=Cv_Img
        height, width = Cv_Img.shape[:2]
        self.Img_Width=width
        self.Img_Height=height

    def __Display_Img(self,CV_Img,Scale_Factor=1):
        QPix=CV_Img_to_QImage(CV_Img,Scale_Factor)
        self.setPixmap(QPix)
        self.Displayed_Img=CV_Img
    


    def mousePressEvent(self,event):
        btn=get_mouse_btn(event)
        x,y=get_mouse_pos(event)
        self.Pressed_Mouse=btn
        self.Mouse_Press_Loc=[x,y]

        if btn=="LEFT" and self.Action_Type=='WB':
            print("WB_LEFT")
            if self.Box:
                indicator=self.Box[0]
            else:
                #需要新建
                indicator=Indicator(self)
                indicator.Fill=False
                indicator.show()#更新后才会显示出来
                self.Box.append(indicator)
                #self.Indicator_LayOut.addWidget(indicator)
            
            indicator.setStyleSheet("border:1px solid blue")
            indicator.setGeometry(x,y,0,0)
                    
        if btn=="LEFT" and self.Action_Type=='BKGD':
            print("BKGD_LEFT")
            indicator=None
            PressedBtn=Get_Pressed_Key(self)
            ###Box是空的时候直接添加
            if not self.Box:
                indicator=Indicator(self)
                indicator.Fill=True
                indicator.show()
                self.Box.append(indicator)  
            else:
                if PressedBtn==Qt.Key_Control:
                    if 0<len(self.Box)<self.Allowed_Box_Num:
                        ##遍历box看有没有没有用的##
                        for b in self.Box:
                            if b.width()==0:
                                indicator=b
                                break
                        
                        #如果遍历后还是没有
                        if not indicator:
                            indicator=Indicator(self)
                            indicator.Fill=True
                            indicator.show()
                            self.Box.append(indicator)
                            #self.Indicator_LayOut.addWidget(indicator)
                    
                    else:
                        print("Box is Full")
                        ###indicator 依然是None
                
                else:
                    ###不按着Ctrl的时候隐藏所有Box,返回第一个box####
                    for box in self.Box:
                        box.setGeometry(0,0,0,0)
                        box.setStyleSheet("")
                    indicator=self.Box[0]
            
            ###
            Marker_w=40
            Marker_h=10
            ###
            if indicator:
                indicator.setStyleSheet("background:green")
                indicator.setGeometry(x-Marker_w/2,y-Marker_h/2,Marker_w,Marker_h)
    
    def mouseMoveEvent(self,mE):
        x,y=get_mouse_pos(mE)
        btn=get_mouse_btn(mE)
        mes="Image Pointer (x:%s y:%s) |Scale: %s" %(str(x),str(y),str(self.Scale_Factor))
        t=Get_Super_Parent(self)
        t.statusbar.showMessage("Ready "+ mes)
    
        #移动的时候一直按着左键
        if self.Action_Type=="WB" and self.Pressed_Mouse=="LEFT":
            indicator=self.Box[0]
            x,y,w,h=Rect_From_Two_Point(self.Mouse_Press_Loc,[x,y])
            indicator.setGeometry(x,y,w,h)
                 
    def mouseReleaseEvent(self,event):
        btn=get_mouse_btn(event)
        self.Pressed_Mouse=None
        self.Mouse_Press_Loc=[]







    def resizeEvent(self,event):
        new_width=self.width()
        self.Scale_Factor=new_width/self.Img_Width
        new_height=mapped_points_with_scale_factor([self.height()],self.Scale_Factor)[0]
        #self.resize(new_width,new_height)
        self.__Display_Img(self.Displayed_Img,self.Scale_Factor)

    

class LabeledImg(QFrame):
    def __init__(self,Filename,*args,**kwargs):
        QFrame.__init__(self,*args,**kwargs)
        self.FileName=Filename
        self.Img=Img(self.FileName,self)
        self.Label=QLabel(self.FileName,self)        
        #self.Label.setStyleSheet("background:blue")
        self.Label.setAlignment(Qt.AlignHCenter)
        self.Label.setMaximumHeight(30)
        hv=QVBoxLayout(self)
        hv.addWidget(self.Label)
        hv.addWidget(self.Img)
    
    
class Img_Block(QFrame):
    """
    Assign two picture
    """
    def __init__(self,*args,**kwargs):
        QFrame.__init__(self,*args,**kwargs)
        hv=QHBoxLayout(self)
        WB='blot.tif'
        BG='background.tif'
        self.WB=LabeledImg(WB,self)
        self.BG=LabeledImg(BG,self)
        self.BG.Img.Action_Type="BKGD"

        hv.addWidget(self.WB)
        hv.addWidget(self.BG)
        hv.setSpacing(20)
        self.AutoreSize()
    
    def AutoreSize(self):
        UI=self.parentWidget()
        self.setGeometry(10,100,UI.width()-20,UI.height()-300)


