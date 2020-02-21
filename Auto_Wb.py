'''
Until to generate Westerblot img from source tiffs
'''
import sys
import re,random
import cv2
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QAction, QApplication
from PyQt5.QtWidgets import QWidget,QLabel,QLineEdit,QPushButton,QHBoxLayout,QVBoxLayout,QFormLayout
from PyQt5.QtGui import QPixmap,QPalette,QIntValidator,QDoubleValidator,QImage



class Utils():

    def get_marker_pos(self,midpos):
        '''
        获取marker的大小
        '''
        w=150
        h=30
        w=w if w%2 else w+1
        h=h if h%2 else h+1
        p11=0 if (midpos[0]-(w-1)/2)<0 else int(midpos[0]-(w-1)/2)
        p12=0 if (midpos[1]-(h-1)/2)<0 else int(midpos[1]-(h-1)/2)
        p21=0 if (midpos[0]+(w-1)/2)<0 else int(midpos[0]+(w-1)/2)
        p22=0 if (midpos[1]+(h-1)/2)<0 else int(midpos[1]+(h-1)/2)
        return (p11,p12),(p21,p22)

    def scale_point(self,scale_factor,point):
        tp=type(point)
        ret=[]
        for i in point:
            if type(i) == int:
                i_n=int(i*scale_factor)
            else:
                i_n=self.scale_point(scale_factor,i)               
            ret.append(i_n)
        return tp(ret)

    def get_mouse_pos(self,mE):
        '''
        获取鼠标的位置
        '''
        n = mE.button()
        t=mE.localPos()
        factor=self.scale_factor
        pos=(int(t.x()/factor),int(t.y()/factor))
        return pos

    def get_mouse_btn(self,mouse_event):
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





###重写QLineEdit
class LineEdit(QLineEdit):
    #KEY = Qt.Key_Shift
    def __init__(self, *args, **kwargs):
        QLineEdit.__init__(self, *args, **kwargs)
        self.isint=True

    def wheelEvent(self, event):
        #print("bbbb")
        s=float(self.text())
        if self.isint:
            factor= 1 if event.angleDelta().y() > 0 else -1
            s=s+factor
            s=str(1 if int(s) ==0 else int(s))    
        else:
            factor= 1.2 if event.angleDelta().y() > 0 else 0.8
            s=s*factor
            s=s if s>0.05 else 0.050
            s=str(round(s,3))
        self.setText(s)
        #event.accept()

class Indicator(QLabel):
    def __int__(self,*args,**kwargs):
        QLabel.__init__(self,*args,**kwargs)
        #self.setText(" ")
        #self.setStyleSheet("border: 2px solid red")
        #self.resize(0,0)
        #self.move(0,0)

    def mouseMoveEvent(self,event):
        print("Moving"+ random.choice(['1','2','3']))
        #QLabel.mouseMoveEvent(self,event)

    def mousePressEvent(self,event):
        print("press_down")
        btn=Utils().get_mouse_btn(event)
        if btn=='LEFT':
            self.setCursor(Qt.ClosedHandCursor)
        #QLabel.mousePressEvent(self,event)
    def mouseReleaseEvent(self,event):
        print("relase")
        self.setCursor(Qt.ArrowCursor)
        #QLabel.mouseReleaseEvent(self,event)






