# pages/operative_page.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea,
    QSpinBox, QHBoxLayout
)
from PyQt5 import QtCore
import pandas as pd

from ui_helpers import CollapsibleSection
from chart_utils import make_bar_chart, make_histogram
from table_utils import make_stats_table


class OperativePage(QWidget):
    """
    Stránka zobrazující statistiky operačních dat podle druhu hernioplastiky a roku.
    Používá QSpinBox pro výběr roku (pouze rok, bez dne/měsíce).
    """
    def __init__(self, main_win, df):
        super().__init__()
        self.main = main_win
        self.df   = df.copy()
        # rozmezí let
        years = self.df['Date of Operation'].dt.year
        self.min_year = int(years.min())
        self.max_year = int(years.max())
        self._build_ui()

    def _build_ui(self):
        lay = QVBoxLayout(self)

        # Nadpis
        title = QLabel("Operative Data – Visualization and Table")
        title.setObjectName("titleLabel")
        title.setAlignment(QtCore.Qt.AlignCenter)
        lay.addWidget(title)

        # prostor pro scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        self.vlay = QVBoxLayout(container)
        self.vlay.setSpacing(20)
        self.vlay.setAlignment(QtCore.Qt.AlignTop)
        scroll.setWidget(container)
        lay.addWidget(scroll)
        
        # počáteční render
        self.update_view()

    def update_view(self):
        # filtr rok
        start_y = self.year_from.value()
        end_y   = self.year_to.value()
        ty      = self.main.current_op_type

        # vyčistit layout
        for i in reversed(range(self.vlay.count())):
            widget = self.vlay.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        # filtrovaná data
        df = self.df[
            self.df['Date of Operation'].dt.year.between(start_y, end_y)
        ]
        if ty:
            df = df[df['Operation_Type'] == ty]

        if df.empty:
            lbl = QLabel("No data for this selection.")
            lbl.setAlignment(QtCore.Qt.AlignCenter)
            self.vlay.addWidget(lbl)
            return

        # 1) Indication for Surgery
        sec1 = CollapsibleSection("Indication for Surgery")
        counts1 = df['Indication'].fillna('Unknown').value_counts()
        sec1.add_widget(make_bar_chart(
            counts1, "Indication for Surgery", "Indication", "Count"
        ))
        self.vlay.addWidget(sec1)

        # specifické sekce podle typu
        if ty == 'GHR':
            # Side of Hernia
            sec2 = CollapsibleSection("Side of the Hernia")
            side_counts = pd.Series({
                'Right': df['GHR_Side_Right'].sum(),
                'Left':  df['GHR_Side_Left'].sum()
            })
            sec2.add_widget(make_bar_chart(
                side_counts, "Side of the Hernia", "Side", "Count"
            ))
            self.vlay.addWidget(sec2)

            # Previous Repairs Right
            sec3 = CollapsibleSection("Previous Repairs (Right)")
            prev_r = df['GHR_Prev_Repairs_Right'].fillna(0).astype(int).value_counts().sort_index()
            sec3.add_widget(make_bar_chart(
                prev_r, "Previous Repairs (Right)", "Repairs", "Count"
            ))
            self.vlay.addWidget(sec3)

            # Previous Repairs Left
            sec4 = CollapsibleSection("Previous Repairs (Left)")
            prev_l = df['GHR_Prev_Repairs_Left'].fillna(0).astype(int).value_counts().sort_index()
            sec4.add_widget(make_bar_chart(
                prev_l, "Previous Repairs (Left)", "Repairs", "Count"
            ))
            self.vlay.addWidget(sec4)

            # Hernia Type Right
            sec5 = CollapsibleSection("Groin Hernia Type (Right)")
            cols_r = [
                'GHR_Type_Right_Lateral', 'GHR_Type_Right_Medial',
                'GHR_Type_Right_Femoral', 'GHR_Type_Right_Obturator'
            ]
            type_counts_r = {col.split('GHR_Type_Right_')[1].replace('_',' '): df[col].sum() for col in cols_r}
            sec5.add_widget(make_bar_chart(
                pd.Series(type_counts_r),
                "Groin Hernia Type (Right)", "Type", "Count"
            ))
            self.vlay.addWidget(sec5)

            # Hernia Type Left
            sec6 = CollapsibleSection("Groin Hernia Type (Left)")
            cols_l = [
                'GHR_Type_Left_Lateral', 'GHR_Type_Left_Medial',
                'GHR_Type_Left_Femoral', 'GHR_Type_Left_Obturator'
            ]
            type_counts_l = {col.split('GHR_Type_Left_')[1].replace('_',' '): df[col].sum() for col in cols_l}
            sec6.add_widget(make_bar_chart(
                pd.Series(type_counts_l),
                "Groin Hernia Type (Left)", "Type", "Count"
            ))
            self.vlay.addWidget(sec6)

        elif ty == 'PHR':
            # Type of Stoma
            sec2 = CollapsibleSection("Type of Stoma")
            stom_counts = df['PHR_Stoma_Type'].fillna('Unknown').value_counts()
            sec2.add_widget(make_bar_chart(
                stom_counts, "Type of Stoma", "Stoma Type", "Count"
            ))
            self.vlay.addWidget(sec2)
            # Previous Repairs
            sec3 = CollapsibleSection("Previous Repairs")
            prev = df['PHR_Prev_Repairs'].fillna(0).astype(int).value_counts().sort_index()
            sec3.add_widget(make_bar_chart(
                prev, "Previous Repairs", "Repairs", "Count"
            ))
            self.vlay.addWidget(sec3)

        elif ty == 'PVHR':
            sec2 = CollapsibleSection("PVHR Subtype")
            sub_counts = df['PVHR_Subtype'].fillna('Unknown').value_counts()
            sec2.add_widget(make_bar_chart(
                sub_counts, "PVHR Subtype", "Subtype", "Count"
            ))
            self.vlay.addWidget(sec2)

        elif ty == 'IVHR':
            sec2 = CollapsibleSection("Previous Hernia Repairs")
            prev_all = df['IVHR_Prev_Repairs'].fillna(0).astype(int).value_counts().sort_index()
            sec2.add_widget(make_bar_chart(
                prev_all, "Previous Hernia Repairs", "Repairs", "Count"
            ))
            self.vlay.addWidget(sec2)

        # summary table
        stats = {"Total operations": len(df)}
        tbl_sec = CollapsibleSection("Summary Statistics")
        tbl_sec.add_widget(make_stats_table(stats))
        self.vlay.addWidget(tbl_sec)
