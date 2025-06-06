# pages/followup_page.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea,
    QHBoxLayout, QComboBox
)
from PyQt5 import QtCore
from ui_helpers import CollapsibleSection
from chart_utils import make_bar_chart
from table_utils import make_stats_table
from ui_helpers import add_download_button


class FollowupPage(QWidget):
    def __init__(self, main_win, df):
        super().__init__()
        self.main = main_win
        self.df = df
        self.selected_age_group = "All"
        self.selected_gender = "All"
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(30, 20, 30, 20)
        root.setSpacing(15)

        title = QLabel("FOLLOW-UP DATA")
        title.setObjectName("titleLabel")
        title.setAlignment(QtCore.Qt.AlignCenter)
        root.addWidget(title)

        self.header = QLabel("")
        self.header.setObjectName("subtitleLabel")
        self.header.setAlignment(QtCore.Qt.AlignCenter)
        root.addWidget(self.header)

        filters_layout = QHBoxLayout()
        filters_layout.setSpacing(30)
        filters_layout.setAlignment(QtCore.Qt.AlignCenter)

        gender_label = QLabel("Sex:")
        gender_label.setObjectName("filterLabel")
        filters_layout.addWidget(gender_label)

        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["All", "Male", "Female"])
        self.gender_combo.currentTextChanged.connect(self._filter_gender)
        filters_layout.addWidget(self.gender_combo)

        age_label = QLabel("Age:")
        age_label.setObjectName("filterLabel")
        filters_layout.addWidget(age_label)

        self.age_combo = QComboBox()
        self.age_combo.addItems([
            "All", "<  25", "25 - 34", "35 - 44", "45 - 54",
            "55 - 64", "65 - 74", ">  75"
        ])
        self.age_combo.currentTextChanged.connect(self._filter_age)
        filters_layout.addWidget(self.age_combo)

        root.addLayout(filters_layout)

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

    def _filter_age(self, age_group):
        self.selected_age_group = age_group
        self.update_view()

    def update_view(self):
        if self.df is None or self.df.empty:
            lbl = QLabel("Error: data unavailable.")
            lbl.setAlignment(QtCore.Qt.AlignCenter)
            self.vlay.addWidget(lbl)
            return
        df = self.df.copy()

        ty = self.main.current_op_type or "All types"
        yr = self.main.selected_year or "All years"

        if 'Year' in df.columns:
            if isinstance(yr, str) and '-' in yr:
                try:
                    start, end = map(int, yr.split('-'))
                    df = df[df['Year'].between(start, end)]
                except:
                    pass
            else:
                try:
                    year = int(yr)
                    df = df[df['Year'] == year]
                except ValueError:
                    pass
        else:
            warn_lbl = QLabel("Note: The ‘Year’ column is not available")
            warn_lbl.setAlignment(QtCore.Qt.AlignCenter)
            self.vlay.addWidget(warn_lbl)

        if self.selected_gender.lower() in ["male", "female"]:
            if 'Gender' in df.columns:
                df = df[df['Gender'] == self.selected_gender.lower()]
            else:
                warn_lbl = QLabel("Note: The ‘Gender’ column is not available")
                warn_lbl.setAlignment(QtCore.Qt.AlignCenter)
                self.vlay.addWidget(warn_lbl)

        if self.selected_age_group != "All":
            if "Age" in df.columns:
                df = df[df["Age"] == self.selected_age_group]
            else:
                warn_lbl = QLabel("Note: The ‘Age’ column is not available")
                warn_lbl.setAlignment(QtCore.Qt.AlignCenter)
                self.vlay.addWidget(warn_lbl)

        self.header.setText(
            f"Operation: {ty}   |   Year: {yr}   |   N = {len(df)}"
        )

        for i in reversed(range(self.vlay.count())):
            w = self.vlay.itemAt(i).widget()
            if w:
                w.setParent(None)

        if df.empty:
            empty_lbl = QLabel("No data for the selected filter")
            empty_lbl.setAlignment(QtCore.Qt.AlignCenter)
            self.vlay.addWidget(empty_lbl)
            return

        if 'Followup_Complications' not in df.columns:
            err_lbl = QLabel("Error: column 'Followup_Complications' is missing.")
            err_lbl.setAlignment(QtCore.Qt.AlignCenter)
            self.vlay.addWidget(err_lbl)
            return

        occ_counts = df['Followup_Complications'].value_counts()
        sec1 = CollapsibleSection("Occurrence of Complications")
        chart1 = make_bar_chart(
            occ_counts,
            "Complications at Follow-up",
            "",
            "Count"
        )
        sec1.add_widget(add_download_button(chart1, "Download Bar Chart"))
        self.vlay.addWidget(sec1)

        cols = [
            'FU_Seroma', 'FU_Hematoma', 'FU_Pain',
            'FU_SSI', 'FU_Mesh_Infection', 'FU_Other'
        ]
        missing_cols = [col for col in cols if col not in df.columns]
        if missing_cols:
            warn_lbl = QLabel(f"Chyba: Chybí sloupce: {', '.join(missing_cols)}.")
            warn_lbl.setAlignment(QtCore.Qt.AlignCenter)
            self.vlay.addWidget(warn_lbl)
            return

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
            fig = chart2.figure
            ax = fig.axes[0]
            for label in ax.get_xticklabels():
                label.set_rotation(45)
                label.set_ha('right')

            fig.tight_layout()
            sec2.add_widget(add_download_button(chart2, "Download Bar Chart"))

        self.vlay.addWidget(sec2)

        n_total = len(df)
        n_comp = 0

        if "Followup_Complications" in df.columns:
            comp_col = df["Followup_Complications"].dropna()
            n_comp = int(comp_col.astype(bool).sum())

        stats = {
            'Total patients': n_total,
            'With complications': n_comp,
            'Without complications': n_total - n_comp if n_total >= n_comp else "N/A",
            '% with complications': f"{n_comp/n_total*100:.1f}%" if n_total > 0 else "N/A"
        }

        sec3 = CollapsibleSection("Summary Statistics")
        wrapper = QWidget()
        wrapper_lay = QVBoxLayout(wrapper)
        wrapper_lay.setContentsMargins(0, 10, 0, 0)
        wrapper_lay.addWidget(make_stats_table(stats))
        sec3.add_widget(wrapper)
        self.vlay.addWidget(sec3)

