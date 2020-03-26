from PyQt5.QtWidgets import QScrollArea, QLabel
from PyQt5.QtCore import Qt, QSize, QRectF, pyqtSlot
from PyQt5.QtGui import QFont, QPainter, QPen, QColor, QPixmap, QImage
from Utils import CV_Img_to_QImage
import cv2


class Realtime_PreView_Img(QScrollArea):
    def __init__(self, *args, **kwargs):
        QScrollArea.__init__(self, *args, **kwargs)
        self.View_Info = None
        self.View_Scale = 1
        self.Add_Border = True
        self.Info_L_Most = 0
        self.Info_T_Most = 0
        self.Info_R_Most = 0
        self.Info_B_Most = 0
        self.draw_text = []  # {'text':#,'font':#,'rect':#}
        self.draw_marker = []  # {'rect':#}
        self.draw_Img = []  # {'rect':#}
        self.draw_rec = []  # {'rect':#}
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
        self.draw_text = []  # {'text':#,'font':#,'rect':#}
        self.draw_marker = []  # {'rect':#}
        self.draw_Img = []  # {'rect':#}
        self.draw_rec = []  # {'rect':#}
        self.Spacer = '  '
        self.crop_Center = 0 # 剪切中心
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
            self.crop_Center = 2 * m_x + m_w

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

        # 调整L_Most 和R_Most 使其始终关于剪切图片中心对称
        crop_Center = self.crop_Center

        if crop_Center:
            if self.Info_L_Most + self.Info_R_Most - crop_Center > 0:
            # 需要增加左侧
                self.Info_L_Most -= self.Info_R_Most - crop_Center + self.Info_L_Most
            else:
            # 需要增加右侧
                self.Info_R_Most += crop_Center - self.Info_L_Most - self.Info_R_Most

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
            pt.drawRect(QRectF(x, y, w, h))

        for m in self.draw_marker:
            pt.setBrush(QColor(0, 0, 0))
            x, y, w, h = self.rect_fix(m['rect'])
            pt.fillRect(x, y, w, h, QColor(0, 0, 0))

        for p in self.draw_Img:
            im, _ = CV_Img_to_QImage(self.View_Info['src_img'], 1,
                                     self.View_Info['rotation'],
                                     self.View_Info['Flip_h'],
                                     self.View_Info['Flip_v'])
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
        self.PreView_Img = Img
        self.View.adjustSize()

