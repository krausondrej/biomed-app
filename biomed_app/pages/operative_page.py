# pages/operative_page.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QDateEdit
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

        self.header = QLabel()
        self.header.setAlignment(QtCore.Qt.AlignCenter)
        lay.addWidget(self.header)

        # datumový rozsah
        self.date_from = QDateEdit(calendarPopup=True)
        self.date_to   = QDateEdit(calendarPopup=True)
        self.date_from.setDate(QtCore.QDate(self.df["OperationDate"].min(), 1, 1))
        self.date_to.setDate(QtCore.QDate(self.df["OperationDate"].max(), 12, 31))
        self.date_from.dateChanged.connect(self.update_view)
        self.date_to.dateChanged.connect(self.update_view)

        # ScrollArea s průhledným pozadím a černým scrollbarem
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            /* Obal scroll oblasti průhledný */
            QScrollArea {
                background: transparent;
                border: none;
            }
            /* Track scrollbaru */
            QScrollBar:vertical {
                background: transparent;
                width: 12px;
                margin: 0;
            }
            /* Handle scrollbaru */
            QScrollBar::handle:vertical {
                background: #000000;
                min-height: 20px;
                border-radius: 6px;
            }
            /* Skryj šipky */
            QScrollBar::sub-line:vertical,
            QScrollBar::add-line:vertical {
                height: 0;
            }
            /* Prázdné partie nad i pod handle */
            QScrollBar::sub-page:vertical,
            QScrollBar::add-page:vertical {
                background: none;
            }
        """)
        # Transparentní viewport
        scroll.viewport().setStyleSheet("background: transparent;")
        scroll.viewport().setAttribute(QtCore.Qt.WA_TranslucentBackground)

        # Kontejner s průhledným pozadím
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        container.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.vlay = QVBoxLayout(container)
        self.vlay.setSpacing(20)
        self.vlay.setAlignment(QtCore.Qt.AlignTop)
        
        scroll.setWidget(container)
        lay.addWidget(scroll)


    def update_view(self):
        ty = self.main.current_op_type or "All types"
        yr = self.main.selected_year   or "All years"
        self.header.setText(f"Type: {ty} ┃ Year: {yr}")

        # vyčistit
        for i in reversed(range(self.vlay.count())):
            w = self.vlay.itemAt(i).widget()
            if w: w.setParent(None)

        df = self.df.copy()
        if yr != "2021-2025":
            try:
                df = df[df["OperationDate"] == int(yr)]
            except ValueError:
                pass
        if ty:
            df = df[df["OperationType"] == ty]
        s, e = self.date_from.date().year(), self.date_to.date().year()
        df = df[(df["OperationDate"] >= s) & (df["OperationDate"] <= e)]

        if df.empty:
            lbl = QLabel("No data for this type/year.")
            lbl.setAlignment(QtCore.Qt.AlignCenter)
            self.vlay.addWidget(lbl)
            return

        # 1) Indication for Surgery
        sec1 = CollapsibleSection("Indication for Surgery")
        sec1.add_widget(make_bar_chart(
            df["Indication"].value_counts(),
            "Indication for Surgery", "Indication", "Count"
        ))
        self.vlay.addWidget(sec1)

        # 2) Type-specific sections
        if ty == "GHR":
            sec2 = CollapsibleSection("Side of the Hernia")
            sec2.add_widget(make_bar_chart(
                df["Side"].fillna("Unknown").value_counts(),
                "Side of the Hernia", "Side", "Count"
            ))
            self.vlay.addWidget(sec2)

            sec3 = CollapsibleSection("Previous Repairs (Right)")
            sec3.add_widget(make_bar_chart(
                df["PrevRepairsRight"].fillna(0).astype(int).value_counts().sort_index(),
                "Previous Repairs (Right)", "Number of Repairs", "Count"
            ))
            self.vlay.addWidget(sec3)

            sec4 = CollapsibleSection("Previous Repairs (Left)")
            sec4.add_widget(make_bar_chart(
                df["PrevRepairsLeft"].fillna(0).astype(int).value_counts().sort_index(),
                "Previous Repairs (Left)", "Number of Repairs", "Count"
            ))
            self.vlay.addWidget(sec4)

            sec5 = CollapsibleSection("Groin Hernia Type (Right)")
            sec5.add_widget(make_bar_chart(
                df["HerniaTypeRight"].fillna("Unknown").value_counts(),
                "Groin Hernia Type (Right)", "Hernia Type", "Count"
            ))
            self.vlay.addWidget(sec5)

            sec6 = CollapsibleSection("Groin Hernia Type (Left)")
            sec6.add_widget(make_bar_chart(
                df["HerniaTypeLeft"].fillna("Unknown").value_counts(),
                "Groin Hernia Type (Left)", "Hernia Type", "Count"
            ))
            self.vlay.addWidget(sec6)

        elif ty == "PHR":
            sec2 = CollapsibleSection("Type of Stoma")
            sec2.add_widget(make_bar_chart(
                df["StomaType"].fillna("Unknown").value_counts(),
                "Type of Stoma", "Stoma Type", "Count"
            ))
            self.vlay.addWidget(sec2)

            sec3 = CollapsibleSection("Number of Previous Repairs")
            total = (df["PrevRepairsRight"].fillna(0) + df["PrevRepairsLeft"].fillna(0)).astype(int)
            sec3.add_widget(make_bar_chart(
                total.value_counts().sort_index(),
                "Number of Previous Repairs", "Number of Repairs", "Count"
            ))
            self.vlay.addWidget(sec3)

        elif ty == "PVHR":
            sec2 = CollapsibleSection("PVHR Type Specification")
            sec2.add_widget(make_bar_chart(
                df["PVHR_Type"].fillna("Unknown").value_counts(),
                "PVHR Type Specification", "PVHR Type", "Count"
            ))
            self.vlay.addWidget(sec2)

        elif ty == "IVHR":
            sec2 = CollapsibleSection("Number of Previous Hernia Repairs")
            total = (df["PrevRepairsRight"].fillna(0) + df["PrevRepairsLeft"].fillna(0)).astype(int)
            sec2.add_widget(make_bar_chart(
                total.value_counts().sort_index(),
                "Number of Previous Hernia Repairs", "Number of Repairs", "Count"
            ))
            self.vlay.addWidget(sec2)

        # 3) Statistics table
        stats = {
            "Total ops":         len(df),
            "Avg duration (h)":  f"{df['OperationDuration_h'].mean():.2f}",
            "Min duration (h)":  f"{df['OperationDuration_h'].min():.2f}",
            "Max duration (h)":  f"{df['OperationDuration_h'].max():.2f}"
        }
        tbl_sec = CollapsibleSection("Summary Statistics")
        tbl_sec.add_widget(make_stats_table(stats))
        self.vlay.addWidget(tbl_sec)
