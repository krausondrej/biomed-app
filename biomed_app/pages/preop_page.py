# pages/preop_page.py
import numpy as np
import pandas as pd
from matplotlib.figure import Figure
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea,
    QComboBox, QHBoxLayout, QSizePolicy
)
from PyQt5 import QtCore
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from ui_helpers import CollapsibleSection
from chart_utils import make_bar_chart, make_histogram
from table_utils import make_stats_table

class PreopPage(QWidget):
    def __init__(self, main_win, df):
        super().__init__()
        self.main = main_win
        # Originální DataFrame uchováváme pro reset filtru
        self.df_master = df.copy()
        self.selected_gender = "All"
        self._build_ui()

    def _build_ui(self):
        # Root layout s odsazením a mezerami
        root = QVBoxLayout(self)
        root.setContentsMargins(30, 20, 30, 20)
        root.setSpacing(20)

        # Titulek
        title = QLabel("PREOPERATIVE DATA")
        title.setObjectName("titleLabel")
        title.setAlignment(QtCore.Qt.AlignCenter)
        root.addWidget(title)

        # Podtitulek pro typ operace a rok
        self.header = QLabel("")
        self.header.setObjectName("subtitleLabel")
        self.header.setAlignment(QtCore.Qt.AlignCenter)
        root.addWidget(self.header)

        # Filtr podle pohlaví
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

        # Scroll area pro sekce
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

        # Společné CSS pro stránku
        self.setStyleSheet("""
            /* Titulek */
            #titleLabel {
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 5px;
            }
            /* Podtitulek */
            #subtitleLabel {
                font-size: 14px;
                color: #555555;
                margin-bottom: 15px;
            }
            /* Popisek filtru */
            #filterLabel {
                font-size: 14px;
                color: #333333;
            }
            /* Kontejner scrollu */
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
        # Vyčistit staré widgety
        for i in reversed(range(self.vlay.count())):
            w = self.vlay.itemAt(i).widget()
            if w:
                w.setParent(None)

        ty = self.main.current_op_type
        yr_sel = self.main.selected_year
        df = self.df_master.copy()

        # Filtrace podle roku
        if isinstance(yr_sel, str) and '-' in yr_sel:
            start, end = map(int, yr_sel.split('-'))
            df = df[df['Year'].between(start, end)]
        else:
            try:
                df = df[df['Year'] == int(yr_sel)]
            except:
                pass

        # Aktualizace podtitulku
        self.header.setText(f"Operation: {ty}   |   Year: {yr_sel}   |   N = {len(df)}")

        # Filtrace podle pohlaví
        if self.selected_gender.lower() in ["male", "female"]:
            df = df[df['Gender'] == self.selected_gender.lower()]

        # Pokud je prázdný dataset
        if df.empty:
            lbl = QLabel("No data for selected filters.")
            lbl.setAlignment(QtCore.Qt.AlignCenter)
            self.vlay.addWidget(lbl)
            return

        # 1) Number of Men and Women
        sec1 = CollapsibleSection("Number of Men and Women")
        counts_gender = df["Gender"].value_counts()

        # přejmenuj indexy z 'male','female' → 'Male','Female'
        counts_gender.index = counts_gender.index.str.capitalize()

        sec1.add_widget(make_bar_chart(
            counts_gender,
            "Statistics of the patients according to gender",
            "",  # xlabel
            "Number"  # ylabel
        ))
        self.vlay.addWidget(sec1)


        # 2) Age Distribution (categorical ranges)
        sec2 = CollapsibleSection("Age Distribution")

        raw_counts = df["Age"].value_counts()

        middle = [lbl for lbl in raw_counts.index if lbl not in ("<  25", ">  75")]
        middle_sorted = sorted(middle)   # nebo jen middle, pokud chcete zachovat původní pořadí
        ordered = ["<  25"] + middle_sorted + [">  75"]

        age_counts = raw_counts.reindex(ordered, fill_value=0)

        sec2.add_widget(make_bar_chart(
            age_counts,
            title="Age of patients",
            xlabel="",
            ylabel="Number of the patients"
        ))

        self.vlay.addWidget(sec2)
        
        # 3) BMI Distribution
        sec3 = CollapsibleSection("BMI Distribution")

        bmi = df["BMI"].dropna()
        bmi_min = int(np.floor(bmi.min()))
        bmi_max = int(np.ceil(bmi.max()))
        bins    = np.arange(bmi_min, bmi_max + 2, 2)

        hist_widget = make_histogram(
            bmi,
            bins=bins,
            title="Distribution of the patients according to the BMI",
            xlabel="BMI",
            ylabel="Number of the patients"
        )

        fig = hist_widget.figure
        ax  = fig.axes[0]
        start_tick = 0
        end_tick   = (bmi_max // 10 + 1) * 10
        ax.set_xticks(np.arange(start_tick, end_tick + 1, 10))
        ax.set_xlim(bins[0], bins[-1])
        
        for txt in list(ax.texts):
            txt.remove()

        fig.tight_layout()

        sec3.add_widget(hist_widget)
        self.vlay.addWidget(sec3)
        
        # 4) Comorbidities Before Surgery
        sec4 = CollapsibleSection("Prevalence of Comorbidities")

        com_sums = df[[
            "No_Comorbidities","Diabetes","COPD",
            "Hepatic_Disease","Renal_Disease",
            "Aortic_Aneurysm","Smoker"
        ]].sum()

        com_sums.index = [lbl.replace("_", " ").title() for lbl in com_sums.index]

        bar_widget = make_bar_chart(
            com_sums,
            title="Patient's Comorbidities before the surgery",
            xlabel="",
            ylabel="Number"
        )

        fig = bar_widget.figure
        ax  = fig.axes[0]
        for label in ax.get_xticklabels():
            label.set_rotation(45)
            label.set_ha("right")   # zarovnání k pravému okraji pro lepší čitelnost

        fig.tight_layout()

        sec4.add_widget(bar_widget)
        self.vlay.addWidget(sec4)

        # 5) Pre-operative Pain Score
        sec5 = CollapsibleSection("Pre-operative Pain Score")

        rest_counts  = df["Pain_rest"].value_counts().sort_index()
        act_counts   = df["Pain_activity"].value_counts().sort_index()
        last_counts  = df["Pain_last_week"].value_counts().sort_index()

        all_scores = sorted(set(rest_counts.index)
                            | set(act_counts.index)
                            | set(last_counts.index))

        rest = rest_counts .reindex(all_scores, fill_value=0)
        act  = act_counts  .reindex(all_scores, fill_value=0)
        last = last_counts .reindex(all_scores, fill_value=0)

        fig = Figure(figsize=(8, 5), dpi=100, facecolor='white')
        ax  = fig.add_subplot(111, facecolor='white')

        x     = np.arange(len(all_scores))
        width = 0.25
        
        bars1 = ax.bar(
            x - width, rest.values, width,
            label="In Rest",
            color="#E63946",  # červená
            edgecolor="#0D1B2A"
        )
        bars2 = ax.bar(
            x, act.values, width,
            label="During Activity",
            color="#457B9D",  # modrá
            edgecolor="#0D1B2A"
        )
        bars3 = ax.bar(
            x + width, last.values, width,
            label="Last Week",
            color="#2A9D8F",  # zelená
            edgecolor="#0D1B2A"
        )

        max_h = max(rest.max(), act.max(), last.max()) or 0
        for bars in (bars1, bars2, bars3):
            for rect in bars:
                h = rect.get_height()
                ax.text(
                    rect.get_x() + rect.get_width() / 2,
                    h + max_h * 0.02,
                    f"{int(h)}",
                    ha="center", va="bottom",
                    color="#0D1B2A",
                    fontsize=9
                )

        ax.set_title("Pre-operative Pain At The Site Of The Hernia", color="#0D1B2A")
        ax.set_xlabel("Intensity of the pain",            color="#0D1B2A", labelpad=16)
        ax.set_ylabel("Number of the patient's",                 color="#0D1B2A")
        ax.set_xticks(x)
        ax.set_xticklabels(all_scores, rotation=0)
        ax.legend()

        ax.spines['left'].set_color("#0D1B2A");   ax.spines['left'].set_linewidth(1.2)
        ax.spines['bottom'].set_color("#0D1B2A")
        ax.yaxis.set_ticks_position("left");      ax.xaxis.set_ticks_position("bottom")

        ax.grid(axis="y", color="#888888", alpha=0.3)
        ax.set_ylim(0, max_h * 1.4)

        fig.tight_layout()

        canvas = FigureCanvas(fig)
        canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        canvas.setMinimumHeight(600)

        sec5.add_widget(canvas)
        self.vlay.addWidget(sec5)

        sec6 = CollapsibleSection("Pre-operative Restrictions Score")

        cols = ["Restrict_inside", "Restrict_outside", "Restrict_sports", "Restrict_heavy"]
        labels = ["Daily Activities", "Outside Activities", "During Sport", "Heavy Labour"]

        counts = [df[col].value_counts().sort_index().reindex(sorted(df[col].unique()), fill_value=0) 
                for col in cols]

        all_scores = sorted({v for cnt in counts for v in cnt.index})
        counts = [cnt.reindex(all_scores, fill_value=0) for cnt in counts]

        fig = Figure(figsize=(8, 5), dpi=100, facecolor='white')
        ax  = fig.add_subplot(111, facecolor='white')

        x     = np.arange(len(all_scores))
        width = 0.2

        colors = ["#E63946", "#457B9D", "#2A9D8F", "#F4A261"]
        bars = []
        for i, cnt in enumerate(counts):
            bars.append(
                ax.bar(
                    x + (i-1.5)*width,  # center groups
                    cnt.values,
                    width,
                    label=labels[i],
                    color=colors[i],
                    edgecolor="#0D1B2A"
                )
            )

        max_h = max(c.max() for c in counts) or 0
        for barset in bars:
            for rect in barset:
                h = rect.get_height()
                ax.text(
                    rect.get_x() + rect.get_width() / 2,
                    h + max_h * 0.02,
                    f"{int(h)}",
                    ha="center", va="bottom",
                    color="#0D1B2A",
                    fontsize=8
                )

        ax.set_title("Pre-operative Restrictions of patients", color="#0D1B2A")
        ax.set_xlabel("Intensity of the restriction",       color="#0D1B2A", labelpad=16)
        ax.set_ylabel("Number of the patient's",                    color="#0D1B2A")
        ax.set_xticks(x)
        ax.set_xticklabels(all_scores, rotation=0)
        ax.legend()

        ax.spines['left'].set_color("#0D1B2A");   ax.spines['left'].set_linewidth(1.2)
        ax.spines['bottom'].set_color("#0D1B2A")
        ax.yaxis.set_ticks_position("left");      ax.xaxis.set_ticks_position("bottom")

        ax.grid(axis="y", color="#888888", alpha=0.3)
        ax.set_ylim(0, max_h * 1.4)

        fig.tight_layout()

        canvas = FigureCanvas(fig)
        canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        canvas.setMinimumHeight(600)

        sec6.add_widget(canvas)
        self.vlay.addWidget(sec6)

        # 7) Aesthetic Discomfort Score
        sec7 = CollapsibleSection("Aesthetic Discomfort Score")

        abd_counts = df["Esthetic_abdomen"].value_counts().sort_index()
        hern_counts = df["Esthetic_hernia"].value_counts().sort_index()

        all_scores = sorted(set(abd_counts.index) | set(hern_counts.index))
        abd = abd_counts.reindex(all_scores, fill_value=0)
        hern = hern_counts.reindex(all_scores, fill_value=0)

        fig = Figure(figsize=(8, 5), dpi=100, facecolor='white')
        ax  = fig.add_subplot(111, facecolor='white')

        x     = np.arange(len(all_scores))
        width = 0.35

        bars1 = ax.bar(
            x - width/2, abd.values, width,
            label="Shape of Abdomen",
            color="#E63946", edgecolor="#0D1B2A"
        )
        bars2 = ax.bar(
            x + width/2, hern.values, width,
            label="The Hernia Itself",
            color="#457B9D", edgecolor="#0D1B2A"
        )

        max_h = max(abd.max(), hern.max()) or 0
        for barset in (bars1, bars2):
            for rect in barset:
                h = rect.get_height()
                ax.text(
                    rect.get_x() + rect.get_width() / 2,
                    h + max_h * 0.02,
                    f"{int(h)}",
                    ha="center", va="bottom",
                    color="#0D1B2A",
                    fontsize=9
                )

        ax.set_title("Aesthetic Discomfort Score", color="#0D1B2A")
        ax.set_xlabel("Discomfort Score", color="#0D1B2A", labelpad=16)
        ax.set_ylabel("Count", color="#0D1B2A")
        ax.set_xticks(x)
        ax.set_xticklabels(all_scores, rotation=0)
        ax.legend()

        ax.spines['left'].set_color("#0D1B2A");   ax.spines['left'].set_linewidth(1.2)
        ax.spines['bottom'].set_color("#0D1B2A")
        ax.yaxis.set_ticks_position("left");      ax.xaxis.set_ticks_position("bottom")
        ax.grid(axis="y", color="#888888", alpha=0.3)
        ax.set_ylim(0, max_h * 1.4)

        fig.tight_layout()

        canvas = FigureCanvas(fig)
        canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        canvas.setMinimumHeight(600)

        sec7.add_widget(canvas)
        self.vlay.addWidget(sec7)
        
        # 8) Summary table
        df['Age_numeric'] = pd.to_numeric(df['Age'], errors='coerce')

        stats = {
            "Total patients": len(df),
            "Males": df["Gender"].value_counts().get("male", 0),
            "Females": df["Gender"].value_counts().get("female", 0),
            "Male %": f"{df['Gender'].value_counts(normalize=True).get('male', 0)*100:.1f}%",
            "Female %": f"{df['Gender'].value_counts(normalize=True).get('female', 0)*100:.1f}%",
            "Mean BMI": f"{df['BMI'].mean():.1f}" if not df['BMI'].dropna().empty else "N/A",
            "Median BMI": f"{df['BMI'].median():.1f}" if not df['BMI'].dropna().empty else "N/A",
            "BMI Std Dev": f"{df['BMI'].std():.1f}"  if not df['BMI'].dropna().empty else "N/A",
            "Min BMI": f"{df['BMI'].min():.1f}"      if not df['BMI'].dropna().empty else "N/A",
            "Max BMI": f"{df['BMI'].max():.1f}"      if not df['BMI'].dropna().empty else "N/A",
            "Mean Pain (rest)": f"{df['Pain_rest'].mean():.1f}"      if not df['Pain_rest'].dropna().empty else "N/A",
            "Mean Pain (activity)": f"{df['Pain_activity'].mean():.1f}" if not df['Pain_activity'].dropna().empty else "N/A",
            "Mean Pain (last week)": f"{df['Pain_last_week'].mean():.1f}" if not df['Pain_last_week'].dropna().empty else "N/A",
            "Mean Comorbidities": f"{df[['Diabetes','COPD','Renal_Disease','Smoker']].sum(axis=1).mean():.2f}"
        }

        tbl_sec = CollapsibleSection("Basic Statistics")
        wrapper = QWidget()
        wrapper_lay = QVBoxLayout(wrapper)
        wrapper_lay.setContentsMargins(0, 10, 0, 0)   # left, top=20px, right, bottom
        wrapper_lay.addWidget(make_stats_table(stats))
        tbl_sec.add_widget(wrapper)
        self.vlay.addWidget(tbl_sec)
