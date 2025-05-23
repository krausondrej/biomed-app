# pages/discharge_page.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea
from PyQt5 import QtCore
from ui_helpers import CollapsibleSection
from chart_utils import make_bar_chart
from table_utils import make_stats_table

class DischargePage(QWidget):
    def __init__(self, main_win, df):
        super().__init__()
        self.main = main_win
        self.df   = df
        self._build_ui()

    def _build_ui(self):
        lay = QVBoxLayout(self)

        lbl = QLabel("Intrahospital Complications")
        lbl.setObjectName("titleLabel")
        lbl.setAlignment(QtCore.Qt.AlignCenter)
        lay.addWidget(lbl)

        self.header = QLabel()
        self.header.setAlignment(QtCore.Qt.AlignCenter)
        lay.addWidget(self.header)

        # ScrollArea s transparentním pozadím a černým scrollbar handle
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 12px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background: #000000;
                min-height: 20px;
                border-radius: 6px;
            }
            QScrollBar::sub-line:vertical,
            QScrollBar::add-line:vertical {
                height: 0;
            }
            QScrollBar::sub-page:vertical,
            QScrollBar::add-page:vertical {
                background: none;
            }
        """)
        # viewport (obsahová plocha) průhledná
        scroll.viewport().setStyleSheet("background: transparent;")
        scroll.viewport().setAttribute(QtCore.Qt.WA_TranslucentBackground)

        # Kontejner uvnitř ScrollArea také průhledný
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        container.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        # Layout pro obsah
        self.vlay = QVBoxLayout(container)
        self.vlay.setSpacing(20)
        self.vlay.setAlignment(QtCore.Qt.AlignTop)
        
        scroll.setWidget(container)
        lay.addWidget(scroll)


    def update_view(self):
        ty = self.main.current_op_type or "All types"
        yr = self.main.selected_year   or "All years"
        self.header.setText(f"Type: {ty} ┃ Year: {yr}")

        # vyčistit předchozí obsah
        for i in reversed(range(self.vlay.count())):
            w = self.vlay.itemAt(i).widget()
            if w:
                w.setParent(None)

        # filtrování podle roku
        df = self.df.copy()
        if yr != "2021-2025":
            try:
                df = df[df["Year"] == int(yr)]
            except ValueError:
                pass

        if df.empty:
            lbl = QLabel("No discharge data for selected year.")
            lbl.setAlignment(QtCore.Qt.AlignCenter)
            self.vlay.addWidget(lbl)
            return

        # 1) Occurrence of Intrahospital Complications
        occ_counts = df["ComplicationOccurrence"] \
                        .map({0: "No", 1: "Yes"}) \
                        .value_counts()
        sec1 = CollapsibleSection("Occurrence of Intrahospital Complications")
        sec1.add_widget(make_bar_chart(
            occ_counts,
            "Occurrence of Intrahospital Complications",
            "Occurrence",
            "Count"
        ))
        self.vlay.addWidget(sec1)

        # 2) Type of Intrahospital Complications
        type_counts = df["ComplicationType"] \
                          .fillna("None") \
                          .value_counts()
        sec2 = CollapsibleSection("Type of Intrahospital Complications")
        sec2.add_widget(make_bar_chart(
            type_counts,
            "Type of Intrahospital Complications",
            "Complication Type",
            "Count"
        ))
        self.vlay.addWidget(sec2)

        # 3) Summary Statistics
        stats = {
            "Total patients":                len(df),
            "Complications (Yes)":           occ_counts.get("Yes", 0),
            "Complications (No)":            occ_counts.get("No", 0),
            "Distinct complication types":   len(type_counts)
        }
        sec3 = CollapsibleSection("Summary Statistics")
        sec3.add_widget(make_stats_table(stats))
        self.vlay.addWidget(sec3)