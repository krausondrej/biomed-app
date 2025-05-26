# pages/preop_page.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QComboBox, QHBoxLayout
from PyQt5 import QtCore
from ui_helpers import CollapsibleSection
from chart_utils import make_bar_chart, make_histogram
from table_utils import make_stats_table

class PreopPage(QWidget):
    def __init__(self, main_win, df):
        super().__init__()
        self.main = main_win
        # Původní DataFrame pro filtrování
        self.df_master = df
        # Výchozí výběr pohlaví
        self.selected_gender = "Všechno"
        self._build_ui()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0,0,0,0)
        lay.setSpacing(2)

        lbl = QLabel("Preoperative Data – Visualization")
        lbl.setObjectName("titleLabel"); lbl.setAlignment(QtCore.Qt.AlignCenter)
        lay.addWidget(lbl)

        # Zobrazovaný header s typem a rokem
        self.header = QLabel(); self.header.setAlignment(QtCore.Qt.AlignCenter)
        lay.addWidget(self.header)

        # Popisek filtrace pohlaví
        gender_layout = QHBoxLayout()
        gender_layout.setSpacing(20)
        gender_layout.setAlignment(QtCore.Qt.AlignHCenter)

        gender_label = QLabel("Sex filter:")
        gender_label.setObjectName("filterLabel")
        gender_label.setAlignment(QtCore.Qt.AlignCenter)
        gender_layout.addWidget(gender_label)
        
        # Vyber pohlavi
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["All", "Male", "Female"])
        self.gender_combo.currentTextChanged.connect(self._filter_gender)
        gender_layout.addWidget(self.gender_combo)

        lay.addLayout(gender_layout)
        
        # Scrollovatelná oblast pro obsah
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea { background: transparent; border: none; }
            QScrollBar:vertical { background: transparent; width: 12px; margin: 0; padding: 0; }
            QScrollBar::handle:vertical { background: #000; min-height: 20px; border-radius: 6px; }
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
        """Uloží vybrané pohlaví a překreslí view."""
        self.selected_gender = gender_text
        self.update_view()

    def update_view(self):
        ty = self.main.current_op_type or "All types"
        yr = self.main.selected_year   or "All years"
        self.header.setText(f"Type: {ty} ┃ Year: {yr}")

        # Vyčistit staré widgety
        for i in reversed(range(self.vlay.count())):
            w = self.vlay.itemAt(i).widget()
            if w:
                w.setParent(None)

        # Základní DataFrame podle roku
        df = self.df_master.copy()
        if yr != "2021-2025":
            try:
                df = df[df["Year"] == int(yr)]
            except ValueError:
                pass

        # Filtrace podle pohlaví
        if self.selected_gender == "Male":
            df = df[df["Gender"] == "Male"]
        elif self.selected_gender == "Female":
            df = df[df["Gender"] == "Female"]

        if df.empty:
            lbl = QLabel("No data for selected filters.")
            lbl.setAlignment(QtCore.Qt.AlignCenter)
            self.vlay.addWidget(lbl)
            return

        # 1) Počet mužů a žen
        sec1 = CollapsibleSection("Number of Men and Women")
        chart1 = make_bar_chart(
            df["Gender"].value_counts(),
            "Number of Men and Women", "Gender", "Count"
        )
        sec1.add_widget(chart1)
        self.vlay.addWidget(sec1)

        # 2) Age Distribution
        sec2 = CollapsibleSection("Age Distribution")
        chart2 = make_histogram(
            df["Age"], bins=10,
            title="Age Distribution", xlabel="Age", ylabel="Count"
        )
        sec2.add_widget(chart2)
        self.vlay.addWidget(sec2)

        # 3) BMI Distribution
        sec3 = CollapsibleSection("BMI Distribution")
        chart3 = make_histogram(
            df["BMI"], bins=10,
            title="BMI Distribution", xlabel="BMI", ylabel="Count"
        )
        sec3.add_widget(chart3)
        self.vlay.addWidget(sec3)

        # 4) Comorbidities Before Surgery
        sec4 = CollapsibleSection("Prevalence of Comorbidities")
        com_sums = df[["Diabetes", "Hypertension", "Heart_Disease"]].sum()
        chart4 = make_bar_chart(
            com_sums,
            "Prevalence of Comorbidities", "Comorbidity", "Number of Patients"
        )
        sec4.add_widget(chart4)
        self.vlay.addWidget(sec4)

        # 5) Pre-operative Pain Score
        sec5 = CollapsibleSection("Pre-operative Pain Score")
        chart5 = make_histogram(
            df["Preop_Pain_Score"], bins=10,
            title="Pre-operative Pain Score", xlabel="Pain Score", ylabel="Count"
        )
        sec5.add_widget(chart5)
        self.vlay.addWidget(sec5)

        # 6) Pre-operative Restrictions Score
        sec6 = CollapsibleSection("Pre-operative Restrictions Score")
        chart6 = make_histogram(
            df["Preop_Restrictions_Score"], bins=10,
            title="Pre-operative Restrictions Score", xlabel="Restrictions Score", ylabel="Count"
        )
        sec6.add_widget(chart6)
        self.vlay.addWidget(sec6)

        # 7) Aesthetic Discomfort Score
        sec7 = CollapsibleSection("Aesthetic Discomfort Score")
        chart7 = make_histogram(
            df["Aesthetic_Discomfort_Score"], bins=10,
            title="Aesthetic Discomfort Score", xlabel="Discomfort Score", ylabel="Count"
        )
        sec7.add_widget(chart7)
        self.vlay.addWidget(sec7)

        # 8) Přehledová tabulka statistik
        stats = {
            "Total patients": len(df),
            "Males": df["Gender"].value_counts().get("Male", 0),
            "Females": df["Gender"].value_counts().get("Female", 0),
            "Mean age": f"{df['Age'].mean():.1f}",
            "Median age": f"{df['Age'].median():.1f}",
            "Mean BMI": f"{df['BMI'].mean():.1f}"
        }
        tbl = make_stats_table(stats)
        tbl_sec = CollapsibleSection("Basic Statistics")
        tbl_sec.add_widget(tbl)
        self.vlay.addWidget(tbl_sec)
