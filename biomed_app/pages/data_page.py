# pages/data_pages.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5 import QtCore

class DataPage(QWidget):
    def __init__(self, main_win):
        super().__init__()
        self.main = main_win
        lay = QVBoxLayout(self)

        self.lbl = QLabel("")               # sem se může psát rok, typ
        self.lbl.setAlignment(QtCore.Qt.AlignCenter)
        lay.addWidget(self.lbl)

        cats = [
            "Preoperative data",
            "Operative data",
            "Postoperative data (hospitalization)",
            "Long-term postoperative data"
        ]
        for cat in cats:
            btn = QPushButton(cat)
            # místo přímého navigate používej show_category_page
            btn.clicked.connect(lambda _, c=cat: self.main.show_category_page(c))
            lay.addWidget(btn)
