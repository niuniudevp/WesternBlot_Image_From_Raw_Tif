from PyQt5.QtWidgets import QFrame, QGridLayout
from Image_Block import Img_Block
from Preview import Realtime_PreView_Img
from Utils import Get_Super_Parent


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
        self.Pre = Realtime_PreView_Img(self)
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

