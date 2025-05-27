from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QHBoxLayout, QComboBox
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
        lay = QVBoxLayout(self)

        lbl = QLabel("Follow-Up Complications")
        lbl.setObjectName("titleLabel")
        lbl.setAlignment(QtCore.Qt.AlignCenter)
        lay.addWidget(lbl)

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

        # ScrollArea s transparentním pozadím a černým scrollbarem
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            /* celý scrollArea průhledně */
            QScrollArea {
                background: transparent;
                border: none;
            }
            /* track scrollbaru */
            QScrollBar:vertical {
                background: transparent;
                width: 12px;
                margin: 0;
            }
            /* jezdec scrollbaru */
            QScrollBar::handle:vertical {
                background: #000000;
                min-height: 20px;
                border-radius: 6px;
            }
            /* skryj šipky */
            QScrollBar::sub-line:vertical,
            QScrollBar::add-line:vertical {
                height: 0;
            }
            /* zbytek drážky */
            QScrollBar::sub-page:vertical,
            QScrollBar::add-page:vertical {
                background: none;
            }
        """)
        # viewport musí být taky průhledný
        scroll.viewport().setStyleSheet("background: transparent;")
        scroll.viewport().setAttribute(QtCore.Qt.WA_TranslucentBackground)

        # kontejner pod scrollArea
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
        ty = self.main.current_op_type or "All types"
        yr = self.main.selected_year   or "All years"
        self.header.setText(f"Type: {ty} ┃ Year: {yr}")

        # vyčistit obsah
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
        
        # filtrovat podle roku
        df = self.df.copy()
        if yr != "2021-2025":
            try:
                df = df[df["Year"] == int(yr)]
            except ValueError:
                pass

        if df.empty:
            lbl = QLabel("No follow-up data for selected year.")
            lbl.setAlignment(QtCore.Qt.AlignCenter)
            self.vlay.addWidget(lbl)
            return

        if self.selected_gender.lower() in ["male", "female"]:
            df = df[df["Gender"] == self.selected_gender.lower()]

        # 1) Occurrence of complications
        occ_counts = df["Followup_Complications"] \
                        .map({0: "No", 1: "Yes"}) \
                        .value_counts()
        sec1 = CollapsibleSection("Occurrence of Complications")
        sec1.add_widget(make_bar_chart(
            occ_counts,
            "Occurrence of Follow-Up Complications",
            "Occurrence",
            "Count"
        ))
        self.vlay.addWidget(sec1)

        # 2) Type of complications
        cols = [
            "FU_Seroma",
            "FU_Hematoma",
            "FU_Pain",
            "FU_SSI",
            "FU_Mesh_Infection",
            "FU_Other"
        ]
        # spočítáme jedničky pro každý typ bez sčítání přes stack
        counts = df[cols].sum()
        counts = counts.fillna(0).astype(int)
        type_counts = counts

        sec2 = CollapsibleSection("Type of Complications")
        sec2.add_widget(make_bar_chart(
            type_counts,
            "Type of Follow-Up Complications",
            "Complication Type",
            "Count"
        ))
        self.vlay.addWidget(sec2)

        # 3) (Volitelně) přehledová tabulka
        stats = {
            "Total patients":      len(df),
            "Complications (Yes)":  occ_counts.get("Yes", 0),
            "Complications (No)":   occ_counts.get("No", 0)
        }
        sec3 = CollapsibleSection("Summary Statistics")
        sec3.add_widget(make_stats_table(stats))
        self.vlay.addWidget(sec3)
