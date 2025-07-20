# pages/preop_page.py
import numpy as np
import pandas as pd
from matplotlib.figure import Figure
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea,
    QComboBox, QHBoxLayout, QSizePolicy
)
import matplotlib.pyplot as plt
from PyQt5 import QtCore
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from ui_helpers import CollapsibleSection
from chart_utils import make_bar_chart, make_histogram
from table_utils import make_stats_table
from ui_helpers import add_download_button


class PreopPage(QWidget):
    def __init__(self, main_win, df):
        super().__init__()
        self.main = main_win
        self.df_master = df.copy()
        self.selected_gender = "All"
        self.selected_age_group = "All"
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(30, 20, 30, 20)
        root.setSpacing(20)

        title = QLabel("PREOPERATIVE DATA")
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

    def _filter_age(self, age_group):
        self.selected_age_group = age_group
        self.update_view()

    def update_view(self):
        for i in reversed(range(self.vlay.count())):
            w = self.vlay.itemAt(i).widget()
            if w:
                w.setParent(None)

        if self.df_master is None or self.df_master.empty:
            lbl = QLabel("Error: data not available")
            lbl.setAlignment(QtCore.Qt.AlignCenter)
            self.vlay.addWidget(lbl)
            return

        ty = self.main.current_op_type
        yr_sel = self.main.selected_year
        df = self.df_master.copy()

        if 'Year' in df.columns:
            if isinstance(yr_sel, str) and '-' in yr_sel:
                try:
                    start, end = map(int, yr_sel.split('-'))
                    df = df[df['Year'].between(start, end)]
                except:
                    pass
            else:
                try:
                    df = df[df['Year'] == int(yr_sel)]
                except:
                    pass
        else:
            lbl = QLabel("Note: The 'Year' column is not available")
            lbl.setAlignment(QtCore.Qt.AlignCenter)
            self.vlay.addWidget(lbl)

        if self.selected_gender.lower() in ["male", "female"]:
            if 'Gender' in df.columns:
                df = df[df['Gender'] == self.selected_gender.lower()]
            else:
                lbl = QLabel("Note: The 'Gender' column is not available")
                lbl.setAlignment(QtCore.Qt.AlignCenter)
                self.vlay.addWidget(lbl)

        if self.selected_age_group != "All":
            if "Age" in df.columns:
                df = df[df["Age"] == self.selected_age_group]
            else:
                lbl = QLabel("Note: The 'Age' column is not available")
                lbl.setAlignment(QtCore.Qt.AlignCenter)
                self.vlay.addWidget(lbl)

        self.header.setText(
            f"Operation: {ty}   |   Year: {yr_sel}   |   N = {len(df)}"
        )

        if df.empty:
            lbl = QLabel("No data for the selected filter")
            lbl.setAlignment(QtCore.Qt.AlignCenter)
            self.vlay.addWidget(lbl)
            return

        sec1 = CollapsibleSection("Number of Men and Women")
        if "Gender" not in df.columns or df["Gender"].dropna().empty:
            lbl = QLabel("No Data: Gender statistics")
            lbl.setAlignment(QtCore.Qt.AlignCenter)
            self.vlay.addWidget(lbl)
        else:
            counts_gender = df["Gender"].value_counts()
            counts_gender.index = counts_gender.index.str.capitalize()

            chart = make_bar_chart(
                counts_gender,
                "Statistics of the patients according to gender",
                "",
                "Number"
            )
            sec1.add_widget(add_download_button(chart, "Download Bar Chart"))
            self.vlay.addWidget(sec1)


        sec2 = CollapsibleSection("Distribution of Patients According to the Age")
        if "Age" not in df.columns or df["Age"].dropna().empty:
            lbl = QLabel("No Data: Age Distribution")
            lbl.setAlignment(QtCore.Qt.AlignCenter)
            self.vlay.addWidget(lbl)
        else:
            raw_counts = df["Age"].value_counts()

            middle = [lbl for lbl in raw_counts.index if lbl not in ("<  25", ">  75")]
            middle_sorted = sorted(middle)
            ordered = ["<  25"] + middle_sorted + [">  75"]

            age_counts = raw_counts.reindex(ordered, fill_value=0)

            chart = make_bar_chart(
                age_counts,
                title="Age of patients",
                xlabel="",
                ylabel="Number of the patients"
            )
            sec2.add_widget(add_download_button(chart, "Download Bar Chart"))
            self.vlay.addWidget(sec2)


        sec3 = CollapsibleSection("Distribution of Patients According to the BMI")
        if "BMI" not in df.columns or df["BMI"].dropna().empty:
            lbl = QLabel("No Data: BMI Distribution")
            lbl.setAlignment(QtCore.Qt.AlignCenter)
            self.vlay.addWidget(lbl)
        else:
            bmi = df["BMI"].dropna()
            bmi_min = int(np.floor(bmi.min()))
            bmi_max = int(np.ceil(bmi.max()))
            bins = np.arange(bmi_min, bmi_max + 2, 2)

            # Histogram
            hist_widget = make_histogram(
                bmi,
                bins=bins,
                title="Distribution of the patients according to the BMI",
                xlabel="BMI",
                ylabel="Number of the patients"
            )
            fig = hist_widget.figure
            ax = fig.axes[0]
            ax.set_xticks(np.arange(0, (bmi_max // 10 + 1) * 10 + 1, 10))
            ax.set_xlim(bins[0], bins[-1])
            for txt in list(ax.texts):
                txt.remove()
            fig.tight_layout()
            sec3.add_widget(add_download_button(hist_widget, "Download histogram"))

            # Scatter plot
            fig2, ax2 = plt.subplots()
            ax2.scatter(range(len(bmi)), bmi, color="red", s=20)
            ax2.set_title("BMI values of individual patients")
            ax2.set_xlabel("Patient index")
            ax2.set_ylabel("BMI")
            fig2.tight_layout()

            scatter_widget = FigureCanvas(fig2)
            sec3.add_widget(add_download_button(scatter_widget, "Download histogram"))

            self.vlay.addWidget(sec3)


        sec4 = CollapsibleSection("Comorbidities Before the Surgery")

        comorb_cols = [
            "No_Comorbidities", "Diabetes", "COPD",
            "Hepatic_Disease", "Renal_Disease",
            "Aortic_Aneurysm", "Smoker"
        ]

        valid_cols = [col for col in comorb_cols if col in df.columns]

        if not valid_cols:
            lbl = QLabel("No Data: Comorbidities")
            lbl.setAlignment(QtCore.Qt.AlignCenter)
            self.vlay.addWidget(lbl)
        else:
            com_sums = df[valid_cols].sum()
            if com_sums.sum() == 0:
                lbl = QLabel("No Data: Comorbidities")
                lbl.setAlignment(QtCore.Qt.AlignCenter)
                self.vlay.addWidget(lbl)
            else:
                com_sums.index = [lbl.replace("_", " ").title() for lbl in com_sums.index]

                bar_widget = make_bar_chart(
                    com_sums,
                    title="Patient's Comorbidities before the surgery",
                    xlabel="",
                    ylabel="Number"
                )

                fig = bar_widget.figure
                ax = fig.axes[0]
                for label in ax.get_xticklabels():
                    label.set_rotation(45)
                    label.set_ha("right")

                fig.tight_layout()

                sec4.add_widget(bar_widget)
                sec4.add_widget(add_download_button(bar_widget, "Download Bar Chart"))
                self.vlay.addWidget(sec4)


        sec5 = CollapsibleSection("Pre-operative Pain at the Site of the Hernia")
        required_pain_cols = ["Pain_rest", "Pain_activity", "Pain_last_week"]
        valid_pain_cols = [col for col in required_pain_cols if col in df.columns]

        if len(valid_pain_cols) < 3:
            lbl = QLabel("No Data: Pain Score")
            lbl.setAlignment(QtCore.Qt.AlignCenter)
            self.vlay.addWidget(lbl)
        else:
            rest_counts = df["Pain_rest"].value_counts().sort_index()
            act_counts = df["Pain_activity"].value_counts().sort_index()
            last_counts = df["Pain_last_week"].value_counts().sort_index()

            all_scores = sorted(set(rest_counts.index) | set(act_counts.index) | set(last_counts.index))

            rest = rest_counts.reindex(all_scores, fill_value=0)
            act = act_counts.reindex(all_scores, fill_value=0)
            last = last_counts.reindex(all_scores, fill_value=0)

            if rest.sum() == 0 and act.sum() == 0 and last.sum() == 0:
                lbl = QLabel("No Data: Pain Score")
                lbl.setAlignment(QtCore.Qt.AlignCenter)
                self.vlay.addWidget(lbl)
            else:
                fig = Figure(figsize=(8, 5), dpi=100, facecolor='white')
                ax = fig.add_subplot(111, facecolor='white')

                x = np.arange(len(all_scores))
                width = 0.25

                bars1 = ax.bar(x - width, rest.values, width, label="In Rest", color="#E63946", edgecolor="#0D1B2A")
                bars2 = ax.bar(x, act.values, width, label="During Activity", color="#457B9D", edgecolor="#0D1B2A")
                bars3 = ax.bar(x + width, last.values, width, label="Last Week", color="#2A9D8F", edgecolor="#0D1B2A")

                max_h = max(rest.max(), act.max(), last.max()) or 0
                for bars in (bars1, bars2, bars3):
                    for rect in bars:
                        h = rect.get_height()
                        ax.text(rect.get_x() + rect.get_width() / 2, h + max_h * 0.02, f"{int(h)}",
                                ha="center", va="bottom", color="#0D1B2A", fontsize=9)

                ax.set_title("Pre-operative Pain At The Site Of The Hernia", color="#0D1B2A")
                ax.set_xlabel("Intensity of the pain", color="#0D1B2A", labelpad=16)
                ax.set_ylabel("Number of the patient's", color="#0D1B2A")
                ax.set_xticks(x)
                ax.set_xticklabels(all_scores, rotation=0)
                ax.legend()

                ax.spines['left'].set_color("#0D1B2A")
                ax.spines['left'].set_linewidth(1.2)
                ax.spines['bottom'].set_color("#0D1B2A")
                ax.yaxis.set_ticks_position("left")
                ax.xaxis.set_ticks_position("bottom")
                ax.grid(axis="y", color="#888888", alpha=0.3)
                ax.set_ylim(0, max_h * 1.4)

                fig.tight_layout()

                canvas = FigureCanvas(fig)
                canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

                sec5.add_widget(add_download_button(canvas, "Download Bar Chart"))
                self.vlay.addWidget(sec5)


        sec6 = CollapsibleSection("Pre-operative Restrictions")

        cols = ["Restrict_inside", "Restrict_outside", "Restrict_sports", "Restrict_heavy"]
        labels = ["Daily Activities", "Outside Activities", "During Sport", "Heavy Labour"]
        valid_cols = [col for col in cols if col in df.columns]

        if len(valid_cols) < len(cols):
            lbl = QLabel("No Data: Restrictions Score")
            lbl.setAlignment(QtCore.Qt.AlignCenter)
            self.vlay.addWidget(lbl)
        else:
            counts = []
            for col in cols:
                values = df[col].dropna()
                if values.empty:
                    counts.append(pd.Series(dtype=int))
                else:
                    ordered_index = sorted(values.unique())
                    cnt = values.value_counts().sort_index().reindex(ordered_index, fill_value=0)
                    counts.append(cnt)

            all_scores = sorted({v for cnt in counts for v in cnt.index})
            if not all_scores or all(sum(cnt.values) == 0 for cnt in counts):
                lbl = QLabel("No Data: Restrictions Score")
                lbl.setAlignment(QtCore.Qt.AlignCenter)
                self.vlay.addWidget(lbl)
            else:
                counts = [cnt.reindex(all_scores, fill_value=0) for cnt in counts]

                fig = Figure(figsize=(8, 5), dpi=100, facecolor='white')
                ax = fig.add_subplot(111, facecolor='white')

                x = np.arange(len(all_scores))
                width = 0.2
                colors = ["#E63946", "#457B9D", "#2A9D8F", "#F4A261"]
                bars = []

                for i, cnt in enumerate(counts):
                    bars.append(
                        ax.bar(
                            x + (i - 1.5) * width,
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
                ax.set_xlabel("Intensity of the restriction", color="#0D1B2A", labelpad=16)
                ax.set_ylabel("Number of the patient's", color="#0D1B2A")
                ax.set_xticks(x)
                ax.set_xticklabels(all_scores, rotation=0)
                ax.legend()

                ax.spines['left'].set_color("#0D1B2A")
                ax.spines['left'].set_linewidth(1.2)
                ax.spines['bottom'].set_color("#0D1B2A")
                ax.yaxis.set_ticks_position("left")
                ax.xaxis.set_ticks_position("bottom")
                ax.grid(axis="y", color="#888888", alpha=0.3)
                ax.set_ylim(0, max_h * 1.4)

                fig.tight_layout()

                canvas = FigureCanvas(fig)
                canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

                sec6.add_widget(add_download_button(canvas, "Download Bar Chart"))
                self.vlay.addWidget(sec6)


        sec7 = CollapsibleSection("Preoperative Estetical Discomfort")
        cols = ["Esthetic_abdomen", "Esthetic_hernia"]
        if not all(col in df.columns for col in cols):
            lbl = QLabel("No Data: Preoperative estetical discomfort")
            lbl.setAlignment(QtCore.Qt.AlignCenter)
            self.vlay.addWidget(lbl)
        else:
            abd_counts = df["Esthetic_abdomen"].dropna().value_counts().sort_index()
            hern_counts = df["Esthetic_hernia"].dropna().value_counts().sort_index()

            if abd_counts.empty and hern_counts.empty:
                lbl = QLabel("No Data: Preoperative estetical discomfort")
                lbl.setAlignment(QtCore.Qt.AlignCenter)
                self.vlay.addWidget(lbl)
            else:
                all_scores = sorted(set(abd_counts.index) | set(hern_counts.index))
                abd = abd_counts.reindex(all_scores, fill_value=0)
                hern = hern_counts.reindex(all_scores, fill_value=0)

                fig = Figure(figsize=(8, 5), dpi=100, facecolor='white')
                ax = fig.add_subplot(111, facecolor='white')

                x = np.arange(len(all_scores))
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

                ax.spines['left'].set_color("#0D1B2A")
                ax.spines['left'].set_linewidth(1.2)
                ax.spines['bottom'].set_color("#0D1B2A")
                ax.yaxis.set_ticks_position("left")
                ax.xaxis.set_ticks_position("bottom")
                ax.grid(axis="y", color="#888888", alpha=0.3)
                ax.set_ylim(0, max_h * 1.4)

                fig.tight_layout()

                canvas = FigureCanvas(fig)
                canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

                sec7.add_widget(add_download_button(canvas, "Download Bar Chart"))
                self.vlay.addWidget(sec7)


        if "Age" in df.columns:
            df['Age_numeric'] = pd.to_numeric(df['Age'], errors='coerce')

        stats = {
            "Total patients": len(df),
            "Males": df["Gender"].value_counts().get("male", 0) if "Gender" in df.columns else "N/A",
            "Females": df["Gender"].value_counts().get("female", 0) if "Gender" in df.columns else "N/A",
            "Male %": f"{df['Gender'].value_counts(normalize=True).get('male', 0)*100:.1f}%" if "Gender" in df.columns else "N/A",
            "Female %": f"{df['Gender'].value_counts(normalize=True).get('female', 0)*100:.1f}%" if "Gender" in df.columns else "N/A",
            "Mean BMI": f"{df['BMI'].mean():.1f}" if "BMI" in df.columns and not df['BMI'].dropna().empty else "N/A",
            "Median BMI": f"{df['BMI'].median():.1f}" if "BMI" in df.columns and not df['BMI'].dropna().empty else "N/A",
            "BMI Std Dev": f"{df['BMI'].std():.1f}" if "BMI" in df.columns and not df['BMI'].dropna().empty else "N/A",
            "Min BMI": f"{df['BMI'].min():.1f}" if "BMI" in df.columns and not df['BMI'].dropna().empty else "N/A",
            "Max BMI": f"{df['BMI'].max():.1f}" if "BMI" in df.columns and not df['BMI'].dropna().empty else "N/A",
            "Mean Pain (rest)": f"{df['Pain_rest'].mean():.1f}" if "Pain_rest" in df.columns and not df['Pain_rest'].dropna().empty else "N/A",
            "Mean Pain (activity)": f"{df['Pain_activity'].mean():.1f}" if "Pain_activity" in df.columns and not df['Pain_activity'].dropna().empty else "N/A",
            "Mean Pain (last week)": f"{df['Pain_last_week'].mean():.1f}" if "Pain_last_week" in df.columns and not df['Pain_last_week'].dropna().empty else "N/A",
            "Mean Comorbidities": (
                f"{df[['Diabetes', 'COPD', 'Renal_Disease', 'Smoker']].sum(axis=1).mean():.2f}"
                if all(col in df.columns for col in ['Diabetes', 'COPD', 'Renal_Disease', 'Smoker'])
                else "N/A"
            )
        }

        tbl_sec = CollapsibleSection("Basic Statistics")
        wrapper = QWidget()
        wrapper_lay = QVBoxLayout(wrapper)
        wrapper_lay.setContentsMargins(0, 10, 0, 0)
        wrapper_lay.addWidget(make_stats_table(stats))
        tbl_sec.add_widget(wrapper)
        self.vlay.addWidget(tbl_sec)