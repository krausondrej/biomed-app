import pandas as pd
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea,
    QHBoxLayout, QComboBox
)
from PyQt5 import QtCore
from ui_helpers import CollapsibleSection
from chart_utils import make_bar_chart
from table_utils import make_stats_table

class FollowupPage(QWidget):
    def __init__(self, main_win, df):
        super().__init__()
        self.main = main_win
        self.df   = df
        self.selected_gender = "All"
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(30, 20, 30, 20)
        root.setSpacing(15)

        # Title
        title = QLabel("FOLLOW-UP COMPLICATIONS")
        title.setObjectName("titleLabel")
        title.setAlignment(QtCore.Qt.AlignCenter)
        root.addWidget(title)

        # Subtitle / header
        self.header = QLabel("")
        self.header.setObjectName("subtitleLabel")
        self.header.setAlignment(QtCore.Qt.AlignCenter)
        root.addWidget(self.header)

        # Gender filter
        gender_layout = QHBoxLayout()
        gender_layout.setSpacing(10)
        gender_layout.setAlignment(QtCore.Qt.AlignCenter)

        gender_label = QLabel("Sex:")
        gender_label.setObjectName("filterLabel")
        gender_layout.addWidget(gender_label)

        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["All", "Male", "Female"])
        self.gender_combo.currentTextChanged.connect(self._filter_gender)
        gender_layout.addWidget(self.gender_combo)

        root.addLayout(gender_layout)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setObjectName("dataScroll")
        scroll.setStyleSheet("""
            QScrollArea#dataScroll { background: #F9F9F9; border: none; }
        """)

        container = QWidget()
        container.setObjectName("scrollContainer")
        vlay = QVBoxLayout(container)
        vlay.setContentsMargins(0, 10, 0, 10)
        vlay.setSpacing(20)

        scroll.setWidget(container)
        root.addWidget(scroll)
        self.vlay = vlay

        # Apply stylesheet
        self.setStyleSheet("""
            /* Title */
            #titleLabel {
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 5px;
            }
            /* Subtitle */
            #subtitleLabel {
                font-size: 14px;
                color: #555555;
                margin-bottom: 15px;
            }
            /* Filter label */
            #filterLabel {
                font-size: 14px;
                color: #333333;
            }
            /* Scroll container background */
            #scrollContainer {
                background: #FFFFFF;
                border-radius: 8px;
                padding: 15px;
            }
        """)

    def _filter_gender(self, gender_text):
        self.selected_gender = gender_text
        self.update_view()

    def update_view(self):
        ty = self.main.current_op_type or "All types"
        yr = self.main.selected_year   or "All years"
        df = self.df.copy()

        # filter by year
        if isinstance(yr, str) and '-' in yr:
            start, end = map(int, yr.split('-'))
            df = df[df['Year'].between(start, end)]
        else:
            try:
                year = int(yr)
                df = df[df['Year'] == year]
            except ValueError:
                pass

        # update header
        self.header.setText(f"Operation: {ty}   |   Year: {yr}   |   N = {len(df)}")

        # clear old widgets
        for i in reversed(range(self.vlay.count())):
            w = self.vlay.itemAt(i).widget()
            if w:
                w.setParent(None)

        # gender filter
        if self.selected_gender.lower() in ["male", "female"]:
            df = df[df['Gender'] == self.selected_gender.lower()]

        # 1) Occurrence of complications
        occ_counts = df['Followup_Complications'].value_counts()
        sec1 = CollapsibleSection("Occurrence of Complications")
        chart1 = make_bar_chart(
            occ_counts,
            "Complications at Follow-up",
            "",
            "Count"
        )
        sec1.add_widget(chart1)
        self.vlay.addWidget(sec1)

        # 2) Type of complications
        cols = [
            'FU_Seroma', 'FU_Hematoma', 'FU_Pain',
            'FU_SSI', 'FU_Mesh_Infection', 'FU_Other'
        ]
        counts = df[cols].sum().fillna(0).astype(int)
        label_map = {
            'FU_Seroma': 'Seroma',
            'FU_Hematoma': 'Hematoma',
            'FU_Pain': 'Pain',
            'FU_SSI': 'SSI',
            'FU_Mesh_Infection': 'Mesh Infection',
            'FU_Other': 'Other'
        }
        counts = counts.rename(index=label_map)
        counts = counts[counts > 0]

        sec2 = CollapsibleSection("Type of Complications")
        if counts.empty:
            empty_lbl = QLabel("No complications for selected filters.")
            empty_lbl.setAlignment(QtCore.Qt.AlignCenter)
            sec2.add_widget(empty_lbl)
        else:
            chart2 = make_bar_chart(
                counts,
                title="Complication Types",
                xlabel="Type",
                ylabel="Count"
            )
            sec2.add_widget(chart2)
        self.vlay.addWidget(sec2)

        # 3) Summary Statistics
        n_total = len(df)
        n_comp = int(df['Followup_Complications'].dropna().astype(bool).sum())
        stats = {
            'Total patients': n_total,
            'With complications': n_comp,
            'Without complications': n_total - n_comp,
            '% with complications': f"{n_comp/n_total*100:.1f}%"
        }
        sec3 = CollapsibleSection("Summary Statistics")
        wrapper = QWidget()
        wrapper_lay = QVBoxLayout(wrapper)
        wrapper_lay.setContentsMargins(0, 10, 0, 0)   # left, top=20px, right, bottom
        wrapper_lay.addWidget(make_stats_table(stats))
        sec3.add_widget(wrapper)
        self.vlay.addWidget(sec3)
