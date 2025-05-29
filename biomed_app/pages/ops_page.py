# pages/ops_page.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QGridLayout, QHBoxLayout
)
from PyQt5 import QtCore


class OpsPage(QWidget):
    def __init__(self, main_win):
        super().__init__()
        self.main = main_win

        # Hlavní vertikální layout, do kterého vložíme stretch, obsah a další stretch
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(40, 20, 40, 20)
        root_layout.setSpacing(20)

        # Horní stretch pro vertikální centrování
        root_layout.addStretch()

        # Content layout – sem dáme titulek, podtitul a grid
        content_layout = QVBoxLayout()
        content_layout.setSpacing(20)

        # Titulek
        title = QLabel("SELECT HERNIA OPERATION TYPE")
        title.setObjectName("titleLabel")
        title.setAlignment(QtCore.Qt.AlignCenter)
        content_layout.addWidget(title)

        # Podtitul
        subtitle = QLabel("Select the hernia type you want to analyze")
        subtitle.setObjectName("subtitleLabel")
        subtitle.setAlignment(QtCore.Qt.AlignCenter)
        content_layout.addWidget(subtitle)

        # Grid 2×2 pro tlačítka
        grid = QGridLayout()
        grid.setHorizontalSpacing(30)
        grid.setVerticalSpacing(20)

        ops = [
            ("GHR", "Groin Hernia Repair"),
            ("PHR", "Parastomal Hernia Repair"),
            ("IVHR", "Incisional Ventral Hernia Repair"),
            ("PVHR", "Primary Ventral Hernia Repair")
        ]
        for idx, (code, text) in enumerate(ops):
            btn = QPushButton(f"{code}: {text}")
            btn.setObjectName("opButton")
            btn.setFixedHeight(60)
            btn.clicked.connect(lambda _, c=code: self.main.show_year_page(c))
            row, col = divmod(idx, 2)
            grid.addWidget(btn, row, col)

        # Obalíme grid do HBox se stretch pro horizontální centrování
        hbox = QHBoxLayout()
        hbox.addStretch()
        hbox.addLayout(grid)
        hbox.addStretch()
        content_layout.addLayout(hbox)

        # Přidáme content_layout do root_layout
        root_layout.addLayout(content_layout)

        # Dolní stretch pro vertikální centrování
        root_layout.addStretch()

        # Stylování
        self.setStyleSheet("""
            #titleLabel {
                font-size: 24px;
                font-weight: bold;
            }
            #subtitleLabel {
                font-size: 14px;
            }
            QPushButton#opButton {
                font-size: 16px;
                text-align: left;
                padding-left: 15px;
                background-color: #FFFFFF;
                border: 1px solid #CCCCCC;
                border-radius: 8px;
                min-width: 200px;
                color: #333333;
            }
            QPushButton#opButton:hover {
                background-color: #F0F0F0;
            }
            QPushButton#opButton:pressed {
                background-color: #E0E0E0;
            }
        """)