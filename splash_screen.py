# splash_screen.py
import os
import sys
from PyQt5.QtWidgets import QSplashScreen, QLabel, QWidget, QVBoxLayout
from PyQt5.QtGui import QMovie
from PyQt5.QtCore import Qt

if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.abspath(".")


class SplashScreen(QSplashScreen):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setStyleSheet("background-color: white;")
        self.setFixedSize(300, 300)
        self.center_on_screen()

        container = QWidget(self)
        container.setGeometry(0, 0, 300, 300)

        layout = QVBoxLayout(container)
        layout.setAlignment(Qt.AlignCenter)

        self.label = QLabel()
        gif_path = os.path.join(base_path,
                                "resources", "loading.gif")
        self.movie = QMovie(gif_path)
        self.label.setMovie(self.movie)
        self.movie.start()

        self.text = QLabel("Loading data...")
        self.text.setAlignment(Qt.AlignCenter)
        self.text.setStyleSheet("font-size: 16px;")

        layout.addWidget(self.label)
        layout.addWidget(self.text)

    def center_on_screen(self):
        screen = self.screen().geometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2
        )
