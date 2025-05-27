import pandas as pd
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QHBoxLayout, QComboBox
from PyQt5 import QtCore
from ui_helpers import CollapsibleSection
from chart_utils import make_bar_chart
from table_utils import make_stats_table

class OperativePage(QWidget):
    def __init__(self, main_win, df):
        super().__init__()
        self.main = main_win
        self.df   = df
        self.selected_gender = "All"
        self._build_ui()

    def _build_ui(self):
        lay = QVBoxLayout(self)

        lbl = QLabel("Operative Data – Visualization and Table")
        lbl.setObjectName("titleLabel")
        lbl.setAlignment(QtCore.Qt.AlignCenter)
        lay.addWidget(lbl)

        self.header = QLabel("")
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

        # ScrollArea with transparent background and black scrollbar
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            /* Container transparent */
            QScrollArea { background: transparent; border: none; }
            /* Track */
            QScrollBar:vertical { background: transparent; width: 12px; margin: 0; }
            /* Handle */
            QScrollBar::handle:vertical { background: #000000; min-height: 20px; border-radius: 6px; }
            /* Hide arrows */
            QScrollBar::sub-line:vertical, QScrollBar::add-line:vertical { height: 0; }
            /* Empty areas */
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
        self.selected_gender = gender_text
        self.update_view()

    def update_view(self):
        # clear previous widgets
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

        # update header
        self.header.setText(f"Operation: {ty}   |   Year: {yr_sel}   |   Number of Result: {len(df)}")

        if self.selected_gender.lower() in ["male", "female"]:
            df = df[df["Gender"] == self.selected_gender.lower()]
            
        # 1) Indication for Surgery
        sec1 = CollapsibleSection("Indication for Surgery")
        sec1.add_widget(make_bar_chart(
            df["Indication"].value_counts(),
            "Indication for Surgery", "", "Number of the patients"
        ))
        self.vlay.addWidget(sec1)

        # 2) Type-specific sections
        if ty == "GHR":
            # 1a) Side of the Hernia – combined
            right = df["GHR_Side_Right"].fillna(0).astype(int)
            left  = df["GHR_Side_Left"].fillna(0).astype(int)

            def side_category(r, l):
                if r == 1 and l == 1:
                    return "Bilateral"
                elif r == 1:
                    return "Right"
                elif l == 1:
                    return "Left"
                else:
                    return None

            side = [side_category(r, l) for r, l in zip(right, left)]
            side_series = pd.Series(side).dropna().astype(str)

            side_counts = side_series.value_counts().reindex(
                ["Right", "Left", "Bilateral"], fill_value=0
            )

            sec_side = CollapsibleSection("Side of the Hernia")
            sec_side.add_widget(make_bar_chart(
                side_counts,
                title="Side of the groin hernia",
                xlabel="Side of the hernia",
                ylabel="Number of the patients"
            ))
            self.vlay.addWidget(sec_side)

            # 2a) Previous Repairs (Right)
            sec4 = CollapsibleSection("Previous Repairs (Right)")
            rep_right = df["GHR_Prev_Repairs_Right"].fillna(0).astype(int)
            counts_right = rep_right.value_counts().sort_index()
            counts_right = counts_right[counts_right.index != 0]
            sec4.add_widget(make_bar_chart(
                counts_right,
                "Previous Repairs (Right)",
                "Number of Repairs",
                "Count"
            ))
            self.vlay.addWidget(sec4)

            # 3a) Previous Repairs (Left)
            sec5 = CollapsibleSection("Previous Repairs (Left)")
            rep_left = df["GHR_Prev_Repairs_Left"].fillna(0).astype(int)
            counts_left = rep_left.value_counts().sort_index()
            counts_left = counts_left[counts_left.index != 0]
            sec5.add_widget(make_bar_chart(
                counts_left,
                "Previous Repairs (Left)",
                "Number of Repairs",
                "Count"
            ))
            self.vlay.addWidget(sec5)


            # 4a) Groin Hernia Type – Right
            sec6 = CollapsibleSection("Groin Hernia Type (Right)")

            counts = df[[
                "GHR_Type_Right_Lateral",
                "GHR_Type_Right_Medial",
                "GHR_Type_Right_Femoral",
                "GHR_Type_Right_Obturator"
            ]].sum()

            counts.index = ["Lateral", "Medial", "Femoral", "Obturator"]

            counts = counts[counts > 0]

            sec6.add_widget(make_bar_chart(
                counts,
                title="Groin Hernia Type (Right)",
                xlabel="Type",
                ylabel="Count"
            ))
            self.vlay.addWidget(sec6)

            # 5a) Groin Hernia Type (Left)
            sec7 = CollapsibleSection("Groin Hernia Type (Left)")

            left_types = df[[
                "GHR_Type_Left_Lateral",
                "GHR_Type_Left_Medial",
                "GHR_Type_Left_Femoral",
                "GHR_Type_Left_Obturator"
            ]].fillna(0).astype(int)

            counts_left = left_types.sum()

            counts_left.index = ["Lateral", "Medial", "Femoral", "Obturator"]

            counts_left = counts_left[counts_left > 0]

            sec7.add_widget(make_bar_chart(
                counts_left,
                title="Groin Hernia Type (Left)",
                xlabel="Type",
                ylabel="Count"
            ))
            self.vlay.addWidget(sec7)


        elif ty == "PHR":
            # 1b) Type of Stoma
            sec2 = CollapsibleSection("Type of Stoma")
            sec2.add_widget(make_bar_chart(
                df["PHR_Stoma_Type"].value_counts(),
                "Type of Stoma", "", "Number of the patients"
            ))
            self.vlay.addWidget(sec2)
            
            # 2b) Type of Stoma
            sec3 = CollapsibleSection("Number of Previous Repairs")

            rep = df["PHR_Prev_Repairs"].dropna().astype(int)
            counts = rep.value_counts().sort_index()

            counts = counts[counts.index > 0]

            sec3.add_widget(make_bar_chart(
                counts,
                title="Number of Previous Parastomal Hernia Repairs",
                xlabel="Number of previous Repairs",
                ylabel="Number of patients"
            ))
            self.vlay.addWidget(sec3)

        elif ty == "PVHR":
            # 1c) PVHR Type Specification
            sec2 = CollapsibleSection("PVHR Type Specification")
            sec2.add_widget(make_bar_chart(
                df["PVHR_Subtype"].value_counts(),
                "Specification of the primary ventral hernia type", "", "Number of the patients"
            ))
            self.vlay.addWidget(sec2)

        elif ty == "IVHR":
            # 1d) Number of Previous Hernia Repairs
            sec2 = CollapsibleSection("Number of Previous Hernia Repairs")

            rep = df["IVHR_Prev_Repairs"].dropna().astype(int)
            counts = rep.value_counts().sort_index()

            counts = counts[counts.index > 0]

            sec2.add_widget(make_bar_chart(
                counts,
                title="Number of Previous Hernia Repairs",
                xlabel="Number of previous Repairs",
                ylabel="Number of the patients"
            ))
            self.vlay.addWidget(sec2)

        # 3) Summary Statistics
        stats = {
            "Total ops": len(df),
            # Demografie
            "Males": df["Gender"].value_counts().get("male", 0),
            "Females": df["Gender"].value_counts().get("female", 0),
        }
        total = len(df)
        if total:
            stats["Male %"]   = f"{stats['Males']/total*100:.1f}%"
            stats["Female %"] = f"{stats['Females']/total*100:.1f}%"

        # Typově specifické doplňky
        if ty == "GHR":
            # Strany kýly
            right = df["GHR_Side_Right"].fillna(0).astype(int)
            left  = df["GHR_Side_Left"].fillna(0).astype(int)
            bilat = ((right==1)&(left==1)).sum()
            stats.update({
                "Right %":     f"{(right==1).sum()/total*100:.1f}%",
                "Left %":      f"{(left==1).sum()/total*100:.1f}%",
                "Bilateral %": f"{bilat/total*100:.1f}%",
                # Průměrný počet předchozích oprav
                "Avg Prev Repairs (R)": f"{df['GHR_Prev_Repairs_Right'].dropna().mean():.1f}",
                "Avg Prev Repairs (L)": f"{df['GHR_Prev_Repairs_Left'].dropna().mean():.1f}",
            })

        elif ty == "PHR":
            # Průměrný počet předchozích oprav
            stats["Avg Prev Repairs"] = f"{df['PHR_Prev_Repairs'].dropna().mean():.1f}"
            # Nejčastější typ stoma
            if not df["PHR_Stoma_Type"].dropna().empty:
                most = df["PHR_Stoma_Type"].value_counts().idxmax()
                stats["Most Common Stoma"] = most

        elif ty == "PVHR":
            # Nejčastější podtyp
            if not df["PVHR_Subtype"].dropna().empty:
                stats["Most Common Subtype"] = df["PVHR_Subtype"].value_counts().idxmax()

        elif ty == "IVHR":
            stats["Avg Prev Repairs"] = f"{df['IVHR_Prev_Repairs'].dropna().mean():.1f}"

        # Vložení do GUI
        tbl_sec = CollapsibleSection("Summary Statistics")
        wrapper = QWidget()
        wrapper_lay = QVBoxLayout(wrapper)
        wrapper_lay.setContentsMargins(0, 10, 0, 0)
        wrapper_lay.addWidget(make_stats_table(stats))
        tbl_sec.add_widget(wrapper)
        self.vlay.addWidget(tbl_sec)