#重写 QpixMap
class Img(QLabel):
    Listen_KEY=Qt.Key_Control
    def __init__(self, filename,Action_type,*args, **kwargs):
        QLabel.__init__(self, *args, **kwargs)
        self.setMouseTracking(True)
        self.load_cv_img(filename)
        
        self.setStyleSheet("border: 2px solid black")
        '''
        Action_Type:确定图片处理的类型,是Wb还是Background
        value: 'WB','BKGD'
        '''
        self.Action_Type=Action_type
        print("Clean cccc")
        self.save_pos=[]
        self.Box=[]
        self.live=False
        self.Modify_img()
        self.Auto_position()
        

    def load_cv_img(self,filename):
        cv_img=cv2.imread(filename)
        self.ori_cv=cv_img
        self.show_cv=None
        
    
    def Modify_img(self,cur_pos=(),UI_Resize=False):
        print("Up_img")
        print(self.save_pos)
        UI=self.parentWidget()
        if not UI_Resize:
            img_o=self.ori_cv.copy()
            if self.save_pos and self.Action_Type=='WB':
                if len(self.save_pos)==2:
                    p1,p2=self.save_pos
                if len(self.save_pos)==1:
                    p1=self.save_pos[0]
                    p2=cur_pos
                img_new=cv2.rectangle(img_o,p1,p2,(0,255,0),2)
                self.Box=[p1,p2]
                UI.bk.Box=[p1,p2]
    
                if not self.live:
                    ####在background上面也显示box
                    if self.Action_Type=='WB':
                        #pass
                        #bkci=cv2.rectangle(UI.bk.show_cv.copy(),p1,p2,(0,255,0),2)
                        UI.bk.Display_img(UI.bk.show_cv)

                    ####显示Indicator#####
                    Box_Ind=UI.Box_Indicator
                    p1,p2=Utils().scale_point(self.scale_factor,[p1,p2])
                    ###限定在Img框内
                    x,y,w,h=p1[0]+12,p1[1]+50,p2[0]-p1[0]+2,p2[1]-p1[1]+2
                    size_w,size_h=self.width(),self.height()
                    x=x if 10 <x< size_w + 10 else 0
                    y=y if 50 <y< size_h + 50 else 0
                    w=w if w<size_w else size_w
                    h=h if h<size_h else size_h
                    Box_Ind.setGeometry(x,y,w,h)
                    Box_Ind.setStyleSheet("border: 2px solid red")


            
            if self.save_pos  and self.Action_Type == 'BKGD':
                for p in self.save_pos:
                    p1,p2=self.__get_marker_pos(p)
                    cv2.rectangle(img_o,p1,p2,(0,255,0),-1)
        if UI_Resize:
            img_o=self.show_cv        

        self.Display_img(img_o)    

        if (not cur_pos and self.Action_Type=='WB' and not UI_Resize):
            print("Clean in up_img")
            self.save_pos=[]

    def Display_img(self,cv_img):
        self.show_cv=cv_img
        if self.Action_Type=='BKGD' and self.Box:
            cv_img=cv2.rectangle(cv_img.copy(),self.Box[0],self.Box[1],(255,0,0),2)
        height, width = cv_img.shape[:2]
        currentFrame = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)    
        bytesPerline = 3 * width
        img = QImage(currentFrame, width, height, bytesPerline, QImage.Format_RGB888)    
        im=QPixmap.fromImage(img)

        UI=self.parentWidget()
        window_w,window_h=UI.width(),UI.height()
        allowed_img_w=int(window_w/2-20)
        scale_factor=allowed_img_w/width
        scale_factor=1 if scale_factor>1 else scale_factor
        self.scale_factor=scale_factor   

        new_size_w,new_size_h=int(width*scale_factor),int(height*scale_factor)
        im=im.scaled(new_size_w,new_size_h,Qt.KeepAspectRatio)
        self.resize(new_size_w,new_size_h)
        self.setPixmap(im)

    def Auto_position(self):
        self.Modify_img(UI_Resize=True)
        if self.Action_Type=='WB':
            self.move(10,50)
        if self.Action_Type=='BKGD':
            self.move(self.width()+20,50)

    def __get_marker_pos(self,midpos):
        w=150
        h=30
        w=w if w%2 else w+1
        h=h if h%2 else h+1
        p11=0 if (midpos[0]-(w-1)/2)<0 else int(midpos[0]-(w-1)/2)
        p12=0 if (midpos[1]-(h-1)/2)<0 else int(midpos[1]-(h-1)/2)
        p21=0 if (midpos[0]+(w-1)/2)<0 else int(midpos[0]+(w-1)/2)
        p22=0 if (midpos[1]+(h-1)/2)<0 else int(midpos[1]+(h-1)/2)
        return (p11,p12),(p21,p22)


    def __get_mouse_pos(self,mE):
        n = mE.button()
        t=mE.localPos()
        factor=self.scale_factor
        pos=(int(t.x()/factor),int(t.y()/factor))
        return pos

    def __get_mouse_btn(self,mouse_event):
        btn_code=mouse_event.button()
        if btn_code==Qt.LeftButton:
            return 'LEFT'
        if btn_code==Qt.RightButton:
            return 'RIGHT'
        if btn_code == Qt.MiddleButton:
            return 'MID'
        return None


    def mousePressEvent(self, event):
        mouse_btn=self.__get_mouse_btn(event)
        pos=self.__get_mouse_pos(event)
        self.live=True
        if self.Action_Type=='WB' and mouse_btn=='LEFT':
            self.save_pos.append(pos)
        
        if self.Action_Type=='BKGD' and mouse_btn=='LEFT':
            if self.parentWidget().PressedKey==self.Listen_KEY:
                pass
                #self.save_pos.append(pos)
            else:
                print("Clean in keypress block")
                self.save_pos=[]
    
    def mouseReleaseEvent(self, event):
        mouse_btn=self.__get_mouse_btn(event)
        #print(mouse_btn)
        pos=self.__get_mouse_pos(event)
        self.live=False
        if self.Action_Type=='WB' and mouse_btn=='LEFT':
            self.save_pos.append(pos)

        if self.Action_Type=='BKGD':
            
            #左键画出标记点,并且在同时按下ctrl的时候添加标记点
            if mouse_btn=='LEFT':
                if self.parentWidget().PressedKey==self.Listen_KEY:
                    self.save_pos.append(pos)
                else:
                    self.save_pos=[pos]

            ##右键删除标记点,一次删除一个
            if mouse_btn=='RIGHT':
                for i in range(len(self.save_pos)):
                    pos_1,pos_2=self.__get_marker_pos(self.save_pos[i])
                    if pos_1[0] < pos[0] < pos_2[0] and pos_1[1] < pos[1] < pos_2[1]:
                        self.save_pos.pop(i)
                        print("AA")
                        print(self.save_pos)
                        break
        self.Modify_img()

    def mouseMoveEvent(self,mE):
        pos=self.__get_mouse_pos(mE)
        mes="Image Pointer (x:%s y:%s) |Scale: %s" %(str(pos[0]),str(pos[1]),str(self.scale_factor))
        self.parentWidget().statusbar.showMessage("Ready "+ mes)
        #print(self.save_pos)
        if self.live and self.Action_Type=='WB':
            self.Modify_img(pos) 

    
