import os
import re


class BioRad_Imgs():
    """
    处理BioRad仪器的导出图片显示情况
    实现功能，根据传入的图片，查找同级目录，上级目录，以及与文件名称相同的下级目录里面的图片
    并判断返回WB图片，背景图片
    """
    def __init__(self, img_path):
        self.Current_Img = img_path
        Path, Img = os.path.split(img_path)
        _, ext = os.path.splitext(img_path)
        self.Dir = Path
        self.Img = Img
        self.ext = ext
        self.Name_Pattern = re.findall(r'(.+)_\d', Img)[0]
        self.WB_list = []
        self.BKGD_list = []
        self.search_same_files(self.Dir)
        self.wb_index = self.WB_list.index(os.path.join(Path, Img)) if 'Chemiluminescence' in Img else 0
        self.bkgd_index = self.BKGD_list.index(os.path.join(Path, Img)) if 'Colorimetric' in Img else 0
    
    def search_same_files(self, Dir):
        Sub_Dir = []
        pattern_list = [p for p in os.listdir(Dir) if self.Name_Pattern in p]
        for item in pattern_list:
            t = os.path.join(Dir, item)
            if 'Chemiluminescence)' + self.ext in item:
                self.WB_list.append(t)
            if 'Colorimetric)' + self.ext in item:
                self.BKGD_list.append(t)
            if os.path.isdir(t):
                Sub_Dir.append(t)
        for d in Sub_Dir:
            self.search_same_files(d)

