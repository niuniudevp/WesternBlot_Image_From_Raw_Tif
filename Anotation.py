from PyQt5.QtWidgets import QLineEdit, QFrame, QHBoxLayout, QComboBox, QPushButton, QGridLayout
from Base import LabeledInPut
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPainter, QPen
from Utils import Get_Super_Parent, QImage_to_CV_Img
from bound_detect import bound_from_cv_img


class Magic_Input(QLineEdit):
    def __init__(self, *args, **kwargs):
        QLineEdit.__init__(self, *args, **kwargs)
        self.textEdited.connect(self.update)
        self.Actived = False

    def paintEvent(self, event):
        text = self.text()
        qp = QPainter()
        qp.begin(self)
        if text == "@--":
            self.setFrame(False)
            pen = QPen(Qt.black, 2, Qt.SolidLine)
            qp.setPen(pen)
            half = int(self.height() / 2)
            qp.drawText(event.rect(), Qt.AlignCenter, "AVC")
            qp.drawLine(0, half, self.width(), half)
            #self.setText("")
        if text == "@>":
            pass
        if text == "@<":
            pass
        qp.end()
        QLineEdit.paintEvent(self, event)

    def focusInEvent(self, event):
        P = Get_Super_Parent(self)
        All_Magic_input = P.findChildren(Magic_Input)
        for t in All_Magic_input:
            t.Actived = False
            #t.setFixedSize(t.width(), t.height())
            t.setStyleSheet('border:1px solid red')
        self.Actived = True
        self.setStyleSheet('border: 2px solid green')


class Anotation(QFrame):
    # 增加注释功能

    def __init__(self, *args, **kwargs):
        QFrame.__init__(self, *args, **kwargs)
        self.Label = ""
        self.Inputs =[]
        #hv = QHBoxLayout()
        hv = QGridLayout()
        hv.setContentsMargins(0, 0, 0, 0)
        hv.setSpacing(0)
        self.setLayout(hv)
        self.resize(500, 30)
        self.setStyleSheet("border: 1px solid red")

    def SetColumn(self, split: list, start_pos, end_pos):
        """
        逗号分割各个部分的比例
        """
        space_list = split[1]
        split_str = split[0]
        
        ly = self.layout()
        self.start_pos = start_pos
        self.end_pos = end_pos
        
        for i in range(len(space_list)):
            wid = int(space_list[i])
            t = Magic_Input(self)
            t.setAlignment(Qt.AlignCenter)
            t.setMaximumWidth(wid)
            ly.addWidget(t, 0, i, 1, split_str[i], Qt.AlignCenter)
            ly.setColumnStretch(i, wid)
        """
        for i in range(len(space_list)-1):
            t = Magic_Input(self)
            t.show()
            t.setGeometry(space_list[i], 15, space_list[i+1] - space_list[i], 30)
            #ly.addWidget(t)
            self.Inputs.append(t)
        """

    def SetFont(self, QFont):
        for item in self.layout().count:
            pass

    def SetFontSize(self, font_size):
        pass

    def SetBold(self):
        pass

    def SetItalic(self):
        pass


class Text_Act_Btn(QFrame):
    Action_Signal = pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        QFrame.__init__(self, *args, **kwargs)
        self.UI()
        self.signals()

    def UI(self):
        hv = QHBoxLayout()
        self.Action_Type = QComboBox(self)
        self.Action_Type.addItem('Cell')
        self.Action_Type.addItem('Row')
        self.Btn_MoveLeft = QPushButton("<<<", self)
        self.Btn_MoveRight = QPushButton(">>>", self)
        self.Btn_Larger = QPushButton(" + ", self)
        self.Btn_Smaller = QPushButton(" - ", self)
        self.Rotation = LabeledInPut("Rotation: ", 0, self)
        hv.addWidget(self.Action_Type)
        hv.addWidget(self.Btn_MoveLeft)
        hv.addWidget(self.Btn_Larger)
        hv.addWidget(self.Btn_Smaller)
        hv.addWidget(self.Btn_MoveRight)
        hv.addWidget(self.Rotation)
        self.setLayout(hv)

    def signals(self):
        self.Btn_MoveLeft.clicked.connect(self.Send_Signal)
        self.Btn_MoveRight.clicked.connect(self.Send_Signal)
        self.Btn_Larger.clicked.connect(self.Send_Signal)
        self.Btn_Smaller.clicked.connect(self.Send_Signal)
        self.Rotation.Changed_Signal.connect(self.Send_Signal)

    def Send_Signal(self):
        sender = self.sender()
        target_is_cell = self.Action_Type.currentText() == 'Cell'
        if sender == self.Btn_MoveLeft:
            if target_is_cell:
                self.Action_Signal.emit('<')
            else:
                self.Action_Signal.emit('0<')
        if sender == self.Btn_MoveRight:
            if target_is_cell:
                self.Action_Signal.emit('>')
            else:
                self.Action_Signal.emit('0>')
        if sender == self.Btn_Larger:
            if target_is_cell:
                self.Action_Signal.emit('+')
            else:
                self.Action_Signal.emit('0+')
        if sender == self.Btn_Smaller:
            if target_is_cell:
                self.Action_Signal.emit('-')
            else:
                self.Action_Signal.emit('0-')
        if sender == self.Rotation:
            angel = self.Rotation.Value()
            self.Action_Signal.emit(angel)
