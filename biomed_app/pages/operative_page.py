import pandas as pd
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea
from PyQt5 import QtCore
from ui_helpers import CollapsibleSection
from chart_utils import make_bar_chart, make_histogram
from table_utils import make_stats_table

class OperativePage(QWidget):
    def __init__(self, main_win, df):
        super().__init__()
        self.main = main_win
        self.df   = df
        self._build_ui()

    def _build_ui(self):
        lay = QVBoxLayout(self)

        lbl = QLabel("Operative Data – Visualization and Table")
        lbl.setObjectName("titleLabel")
        lbl.setAlignment(QtCore.Qt.AlignCenter)
        lay.addWidget(lbl)

        self.header = QLabel("")
        self.header.setAlignment(QtCore.Qt.AlignCenter)
        lay.addWidget(self.header)

        # ScrollArea with transparent background and black scrollbar
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            /* Container transparent */
            QScrollArea { background: transparent; border: none; }
            /* Track */
            QScrollBar:vertical { background: transparent; width: 12px; margin: 0; }
            /* Handle */
            QScrollBar::handle:vertical { background: #000000; min-height: 20px; border-radius: 6px; }
            /* Hide arrows */
            QScrollBar::sub-line:vertical, QScrollBar::add-line:vertical { height: 0; }
            /* Empty areas */
            QScrollBar::sub-page:vertical, QScrollBar::add-page:vertical { background: none; }
        """)
        scroll.viewport().setStyleSheet("background: transparent;")
        scroll.viewport().setAttribute(QtCore.Qt.WA_TranslucentBackground)

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        container.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.vlay = QVBoxLayout(container)
        self.vlay.setSpacing(20)
        self.vlay.setAlignment(QtCore.Qt.AlignTop)

        scroll.setWidget(container)
        lay.addWidget(scroll)

    def update_view(self):
        # clear previous widgets
        for i in reversed(range(self.vlay.count())):
            w = self.vlay.itemAt(i).widget()
            if w:
                w.setParent(None)

        ty = self.main.current_op_type
        yr_sel = self.main.selected_year

        # filter dataframe
        df = self.df.copy()
        if isinstance(yr_sel, str) and '-' in yr_sel:
            start, end = map(int, yr_sel.split('-'))
            df = df[df['Year'].between(start, end)]
        else:
            try:
                yr = int(yr_sel)
                df = df[df['Year'] == yr]
            except Exception:
                pass

        # update header
        self.header.setText(f"Operace: {ty}   |   Rok: {yr_sel}   |   Počet záznamů: {len(df)}")

        # 1) Indication for Surgery
        sec1 = CollapsibleSection("Indication for Surgery")
        sec1.add_widget(make_bar_chart(
            df["Indication"].value_counts(),
            "Indication for Surgery", "Indication", "Count"
        ))
        self.vlay.addWidget(sec1)

        # 2) Type-specific sections
        if ty == "GHR":
            # Side of the Hernia – Right
            sec2 = CollapsibleSection("Side of the Hernia – Right")
            sec2.add_widget(make_bar_chart(
                df["GHR_Side_Right"].fillna("Unknown").value_counts(),
                "Side of the Hernia (Right)", "Side", "Count"
            ))
            self.vlay.addWidget(sec2)

            # Side of the Hernia – Left
            sec3 = CollapsibleSection("Side of the Hernia – Left")
            sec3.add_widget(make_bar_chart(
                df["GHR_Side_Left"].fillna("Unknown").value_counts(),
                "Side of the Hernia (Left)", "Side", "Count"
            ))
            self.vlay.addWidget(sec3)

            # Previous Repairs (Right)
            sec4 = CollapsibleSection("Previous Repairs (Right)")
            sec4.add_widget(make_bar_chart(
                df["GHR_Prev_Repairs_Right"].fillna(0).astype(int).value_counts().sort_index(),
                "Previous Repairs (Right)", "Number of Repairs", "Count"
            ))
            self.vlay.addWidget(sec4)

            # Previous Repairs (Left)
            sec5 = CollapsibleSection("Previous Repairs (Left)")
            sec5.add_widget(make_bar_chart(
                df["GHR_Prev_Repairs_Left"].fillna(0).astype(int).value_counts().sort_index(),
                "Previous Repairs (Left)", "Number of Repairs", "Count"
            ))
            self.vlay.addWidget(sec5)

            # Groin Hernia Type (Right)
            sec6 = CollapsibleSection("Groin Hernia Type (Right)")
            sec6.add_widget(make_bar_chart(
                df[["GHR_Type_Right_Lateral", "GHR_Type_Right_Medial", "GHR_Type_Right_Femoral", "GHR_Type_Right_Obturator"]]
                  .fillna("Unknown").stack().value_counts(),
                "Groin Hernia Type (Right)", "Hernia Type", "Count"
            ))
            self.vlay.addWidget(sec6)

            # Groin Hernia Type (Left)
            sec7 = CollapsibleSection("Groin Hernia Type (Left)")
            sec7.add_widget(make_bar_chart(
                df[["GHR_Type_Left_Lateral", "GHR_Type_Left_Medial", "GHR_Type_Left_Femoral", "GHR_Type_Left_Obturator"]]
                  .fillna("Unknown").stack().value_counts(),
                "Groin Hernia Type (Left)", "Hernia Type", "Count"
            ))
            self.vlay.addWidget(sec7)

        elif ty == "PHR":
            sec2 = CollapsibleSection("Type of Stoma")
            sec2.add_widget(make_bar_chart(
                df["PHR_Stoma_Type"].fillna("Unknown").value_counts(),
                "Type of Stoma", "Stoma Type", "Count"
            ))
            self.vlay.addWidget(sec2)

            sec3 = CollapsibleSection("Number of Previous Repairs")
            sec3.add_widget(make_bar_chart(
                df["PHR_Prev_Repairs"].fillna(0).astype(int).value_counts().sort_index(),
                "Number of Previous Repairs", "Number of Repairs", "Count"
            ))
            self.vlay.addWidget(sec3)

        elif ty == "PVHR":
            sec2 = CollapsibleSection("PVHR Type Specification")
            sec2.add_widget(make_bar_chart(
                df["PVHR_Subtype"].fillna("Unknown").value_counts(),
                "PVHR Type Specification", "PVHR Type", "Count"
            ))
            self.vlay.addWidget(sec2)

        elif ty == "IVHR":
            sec2 = CollapsibleSection("Number of Previous Hernia Repairs")
            sec2.add_widget(make_bar_chart(
                df["IVHR_Prev_Repairs"].fillna(0).astype(int).value_counts().sort_index(),
                "Number of Previous Hernia Repairs", "Number of Repairs", "Count"
            ))
            self.vlay.addWidget(sec2)

        # 3) Summary Statistics
        stats = {"Total ops": len(df)}
        tbl_sec = CollapsibleSection("Summary Statistics")
        tbl_sec.add_widget(make_stats_table(stats))
        self.vlay.addWidget(tbl_sec)
