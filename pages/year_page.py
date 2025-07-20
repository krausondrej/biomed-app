# pages/year_page.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QHBoxLayout
)
from PyQt5 import QtCore


class YearPage(QWidget):
    def __init__(self, main_win):
        super().__init__()
        self.main = main_win

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(40, 20, 40, 20)
        root_layout.setSpacing(20)
        root_layout.addStretch()

        content_layout = QVBoxLayout()
        content_layout.setSpacing(20)

        title = QLabel("SELECT YEAR")
        title.setObjectName("yearTitle")
        title.setAlignment(QtCore.Qt.AlignCenter)
        content_layout.addWidget(title)

        self.lbl = QLabel("")
        self.lbl.setObjectName("yearSubtitle")
        self.lbl.setAlignment(QtCore.Qt.AlignCenter)
        content_layout.addWidget(self.lbl)

        years = ["2021-2025", "2021", "2022", "2023", "2024", "2025"]
        for yr in years:
            btn = QPushButton(yr)
            btn.setObjectName("yearButton")
            btn.setFixedHeight(50)
            btn.clicked.connect(lambda _, y=yr: self.main.show_data_page(y))

            hbox = QHBoxLayout()
            hbox.addStretch()
            hbox.addWidget(btn)
            hbox.addStretch()

            content_layout.addLayout(hbox)

        root_layout.addLayout(content_layout)
        root_layout.addStretch()

        self.setStyleSheet("""
            /* Titulek */
            #yearTitle {
                font-size: 24px;
                font-weight: bold;
            }
            /* Podtitulek (zobrazuje typ operace) */
            #yearSubtitle {
                font-size: 16px;
            }
            /* Tlačítka pro roky */
            QPushButton#yearButton {
                font-size: 16px;
                padding: 10px 20px;
                background-color: #FFFFFF;
                border: 1px solid #CCCCCC;
                border-radius: 8px;
                min-width: 150px;
                color: #333333;
            }
            QPushButton#yearButton:hover {
                background-color: #F0F0F0;
            }
            QPushButton#yearButton:pressed {
                background-color: #E0E0E0;
            }
        """)