##新建控件TextInput
class TextInput(QWidget):
    def __init__(self,label_name,onlylabel,*args,**kwargs):
        QWidget.__init__(self, *args, **kwargs)
        self.onlylabel=onlylabel
        self.label=QLabel(label_name,*args,**kwargs)
        if not self.onlylabel:
            self.input=LineEdit(*args, **kwargs)
            self.input.setText("10")
            #self.input.textChanged.connect(self.change)
            self.input.setMouseTracking(True)
            #self.input.wheelEvent.connect(self.roll_over)
            self.input.setValidator(QIntValidator())
        self.pos=self.label.pos

        self.UI_setting()
    
    def __get_text_pix(self):
        wid=0
        for uchar in self.label.text():
            if uchar >= u'\u4e00' and uchar<=u'\u9fa5':
                wid=wid+15
            else:
                wid=wid+10
        return wid

    def UI_setting(self):
        palette=QPalette()
        palette.setColor(QPalette.Window,Qt.blue)
        self.label.setAlignment(Qt.AlignRight)
        #self.label.setAutoFillBackground(True)
        #self.label.setPalette(palette)
        wid=self.__get_text_pix()
        self.label.resize(wid,self.label.height())
        self.label.setAlignment(Qt.AlignBottom)        
        if not self.onlylabel:
            w=80
            self.input.resize(w,self.label.height())
            #widgets.move(left,top)
            self.input.move(self.label.x()+self.label.width(), self.label.y())
    def set_label(self,label_name):
        selt.label.set_label(label_name)

    def width(self):
        if not self.onlylabel:
            return self.label.width()+self.input.width()
        else:
            return self.label.width()
    
    def height(self):
        if not self.onlylabel:
            return max(self.label.height(),self.input.height())
        else:
            return self.label.height()
    
    def move(self,new_position_x,new_position_y):
        self.label.move(new_position_x,new_position_y)
        if not self.onlylabel:
            self.input.move(new_position_x+self.label.width(),new_position_y)

    def rect(self):
        x=self.label.x()
        y=self.label.y()
        w=self.width()
        h=self.height()
        return(x,y,w,h)
    def x(self):
        return(self.label.x())
    def y(self):
        return(self.label.y())

