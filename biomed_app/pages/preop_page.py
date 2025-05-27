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
        self.df   = df
        # Master DataFrame pro filtrování
        self.df_master = df.copy()
        self.selected_gender = "All"
        self._build_ui()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0,0,0,0)
        lay.setSpacing(2)

        title = QLabel("Preoperative Data – Visualization and Table")
        title.setObjectName("titleLabel")
        title.setAlignment(QtCore.Qt.AlignCenter)
        lay.addWidget(title)

        # Header pro typ a rok
        self.header = QLabel()
        self.header.setAlignment(QtCore.Qt.AlignCenter)
        lay.addWidget(self.header)
        
        # Filtr pohlaví
        gender_layout = QHBoxLayout()
        gender_layout.setSpacing(20)
        gender_layout.setAlignment(QtCore.Qt.AlignHCenter)
        gender_label = QLabel("Sex filter:")
        gender_label.setObjectName("filterLabel")
        gender_layout.addWidget(gender_label)
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["All", "Male", "Female"])
        self.gender_combo.currentTextChanged.connect(self._filter_gender)
        gender_layout.addWidget(self.gender_combo)
        lay.addLayout(gender_layout)

        # Scroll area
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

    def _filter_gender(self, gender_text):
        self.selected_gender = gender_text
        self.update_view()

    def update_view(self):
        # Vyčistit staré widgety
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

        if df.empty:
            lbl = QLabel("No data for selected filters.")
            lbl.setAlignment(QtCore.Qt.AlignCenter)
            self.vlay.addWidget(lbl)
            return

        # 1) Number of Men and Women
        sec1 = CollapsibleSection("Number of Men and Women")
        counts_gender = df["Gender"].value_counts()
        sec1.add_widget(make_bar_chart(
            counts_gender, "Number of Men and Women", "Gender", "Count"
        ))
        self.vlay.addWidget(sec1)

        # 2) Age Distribution (categorical ranges)
        sec2 = CollapsibleSection("Age Distribution")
        age_counts = df["Age"].fillna("Unknown").value_counts().sort_index()
        sec2.add_widget(make_bar_chart(
            age_counts, "Age Distribution", "Age Range", "Count"
        ))
        self.vlay.addWidget(sec2)

        # 3) BMI Distribution
        sec3 = CollapsibleSection("BMI Distribution")
        sec3.add_widget(make_histogram(
            df["BMI"], bins=10,
            title="BMI Distribution", xlabel="BMI", ylabel="Count"
        ))
        self.vlay.addWidget(sec3)

        # 4) Comorbidities Before Surgery
        sec4 = CollapsibleSection("Prevalence of Comorbidities")
        com_sums = df[[
            "No_Comorbidities","Diabetes","COPD",
            "Hepatic_Disease","Renal_Disease",
            "Aortic_Aneurysm","Smoker"
        ]].sum()
        sec4.add_widget(make_bar_chart(
            com_sums, "Prevalence of Comorbidities", "Comorbidity", "Patients"
        ))
        self.vlay.addWidget(sec4)

        # 5) Pre-operative Pain Score
        sec5 = CollapsibleSection("Pre-operative Pain Score")
        sec5.add_widget(make_histogram(
            df["Preop_Pain_Score"], bins=10,
            title="Pre-operative Pain Score", xlabel="Pain Score", ylabel="Count"
        ))
        self.vlay.addWidget(sec5)

        # 6) Pre-operative Restrictions Score
        sec6 = CollapsibleSection("Pre-operative Restrictions Score")
        sec6.add_widget(make_histogram(
            df["Preop_Restrict_Score"], bins=10,
            title="Pre-operative Restrictions Score", xlabel="Restrictions Score", ylabel="Count"
        ))
        self.vlay.addWidget(sec6)

        # 7) Aesthetic Discomfort Score
        sec7 = CollapsibleSection("Aesthetic Discomfort Score")
        sec7.add_widget(make_histogram(
            df["Esthetic_Discomfort_Score"], bins=10,
            title="Aesthetic Discomfort Score", xlabel="Discomfort Score", ylabel="Count"
        ))
        self.vlay.addWidget(sec7)

        # 8) Summary table
        stats = {
            "Total patients": len(df),
            "Males": df["Gender"].value_counts().get("male", 0),
            "Females": df["Gender"].value_counts().get("female", 0),
            "Mean BMI": f"{df['BMI'].mean():.1f}",
            "Median BMI": f"{df['BMI'].median():.1f}"
        }
        tbl_sec = CollapsibleSection("Basic Statistics")
        tbl_sec.add_widget(make_stats_table(stats))
        self.vlay.addWidget(tbl_sec)
