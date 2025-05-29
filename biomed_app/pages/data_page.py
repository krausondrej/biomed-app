# pages/data_page.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QGridLayout, QHBoxLayout
)
from PyQt5 import QtCore

class DataPage(QWidget):
    def __init__(self, main_win):
        super().__init__()
        self.main = main_win

        # Hlavní layout s vertikálním centrováním
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(40, 20, 40, 20)
        root_layout.setSpacing(20)
        root_layout.addStretch()  # horní mezera

        # Obsahová část
        content_layout = QVBoxLayout()
        content_layout.setSpacing(15)

        # Titulek
        title = QLabel("SELECT DATA CATEGORY")
        title.setObjectName("dataTitle")
        title.setAlignment(QtCore.Qt.AlignCenter)
        content_layout.addWidget(title)

        # Podtitulek (rok + typ operace)
        self.lbl = QLabel("")  
        self.lbl.setObjectName("dataSubtitle")
        self.lbl.setAlignment(QtCore.Qt.AlignCenter)
        content_layout.addWidget(self.lbl)

        # Grid tlačítek – 2 sloupce
        categories = [
            "Preoperative data",
            "Operative data",
            "Postoperative data (hospitalization)",
            "Long-term postoperative data"
        ]
        grid = QGridLayout()
        grid.setHorizontalSpacing(30)
        grid.setVerticalSpacing(20)

        for idx, cat in enumerate(categories):
            btn = QPushButton(cat)
            btn.setObjectName("dataButton")
            btn.setFixedHeight(50)
            btn.clicked.connect(lambda _, c=cat: self.main.show_category_page(c))
            row, col = divmod(idx, 2)
            grid.addWidget(btn, row, col)

        # Obalený grid pro horizontální centrování
        hbox = QHBoxLayout()
        hbox.addStretch()
        hbox.addLayout(grid)
        hbox.addStretch()
        content_layout.addLayout(hbox)

        # Přidáme content a dolní mezera
        root_layout.addLayout(content_layout)
        root_layout.addStretch()

        # Společné stylování
        self.setStyleSheet("""
            /* Title */
            #dataTitle {
                font-size: 24px;
                font-weight: bold;
            }
            /* Subtitle: current op type + year */
            #dataSubtitle {
                font-size: 14px;
            }
            /* Category buttons */
            QPushButton#dataButton {
                font-size: 16px;
                text-align: left;
                padding-left: 15px;
                background-color: #FFFFFF;
                border: 1px solid #CCCCCC;
                border-radius: 8px;
                min-width: 220px;
                color: #333333;
            }
            QPushButton#dataButton:hover {
                background-color: #F5F5F5;
            }
            QPushButton#dataButton:pressed {
                background-color: #E0E0E0;
            }
        """)

    def update_view(self):
        """Aktualizuje podtitulek podle vybraného typu operace a roku."""
        op = self.main.current_op_type or "—"
        yr = self.main.selected_year     or "—"
        self.lbl.setText(f"Operation: {op}   |   Year: {yr}")
