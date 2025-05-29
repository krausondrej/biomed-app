# pages/operative_page.py
import pandas as pd
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea,
    QHBoxLayout, QComboBox
)
from PyQt5 import QtCore
from ui_helpers import CollapsibleSection
from chart_utils import make_bar_chart
from table_utils import make_stats_table
from ui_helpers import add_download_button


class OperativePage(QWidget):
    def __init__(self, main_win, df):
        super().__init__()
        self.main = main_win
        self.df = df
        self.selected_age_group = "All"
        self.selected_gender = "All"
        self._build_ui()

    def _build_ui(self):
        # Root layout with margins and spacing
        root = QVBoxLayout(self)
        root.setContentsMargins(30, 20, 30, 20)
        root.setSpacing(15)

        # Title
        title = QLabel("OPERATIVE DATA")
        title.setObjectName("titleLabel")
        title.setAlignment(QtCore.Qt.AlignCenter)
        root.addWidget(title)

        # Subtitle / header
        self.header = QLabel("")
        self.header.setObjectName("subtitleLabel")
        self.header.setAlignment(QtCore.Qt.AlignCenter)
        root.addWidget(self.header)

        # Společný layout pro oba filtry (vedle sebe)
        filters_layout = QHBoxLayout()
        filters_layout.setSpacing(30)  # mezera mezi filtry
        filters_layout.setAlignment(QtCore.Qt.AlignCenter)

        # --- Filtr pohlaví ---
        gender_label = QLabel("Sex:")
        gender_label.setObjectName("filterLabel")
        filters_layout.addWidget(gender_label)

        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["All", "Male", "Female"])
        self.gender_combo.currentTextChanged.connect(self._filter_gender)
        filters_layout.addWidget(self.gender_combo)

        # --- Filtr věku ---
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

        # Přidej do root layoutu
        root.addLayout(filters_layout)

        # Scroll area for collapsible sections
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setObjectName("dataScroll")
        scroll.setStyleSheet("""
            QScrollArea#dataScroll {
                background: #F9F9F9;
                border: none;
            }
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
            /* CollapsibleSection header */
            CollapsibleSection > QWidget {
                border-radius: 6px;
            }
            /* CollapsibleSection title */
            CollapsibleSection QLabel {
                font-size: 16px;
                font-weight: bold;
            }
            /* Chart and table wrappers */
            QWidget#chartWrapper, QWidget#tableWrapper {
                background: #FFFFFF;
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                padding: 10px;
            }
        """)

    def _filter_gender(self, gender_text):
        self.selected_gender = gender_text
        self.update_view()

    def _filter_age(self, age_group):
        self.selected_age_group = age_group
        self.update_view()

    def update_view(self):
        # Clear previous content
        for i in reversed(range(self.vlay.count())):
            w = self.vlay.itemAt(i).widget()
            if w:
                w.setParent(None)

        ty = self.main.current_op_type
        yr_sel = self.main.selected_year
        df = self.df.copy()

        # Year filtering
        if isinstance(yr_sel, str) and '-' in yr_sel:
            start, end = map(int, yr_sel.split('-'))
            df = df[df['Year'].between(start, end)]
        else:
            try:
                yr = int(yr_sel)
                df = df[df['Year'] == yr]
            except Exception:
                pass

        # Header update
        self.header.setText(f"{ty}  |  {yr_sel}  |  N = {len(df)}")

        # Gender filtering
        if self.selected_gender.lower() in ["male", "female"]:
            df = df[df["Gender"] == self.selected_gender.lower()]

        # Filtrace podle věku
        if self.selected_age_group != "All":
            df = df[df["Age"] == self.selected_age_group]

        # 1) Indication for Surgery
        sec1 = CollapsibleSection("Indication for Surgery")
        chart1 = make_bar_chart(
            df["Indication"].value_counts(),
            "Indication for Surgery", "", "Number of Patients"
        )
        chart1.setObjectName("chartWrapper")
        sec1.add_widget(add_download_button(chart1, "Download Bar Chart"))
        self.vlay.addWidget(sec1)

        # 2) Type-specific sections
        if ty == "GHR":
            # Side of the Hernia
            right = df["GHR_Side_Right"].fillna(0).astype(int)
            left = df["GHR_Side_Left"].fillna(0).astype(int)

            def side_cat(r, l):
                if r and l:
                    return "Bilateral"
                if r:
                    return "Right"
                if l:
                    return "Left"
            side_series = pd.Series([
                side_cat(r, l) for r, l in zip(right, left)
            ]).dropna()
            counts = side_series.value_counts().reindex(
                ["Right", "Left", "Bilateral"], fill_value=0
            )
            sec_side = CollapsibleSection("Side of the Hernia")
            chart2 = make_bar_chart(
                counts, "Side of the Hernia", "Side", "Count"
            )
            chart2.setObjectName("chartWrapper")

            sec_side.add_widget(add_download_button(
                chart2, "Download Bar Chart"))
            self.vlay.addWidget(sec_side)

            # Previous Repairs Right
            sec_r = CollapsibleSection("Previous Repairs (Right)")
            rep_r = df["GHR_Prev_Repairs_Right"].dropna().astype(int)
            cnt_r = rep_r.value_counts().sort_index()
            cnt_r = cnt_r[cnt_r.index > 0]
            chart_r = make_bar_chart(
                cnt_r, "Previous Repairs (Right)", "Repairs", "Count"
            )
            chart_r.setObjectName("chartWrapper")

            sec_r.add_widget(add_download_button(
                chart_r, "Download Bar Chart"))
            self.vlay.addWidget(sec_r)

            # Previous Repairs Left
            sec_l = CollapsibleSection("Previous Repairs (Left)")
            rep_l = df["GHR_Prev_Repairs_Left"].dropna().astype(int)
            cnt_l = rep_l.value_counts().sort_index()
            cnt_l = cnt_l[cnt_l.index > 0]
            chart_l = make_bar_chart(
                cnt_l, "Previous Repairs (Left)", "Repairs", "Count"
            )
            chart_l.setObjectName("chartWrapper")

            sec_l.add_widget(add_download_button(
                chart_l, "Download Bar Chart"))
            self.vlay.addWidget(sec_l)

            # Groin Hernia Type Right
            sec_tr = CollapsibleSection("Groin Hernia Type (Right)")
            counts_tr = df[[
                "GHR_Type_Right_Lateral", "GHR_Type_Right_Medial",
                "GHR_Type_Right_Femoral", "GHR_Type_Right_Obturator"
            ]].sum()
            counts_tr.index = ["Lateral", "Medial", "Femoral", "Obturator"]
            counts_tr = counts_tr[counts_tr > 0]
            chart_tr = make_bar_chart(
                counts_tr, "Type (Right)", "", "Count"
            )
            chart_tr.setObjectName("chartWrapper")
            sec_tr.add_widget(add_download_button(
                chart_tr, "Download Bar Chart"))
            self.vlay.addWidget(sec_tr)

            # Groin Hernia Type Left
            sec_tl = CollapsibleSection("Groin Hernia Type (Left)")
            left_types = df[[
                "GHR_Type_Left_Lateral", "GHR_Type_Left_Medial",
                "GHR_Type_Left_Femoral", "GHR_Type_Left_Obturator"
            ]].fillna(0).astype(int).sum()
            left_types.index = ["Lateral", "Medial", "Femoral", "Obturator"]
            left_types = left_types[left_types > 0]
            chart_tl = make_bar_chart(
                left_types, "Type (Left)", "", "Count"
            )
            chart_tl.setObjectName("chartWrapper")

            sec_tl.add_widget(add_download_button(
                chart_tl, "Download Bar Chart"))
            self.vlay.addWidget(sec_tl)

        elif ty == "PHR":
            sec_st = CollapsibleSection("Type of Stoma")
            chart_st = make_bar_chart(
                df["PHR_Stoma_Type"].value_counts(),
                "Type of Stoma", "", "Count"
            )
            chart_st.setObjectName("chartWrapper")
            sec_st.add_widget(chart_st)
            self.vlay.addWidget(sec_st)

            sec_pr = CollapsibleSection("Previous Repairs Count")
            rep = df["PHR_Prev_Repairs"].dropna().astype(int)
            cnt = rep.value_counts().sort_index()
            cnt = cnt[cnt.index > 0]
            chart_pr = make_bar_chart(
                cnt, "Previous Repairs", "", "Count"
            )
            chart_pr.setObjectName("chartWrapper")

            sec_pr.add_widget(add_download_button(
                chart_pr, "Download Bar Chart"))
            self.vlay.addWidget(sec_pr)

        elif ty == "PVHR":
            sec_pv = CollapsibleSection("Ventral Hernia Subtypes")
            chart_pv = make_bar_chart(
                df["PVHR_Subtype"].value_counts(),
                "PVHR Subtypes", "", "Count"
            )
            chart_pv.setObjectName("chartWrapper")

            sec_pv.add_widget(add_download_button(
                chart_pv, "Download Bar Chart"))
            self.vlay.addWidget(sec_pv)

        elif ty == "IVHR":
            sec_iv = CollapsibleSection("Previous Hernia Repairs")
            rep_iv = df["IVHR_Prev_Repairs"].dropna().astype(int)
            cnt_iv = rep_iv.value_counts().sort_index()
            cnt_iv = cnt_iv[cnt_iv.index > 0]
            chart_iv = make_bar_chart(
                cnt_iv, "Previous Repairs", "", "Count"
            )
            chart_iv.setObjectName("chartWrapper")

            sec_iv.add_widget(add_download_button(
                chart_iv, "Download Bar Chart"))
            self.vlay.addWidget(sec_iv)

        # Summary Statistics
        stats = {
            "Total ops": len(df),
            "Males": df["Gender"].value_counts().get("male", 0),
            "Females": df["Gender"].value_counts().get("female", 0)
        }
        total = stats["Total ops"]
        if total:
            stats["Male %"] = f"{stats['Males']/total*100:.1f}%"
            stats["Female %"] = f"{stats['Females']/total*100:.1f}%"

        # Type-specific summary
        if ty == "GHR":
            right = df["GHR_Side_Right"].fillna(0).astype(int)
            left = df["GHR_Side_Left"].fillna(0).astype(int)
            bilat = ((right == 1) & (left == 1)).sum()
            stats.update({
                "Right %":     f"{(right == 1).sum()/total*100:.1f}%",
                "Left %":      f"{(left == 1).sum()/total*100:.1f}%",
                "Bilateral %": f"{bilat/total*100:.1f}%",
                "Avg Repairs R": f"{df['GHR_Prev_Repairs_Right'].dropna().mean():.1f}",
                "Avg Repairs L": f"{df['GHR_Prev_Repairs_Left'].dropna().mean():.1f}"
            })
        elif ty == "PHR":
            stats["Avg Repairs"] = f"{df['PHR_Prev_Repairs'].dropna().mean():.1f}"
            if not df["PHR_Stoma_Type"].dropna().empty:
                stats["Common Stoma"] = df["PHR_Stoma_Type"].value_counts().idxmax()
        elif ty == "PVHR":
            if not df["PVHR_Subtype"].dropna().empty:
                stats["Common Subtype"] = df["PVHR_Subtype"].value_counts().idxmax()
        elif ty == "IVHR":
            stats["Avg Repairs"] = f"{df['IVHR_Prev_Repairs'].dropna().mean():.1f}"

        tbl_sec = CollapsibleSection("Summary Statistics")
        wrapper = QWidget()
        wrapper_lay = QVBoxLayout(wrapper)
        # left, top=20px, right, bottom
        wrapper_lay.setContentsMargins(0, 10, 0, 0)
        wrapper_lay.addWidget(make_stats_table(stats))
        tbl_sec.add_widget(wrapper)
        self.vlay.addWidget(tbl_sec)