class combine_it:
    '''
    将输入的display widgets 横向组合在一起
    '''
    def __init__(self,*args):
        hv=QHBoxLayout()
        for wid in args:
            hv.addWidget(wid)
        self.layout=hv

class label_it:
    '''
    Add label to a display object
    '''
    def __init__(self,windows,label_name,comb_odbject):
        hv=QHBoxLayout()
        label=QLabel(label_name,windows)
        hv.addWidget(label)
        hv.addWidget(comb_odbject)
        self.layout=hv
        #return hv

class ToolBar:
    '''
    Add toolbar
    '''
    def __init__(self):
        self.width=0
        self.height=0
        self.begin_pos=[10,10]
        self.end_pos=[0,10]
        self.widgets=[]
        hv=QHBoxLayout()
        self.layout=hv    

    def add(self,*args):
        for wid in args:
            wid.move(self.end_pos[0]+5,self.begin_pos[1])
            self.widgets.append(wid)
            x,y,w,h=wid.x(),wid.y(),wid.width(),wid.height()
            self.width=x+w
            self.height=max(self.height,wid.height())
            self.end_pos=[x+w,y+h]
            self.layout.addWidget(wid)

#class UI(QWidget):
class UI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_UI()
    
    def __spacer(self,width=6):
        ss=' '*6
        splice=TextInput(ss,True,self)
        return(splice)

    def init_UI(self):
        self.statusbar = self.statusBar()
        self.statusbar.showMessage('Ready')
        self.setGeometry(300, 300, 1500, 750)
        self.setWindowTitle('Statusbar')
        self.setMouseTracking(True)
        self.PressedKey=None

        toolbar=ToolBar()
        angel=TextInput("  角度:",False,self)
        angel.input.isint=False
        angel.input.setValidator(QDoubleValidator())
        self.angel=angel
        scale=TextInput("  缩放:",False,self)
        scale.input.isint=False
        scale.input.setValidator(QDoubleValidator())
        self.scale=scale
        crop=TextInput("  剪切:",True,self)
        crop_w=TextInput("宽 ",False,self)
        crop_x=TextInput(' ',True,self)
        crop_h=TextInput("高 ",False,self)
        self.crop_w=crop_w
        self.crop_h=crop_h
        marker=TextInput("Marker:",True,self)
        marker_w=TextInput("宽 ",False,self)
        marker_h=TextInput("高 ",False,self)
        self.marker_w=marker_w
        self.marker_h=marker_h
        btn_apply=QPushButton("应用",self)
        btn_save=QPushButton("保存",self)
        toolbar.add(angel,scale,crop,crop_w,crop_x,crop_h,self.__spacer(12),marker,marker_w,marker_h,self.__spacer(12),btn_apply,btn_save)
        
        hv=QHBoxLayout()
        self.wb=Img("blot.tif",'WB',self)
        self.bk=Img("background.tif","BKGD",self)
        self.Box_Indicator=Indicator(self)
        #self.Box_Indicator.setStyleSheet("border: 2px solid black")
        #hv.addWidget(wb)
        #hv.addWidget(self.Box_Indicator)    
        #ss=QVBoxLayout()
        #ss.addLayout(toolbar.layout)
        #ss.addLayout(hv)
        #self.setLayout(hv)
           
        self.show()
    
    def resizeEvent(self,event):
        self.bk.Auto_position()
        self.wb.Auto_position()
        self.scale.input.setEnabled(False)
        self.scale.input.setText(str(self.wb.scale_factor)[0:5])
        #event.accept()

    def mouseMoveEvent(self,mE):
        t=mE.localPos()
        mes=" Pointer x:%s y:%s" %(str(t.x()),str(t.y()))
        self.statusbar.showMessage("Ready "+ mes)

    def keyPressEvent(self,event):
        self.PressedKey=event.key()
        QMainWindow.keyPressEvent(self,event)
    def keyReleaseEvent(self,event):
        self.PressedKey=None
        QMainWindow.keyReleaseEvent(self,event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = UI()
    sys.exit(app.exec_())