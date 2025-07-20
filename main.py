# main.py
import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from pages.main_window import MainWindow
from splash_screen import SplashScreen

if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.abspath(".")

excel_path = os.path.join(base_path, "ExportedData.xlsx")
style_path = os.path.join(base_path, "resources", "style.qss")


def start_main_window():
    window = MainWindow()
    window.show()
    splash.finish(window)


def main():
    app = QApplication(sys.argv)

    base = os.path.dirname(os.path.abspath(__file__))
    qss = os.path.join(base, style_path)
    with open(qss, encoding="utf-8") as f:
        app.setStyleSheet(f.read())

    global splash
    splash = SplashScreen()
    splash.show()

    QTimer.singleShot(2000, start_main_window)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
