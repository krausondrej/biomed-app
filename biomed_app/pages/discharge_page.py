# pages/discharge_page.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea,
    QHBoxLayout, QComboBox
)
from PyQt5 import QtCore
from ui_helpers import CollapsibleSection
from chart_utils import make_bar_chart
from table_utils import make_stats_table
from ui_helpers import add_download_button


class DischargePage(QWidget):
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

        title = QLabel("INTRAHOSPITAL COMPLICATIONS")
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
            lbl = QLabel("Chyba: Data nejsou dostupná.")
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
            warn_lbl = QLabel("Upozornění: Sloupec 'Year' není dostupný.")
            warn_lbl.setAlignment(QtCore.Qt.AlignCenter)
            self.vlay.addWidget(warn_lbl)

        if self.selected_gender.lower() in ["male", "female"]:
            if 'Gender' in df.columns:
                df = df[df['Gender'] == self.selected_gender.lower()]
            else:
                lbl = QLabel("Upozornění: Sloupec 'Gender' chybí.")
                lbl.setAlignment(QtCore.Qt.AlignCenter)
                self.vlay.addWidget(lbl)

        if self.selected_age_group != "All":
            if "Age" in df.columns:
                df = df[df["Age"] == self.selected_age_group]
            else:
                warn_lbl = QLabel("Upozornění: Sloupec 'Age' není dostupný.")
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
            empty_lbl = QLabel("No discharge data for selected filters.")
            empty_lbl.setAlignment(QtCore.Qt.AlignCenter)
            self.vlay.addWidget(empty_lbl)
            return

        if 'Intra_Complications' not in df.columns:
            err_lbl = QLabel(
                "Chyba: Sloupec 'Intra_Complications' není dostupný.")
            err_lbl.setAlignment(QtCore.Qt.AlignCenter)
            self.vlay.addWidget(err_lbl)
            return
        occ_counts = df['Intra_Complications'].value_counts()
        sec1 = CollapsibleSection('Occurrence of Intrahospital Complications')
        if occ_counts.empty:
            msg = QLabel('No data for selected filters.')
            msg.setAlignment(QtCore.Qt.AlignCenter)
            sec1.add_widget(msg)
        else:
            chart1 = make_bar_chart(
                occ_counts,
                'Intrahospital Complications', '', 'Count'
            )
            sec1.add_widget(add_download_button(chart1, "Download Bar Chart"))
        self.vlay.addWidget(sec1)

        cols = [
            'Comp_Bleeding', 'Comp_SSI', 'Comp_Mesh_Infection',
            'Comp_Hematoma', 'Comp_Prolonged_Ileus',
            'Comp_Urinary_Retention', 'Comp_General'
        ]
        missing_cols = [c for c in cols if c not in df.columns]
        if missing_cols:
            err_lbl = QLabel(
                f"Chyba: Chybí sloupce: {', '.join(missing_cols)}.")
            err_lbl.setAlignment(QtCore.Qt.AlignCenter)
            self.vlay.addWidget(err_lbl)
            return

        counts = df[cols].sum().fillna(0).astype(int)
        counts = counts[counts > 0]
        label_map = {
            'Comp_Bleeding': 'Bleeding',
            'Comp_SSI': 'SSI',
            'Comp_Mesh_Infection': 'Mesh Infection',
            'Comp_Hematoma': 'Hematoma',
            'Comp_Prolonged_Ileus': 'Prolonged Ileus',
            'Comp_Urinary_Retention': 'Urinary Retention',
            'Comp_General': 'General'
        }
        counts = counts.rename(index=label_map)

        sec2 = CollapsibleSection('Type of Intrahospital Complications')
        if counts.empty:
            msg2 = QLabel('No complication types for selected filters.')
            msg2.setAlignment(QtCore.Qt.AlignCenter)
            sec2.add_widget(msg2)
        else:
            chart2 = make_bar_chart(
                counts,
                title='Complication Types', xlabel='', ylabel='Count'
            )
            fg, ax = chart2.figure, chart2.figure.axes[0]
            for lbl in ax.get_xticklabels():
                lbl.set_rotation(45)
                lbl.set_ha('right')
            chart2.figure.tight_layout()
            sec2.add_widget(add_download_button(chart2, "Download Bar Chart"))
        self.vlay.addWidget(sec2)

        n_total = len(df)
        has = df['Intra_Complications'].dropna().astype(bool)
        n_true = has.sum()

        stats = {
            'Total patients': n_total,
            'With complications': int(n_true),
            'Without complications': n_total - int(n_true),
            '% with complications': f"{n_true/n_total*100:.1f}%" if n_total > 0 else "N/A"
        }

        if 'Gender' in df.columns:
            gender_counts = df['Gender'].value_counts()
            stats['Male %'] = f"{gender_counts.get('male', 0)/n_total*100:.1f}%" if n_total > 0 else "N/A"
            stats['Female %'] = f"{gender_counts.get('female', 0)/n_total*100:.1f}%" if n_total > 0 else "N/A"

        sec3 = CollapsibleSection('Summary Statistics')
        wrapper = QWidget()
        wrapper_lay = QVBoxLayout(wrapper)
        wrapper_lay.setContentsMargins(0, 10, 0, 0)
        wrapper_lay.addWidget(make_stats_table(stats))
        sec3.add_widget(wrapper)
        self.vlay.addWidget(sec3)
