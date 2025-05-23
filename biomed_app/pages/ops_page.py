# pages/ops_page.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5 import QtCore

class OpsPage(QWidget):
    def __init__(self, main_win):
        super().__init__()
        self.main = main_win
        lay = QVBoxLayout(self)

        lbl = QLabel("SELECT HERNIA OPERATION TYPE")
        lbl.setObjectName("titleLabel")
        lbl.setAlignment(QtCore.Qt.AlignCenter)
        lay.addWidget(lbl)

        ops = [
            ("GHR","Groin Hernia Repair"),
            ("PHR","Parastomal Hernia Repair"),
            ("IVHR","Incisional Ventral Hernia Repair"),
            ("PVHR","Primary Ventral Hernia Repair")
        ]
        for code, text in ops:
            btn = QPushButton(f"{code}: {text}")
            # místo _navigate používej show_year_page
            btn.clicked.connect(lambda _, c=code: self.main.show_year_page(c))
            lay.addWidget(btn)
