import sys, os
from GUI import UI
from PyQt5.QtWidgets import QApplication


if __name__ == '__main__':
    try:
        #os.environ['QT_SCREEN_SCALE_FACTORS'] = '2'
        app = QApplication(sys.argv)
        ex = UI()
        ex.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(e)
