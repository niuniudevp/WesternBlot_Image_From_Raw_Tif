import sys
from GUI import UI
from PyQt5.QtWidgets import QApplication
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = UI()
    ex.show()
    sys.exit(app.exec_())