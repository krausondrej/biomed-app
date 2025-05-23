# ui_helpers.py
from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout
from PyQt5 import QtCore

class CollapsibleSection(QWidget):
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        # tlačítko, které se dá stisknout
        self.toggle_button = QPushButton(title)
        self.toggle_button.setStyleSheet("""
            QPushButton {
                background-color: black;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #636564;
            }
        """)
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(False)
        # kontejner na obsah, který schováváme/rozbalujeme
        self.content_area = QWidget()
        self.content_area.setVisible(False)

        # samotné layouty
        main_lay = QVBoxLayout(self)
        main_lay.setContentsMargins(0, 0, 0, 0)
        main_lay.setSpacing(0)
        main_lay.addWidget(self.toggle_button)
        main_lay.addWidget(self.content_area)

        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)

        # bindnutí viditelnosti
        self.toggle_button.toggled.connect(self.content_area.setVisible)

    def add_widget(self, widget: QWidget):
        """Přidá libovolný widget (graf, tabulku…) do rozbalitelné oblasti."""
        self.content_layout.addWidget(widget)
