# pages/discharge_page.py
import pandas as pd
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QHBoxLayout, QComboBox
from PyQt5 import QtCore
from ui_helpers import CollapsibleSection
from chart_utils import make_bar_chart
from table_utils import make_stats_table

class DischargePage(QWidget):
    def __init__(self, main_win, df):
        super().__init__()
        self.main = main_win
        self.df   = df
        self.selected_gender = "All"
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
        
        # Gender filter
        gender_layout = QHBoxLayout()
        gender_layout.setSpacing(20)
        gender_layout.setAlignment(QtCore.Qt.AlignHCenter)
        gender_label = QLabel("Sex filter:")
        gender_label.setObjectName("filterLabel")
        gender_layout.addWidget(gender_label)
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["All", "Male", "Female"])
        self.gender_combo.currentTextChanged.connect(self._filter_gender)
        gender_layout.setContentsMargins(0, 10, 0, 0)
        gender_layout.addWidget(self.gender_combo)
        lay.addLayout(gender_layout)

        # Scrollable container
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea { background: transparent; border: none; }
            QScrollBar:vertical { background: transparent; width: 12px; margin: 0; }
            QScrollBar::handle:vertical { background: #000000; min-height: 20px; border-radius: 6px; }
            QScrollBar::sub-line:vertical, QScrollBar::add-line:vertical { height: 0; }
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

    def _filter_gender(self, gender_text):
        self.selected_gender = gender_text
        self.update_view()

    def update_view(self):
        # read current filters
        ty    = getattr(self.main, 'current_op_type', 'All') or 'All'
        yr    = getattr(self.main, 'selected_year', 'All') or 'All'

        # clear previous content
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
        
        self.header.setText(f"Operation: {ty}   |   Year: {yr_sel}   |   Number of Result: {len(df)}")

        if self.selected_gender.lower() in ["male", "female"]:
                    df = df[df["Gender"] == self.selected_gender.lower()]
                    
        # empty dataset: no records
        if df.empty:
            lbl = QLabel("No discharge data for selected filters.")
            lbl.setAlignment(QtCore.Qt.AlignCenter)
            self.vlay.addWidget(lbl)
            return

        # 1) Occurrence of Intrahospital Complications
        occ_counts = df['Intra_Complications'].value_counts()
        sec1 = CollapsibleSection('Occurrence of Intrahospital Complications')
        if occ_counts.empty:
            sec1.add_widget(QLabel('No data for selected filters.'))
        else:
            sec1.add_widget(make_bar_chart(
                occ_counts,
                'Intrahospital complications',
                '',
                'Number'
            ))
        self.vlay.addWidget(sec1)

        # 2) Type of Intrahospital Complications
        cols = [
            'Comp_Bleeding', 'Comp_SSI', 'Comp_Mesh_Infection',
            'Comp_Hematoma', 'Comp_Prolonged_Ileus',
            'Comp_Urinary_Retention', 'Comp_General'
        ]
        counts = df[cols].sum().fillna(0).astype(int)

        type_counts = counts[counts > 0]

        label_map = {
            'Comp_Bleeding':           "Bleeding complications",
            'Comp_SSI':                "Surgical site infection (SSI)",
            'Comp_Mesh_Infection':     "Mesh infection",
            'Comp_Hematoma':           "Hematoma",
            'Comp_Prolonged_Ileus':    "Prolonged ileus or obstruction",
            'Comp_Urinary_Retention':  "Urinary retention",
            'Comp_General':            "General complications"
        }

        type_counts = type_counts.rename(index=label_map)

        sec2 = CollapsibleSection('Type of Intrahospital Complications')
        if type_counts.sum() == 0:
            sec2.add_widget(QLabel('No complication types for selected filters.'))
        else:
            chart = make_bar_chart(
                type_counts,
                title='Type of Intraope. surgical complications',
                xlabel='',
                ylabel='Number'
            )
            fig = chart.figure
            ax  = fig.axes[0]
            for lbl in ax.get_xticklabels():
                lbl.set_rotation(45)
                lbl.set_ha('right')
            fig.tight_layout()

            sec2.add_widget(chart)

        self.vlay.addWidget(sec2)

        # 3) Summary Statistics
        has_comp = df['Intra_Complications'].dropna().astype(bool)
        n_true  = has_comp.sum()
        n_total = len(df)
        stats = {
            'Total patients':              n_total,
            'Complications (Yes)':         n_true,
            'Complications (No)':          n_total - n_true,
            'Distinct complication types': len(type_counts),
        }

        stats["% with complications"] = f"{n_true/n_total*100:.1f}%"

        comp_counts_per_patient = df[cols].sum(axis=1)
        stats["Avg complications/patient"] = f"{comp_counts_per_patient.mean():.2f}"

        if type_counts.any():
            stats["Most common complication"] = type_counts.idxmax()

        stats["Total complication events"] = int(type_counts.sum())

        gender_counts = df["Gender"].value_counts()
        stats["Male %"]   = f"{gender_counts.get('male',0)/n_total*100:.1f}%"
        stats["Female %"] = f"{gender_counts.get('female',0)/n_total*100:.1f}%"

        yearly = df["Year"].value_counts().sort_index()
        if not yearly.empty:
            stats["Years covered"]    = f"{yearly.index.min()}–{yearly.index.max()}"
            stats["Avg ops per year"] = f"{yearly.mean():.1f}"

        sec3 = CollapsibleSection('Summary Statistics')
        sec3.add_widget(make_stats_table(stats))
        self.vlay.addWidget(sec3)
