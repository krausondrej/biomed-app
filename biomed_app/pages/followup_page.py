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
        gender_layout.setContentsMargins(0, 10, 0, 0)
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
                        .value_counts()
        sec1 = CollapsibleSection("Occurrence of Complications")
        sec1.add_widget(make_bar_chart(
            occ_counts,
            "Complications at FU1",
            "",
            "Number"
        ))
        self.vlay.addWidget(sec1)

       # 2) Type of Follow-Up Complications
        cols = [
            "FU_Seroma",
            "FU_Hematoma",
            "FU_Pain",
            "FU_SSI",
            "FU_Mesh_Infection",
            "FU_Other"
        ]
        counts = df[cols].sum().fillna(0).astype(int)

        label_map = {
            "FU_Seroma":         "Seroma",
            "FU_Hematoma":       "Hematoma",
            "FU_Pain":           "Pain",
            "FU_SSI":            "Surgical site infection (SSI)",
            "FU_Mesh_Infection": "Mesh infection",
            "FU_Other":          "Other"
        }

        counts = counts.rename(index=label_map)

        counts = counts[counts > 0]

        sec2 = CollapsibleSection("Type of Complications")
        if counts.empty:
            sec2.add_widget(QLabel("No follow-up complications for selected filters."))
        else:
            chart = make_bar_chart(
                counts,
                title="Type of Complications at FU1",
                xlabel="",
                ylabel="Number"
            )
            fig = chart.figure
            ax  = fig.axes[0]
            for lbl in ax.get_xticklabels():
                lbl.set_rotation(45)
                lbl.set_ha("right")
            fig.tight_layout()

            sec2.add_widget(chart)

        self.vlay.addWidget(sec2)

        # 3) Summary Statistics
        has_comp = df["Followup_Complications"].dropna().astype(bool)
        n_true   = int(has_comp.sum())
        n_total  = len(df)
        stats = {
            "Total patients":          n_total,
            "Complications (Yes)":     n_true,
            "Complications (No)":      n_total - n_true,
            "Distinct complication types": len(counts[counts > 0])
        }

        # % s komplikacemi
        stats["% with complications"] = f"{n_true/n_total*100:.1f}%"

        # Průměrný počet typů komplikací na pacienta
        comp_per_patient = df[cols].sum(axis=1)
        stats["Avg complications/patient"] = f"{comp_per_patient.mean():.2f}"

        # Nejčastější typ komplikace
        nonzero = counts[counts > 0]
        if not nonzero.empty:
            stats["Most common complication"] = nonzero.idxmax()

        # Celkový počet komplikací (všech typů)
        stats["Total complication events"] = int(comp_per_patient.sum())

        # Demografie podle pohlaví
        gender_counts = df["Gender"].value_counts()
        stats["Male %"]   = f"{gender_counts.get('male',0)/n_total*100:.1f}%"
        stats["Female %"] = f"{gender_counts.get('female',0)/n_total*100:.1f}%"

        # Trend podle let
        yearly = df["Year"].value_counts().sort_index()
        if not yearly.empty:
            stats["Years covered"]    = f"{yearly.index.min()}–{yearly.index.max()}"
            stats["Avg patients/year"] = f"{yearly.mean():.1f}"

        # Vložení do GUI
        tbl_sec = CollapsibleSection("Summary Statistics")
        wrapper = QWidget()
        wrapper_lay = QVBoxLayout(wrapper)
        wrapper_lay.setContentsMargins(0, 10, 0, 0)
        wrapper_lay.addWidget(make_stats_table(stats))
        tbl_sec.add_widget(wrapper)
        self.vlay.addWidget(tbl_sec)