# ui_helpers.py
from PyQt5.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, QSizePolicy, QFileDialog
)

class CollapsibleSection(QWidget):
    def __init__(self, title: str, parent=None):
        super().__init__(parent)

        # tlačítko s šipkou
        self.toggle_button = QPushButton(f"▶  {title}")
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(False)
        self.toggle_button.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #333333;
                font-size: 16px;
                font-weight: bold;
                text-align: left;
                border: 1px solid #333333;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #F5F5F5;
            }
        """)
        self.toggle_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # obsahová oblast, původně skrytá
        self.content_area = QWidget()
        # content area zabírá výšku podle obsahu, ale při collapse se nastaví maxHeight
        self.content_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.content_area.setVisible(False)
        self.content_area.setMaximumHeight(0)

        # layout celé sekce
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.main_layout.addWidget(self.toggle_button)
        self.main_layout.addWidget(self.content_area)

        # layout pro vložené widgety
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(5)

        # spojení: přepíná viditelnost a výšku
        self.toggle_button.toggled.connect(self._on_toggled)

    def _on_toggled(self, checked: bool):
        arrow = "▼" if checked else "▶"
        text = self.toggle_button.text().split("  ", 1)[-1]
        self.toggle_button.setText(f"{arrow}  {text}")

        if checked:
            # expand: zjistit ideální výšku podle obsahu
            self.content_area.setVisible(True)
            full_h = self.content_area.sizeHint().height()
            self.content_area.setMaximumHeight(full_h)
        else:
            # collapse: skrytí a nastavení maxHeight na 0
            self.content_area.setMaximumHeight(0)
            self.content_area.setVisible(False)

    def add_widget(self, widget: QWidget):
        """Přidá widget (graf, tabulku…) do rozbalitelné oblasti."""
        self.content_layout.addWidget(widget)
        
def add_download_button(canvas, label="Download graph"):
    container = QWidget()
    layout = QVBoxLayout()
    container.setLayout(layout)

    layout.addWidget(canvas)

    btn = QPushButton(label)
    layout.addWidget(btn)

    def save_graph():
        file_path, _ = QFileDialog.getSaveFileName(
            None,
            "Save Graph",
            "",
            "PNG Files (*.png);;All Files (*)"
        )
        if file_path:
            canvas.figure.savefig(file_path)

    btn.clicked.connect(save_graph)
    return container
