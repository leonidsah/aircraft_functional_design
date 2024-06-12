import sys

from PyQt5.QtWidgets import QApplication

from qt_gui.gui import MainUI

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = MainUI()
    ui.show()
    app.exec_()
