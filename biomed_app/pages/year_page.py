# pages/year_page.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5 import QtCore

class YearPage(QWidget):
    def __init__(self, main_win):
        super().__init__()
        self.main = main_win
        lay = QVBoxLayout(self)

        # tady se bude vykreslovat selected type
        self.lbl = QLabel("")
        self.lbl.setAlignment(QtCore.Qt.AlignCenter)
        lay.addWidget(self.lbl)

        for yr in ["2021-2025","2021","2022","2023","2024","2025"]:
            btn = QPushButton(yr)
            # místo přímého navigate používej show_data_page
            btn.clicked.connect(lambda _, y=yr: self.main.show_data_page(y))
            lay.addWidget(btn)
