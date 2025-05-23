# main.py
import sys
import os
from PyQt5.QtWidgets import QApplication
from pages.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    # načíst QSS relativně k main.py
    base = os.path.dirname(os.path.abspath(__file__))
    qss  = os.path.join(base, "resources", "style.qss")
    with open(qss, encoding="utf-8") as f:
        app.setStyleSheet(f.read())

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
