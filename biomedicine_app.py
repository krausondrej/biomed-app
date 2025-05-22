import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedWidget, QScrollArea, QDateEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
)
from PyQt5 import QtCore
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtGui import QFont

# Globální styl grafů
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams.update({
    'font.family': 'Arial',
    'font.size': 12,
    'axes.titlesize': 14,
    'axes.labelsize': 12,
    'axes.edgecolor': '#0D1B2A',
    'axes.linewidth': 1,
    'grid.color': '#888888',
    'grid.alpha': 0.3,
    'figure.autolayout': True
})

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Biomedical Data Analyzer")
        self.resize(1000, 800)

        # vybraný typ operace a rok
        self.current_op_type = None
        self.selected_year   = None

        # historie navigace
        self.history = []

        # QSS styl
        self.setStyleSheet("""
            QMainWindow { background-color: #fff; }
            QLabel#titleLabel { color: #0D1B2A; font-size: 24px; font-weight: bold; padding: 10px; }
            QLabel { color: #0D1B2A; font-size: 18px; }
            QPushButton { background-color: black; color: #E0E1DD; border: none; border-radius: 5px; padding: 8px; font-size: 16px; }
            QPushButton:hover { background-color: #636564; }
            QScrollArea { border: none; }
        """)

        # Načtení dat operací a převod data na rok
        self.oper_df = pd.read_csv('mock_oper_data.csv', parse_dates=['OperationDate'])
        self.oper_df['OperationDate'] = self.oper_df['OperationDate'].dt.year

        # Ostatní datasety
        self.preop_df     = pd.read_csv('mock_preop_data.csv')
        self.discharge_df = pd.read_csv('mock_discharge_data.csv')
        self.followup_df  = pd.read_csv('mock_followup_data.csv')

        # Zajistíme sloupec LengthOfStay_days
        if 'LengthOfStay_days' not in self.discharge_df.columns:
            for alt in ['LengthOfStay','StayDays','LengthOfStayDays']:
                if alt in self.discharge_df.columns:
                    self.discharge_df.rename(columns={alt:'LengthOfStay_days'}, inplace=True)
                    break
            else:
                raise KeyError("Chybí sloupec LengthOfStay_days nebo jeho alternativy.")

        # Zpět tlačítko
        self.back_btn = QPushButton("Back")
        self.back_btn.clicked.connect(self.go_back)
        self.back_btn.setVisible(False)

        # Stacked widget
        self.stack = QStackedWidget()

        # Vytvoření stránek
        self.page_ops       = self.create_ops_page()
        self.page_year      = self.create_year_page()
        self.page_data      = self.create_data_page()
        self.page_oper      = self.create_oper_page()
        self.page_preop     = self.create_preop_page()
        self.page_discharge = self.create_discharge_page()
        self.page_followup  = self.create_followup_page()

        for p in [self.page_ops, self.page_year, self.page_data,
                  self.page_oper, self.page_preop,
                  self.page_discharge, self.page_followup]:
            self.stack.addWidget(p)
        self.stack.setCurrentWidget(self.page_ops)

        # Hlavní layout
        container   = QWidget()
        main_layout = QVBoxLayout(container)
        top_bar     = QHBoxLayout()
        top_bar.addStretch()
        top_bar.addWidget(self.back_btn)
        main_layout.addLayout(top_bar)
        main_layout.addWidget(self.stack)
        self.setCentralWidget(container)
        
    def add_collapsible_chart(self, layout, label, draw_func):
        """
        Vloží do layoutu tlačítko s popiskem label,
        pod ním widget (container), do kterého se zavolá draw_func(vlay).
        Container je na začátku skrytý a tlačítko ho umí přepínat.
        """
        btn = QPushButton(f"{label}")
        btn.setStyleSheet("""
            QPushButton {
                background-color: black;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #636564;
            }
        """)
        btn.setCheckable(True)
        container = QWidget()
        container.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        container.setVisible(False)
        vlay = QVBoxLayout(container)
        vlay.setContentsMargins(0,0,0,0)
        vlay.setSpacing(10)
        # vykreslíme do containeru
        draw_func(vlay)
        # napojíme toggle
        btn.clicked.connect(lambda _, c=container: c.setVisible(not c.isVisible()))
        # přidáme do hlavního layoutu
        layout.addWidget(btn)
        layout.addWidget(container)

    def go_back(self):
        if self.history:
            prev = self.history.pop()
            self.stack.setCurrentWidget(prev)
        self.back_btn.setVisible(bool(self.history))

    def navigate(self, frm, to):
        self.history.append(frm)
        self.back_btn.setVisible(True)
        self.stack.setCurrentWidget(to)

    # ====== Stránky ======

    def create_ops_page(self):
        w      = QWidget()
        layout = QVBoxLayout(w)
        lbl    = QLabel("SELECT HERNIA OPERATION TYPE")
        lbl.setObjectName("titleLabel")
        lbl.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(lbl)

        ops = [
            ("GHR",  "Groin Hernia Repair"),
            ("PHR",  "Parastomal Hernia Repair"),
            ("IVHR", "Incisional Ventral Hernia Repair"),
            ("PVHR", "Primary Ventral Hernia Repair")
        ]
        for code, text in ops:
            btn = QPushButton(f"{code}: {text}")
            btn.clicked.connect(lambda _, c=code: self.show_year_page(c))
            layout.addWidget(btn)
        return w

    def create_year_page(self):
        w      = QWidget()
        layout = QVBoxLayout(w)
        self.year_label = QLabel("")
        self.year_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.year_label)

        years = ["2021-2025","2021","2022","2023","2024","2025"]
        for yr in years:
            btn = QPushButton(yr)
            btn.clicked.connect(lambda _, y=yr: self.show_data_page(y))
            layout.addWidget(btn)
        return w

    def create_data_page(self):
        w      = QWidget()
        layout = QVBoxLayout(w)
        self.data_label = QLabel("")
        self.data_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.data_label)

        cats = [
            "Preoperative data",
            "Operative data",
            "Postoperative data (hospitalization)",
            "Long-term postoperative data"
        ]
        for cat in cats:
            btn = QPushButton(cat)
            btn.clicked.connect(lambda _, c=cat: self.show_category_page(c))
            layout.addWidget(btn)
        return w

    def show_year_page(self, op_type):
        self.current_op_type = op_type
        self.year_label.setText(f"Selected Type: {op_type}")
        self.navigate(self.page_ops, self.page_year)

    def show_data_page(self, year):
        self.selected_year = year
        self.data_label.setText(f"Year: {year}")

        # aktualizovat rozsah QDateEdit na oper page
        if year != "2021-2025":
            try:
                yr = int(year)
                self.date_from.setDate(QtCore.QDate(yr,1,1))
                self.date_to.setDate(QtCore.QDate(yr,12,31))
            except ValueError:
                pass
        else:
            min_y = int(self.oper_df['OperationDate'].min())
            max_y = int(self.oper_df['OperationDate'].max())
            self.date_from.setDate(QtCore.QDate(min_y,1,1))
            self.date_to.setDate(QtCore.QDate(max_y,12,31))

        self.navigate(self.page_year, self.page_data)

    def show_category_page(self, category):
        mapping = {
            "Operative data":                      self.page_oper,
            "Preoperative data":                   self.page_preop,
            "Postoperative data (hospitalization)": self.page_discharge,
            "Long-term postoperative data":        self.page_followup
        }
        target = mapping.get(category)
        if target:
            if target is self.page_oper:
                self.update_oper_view()
            if target is self.page_preop:
                self.update_preop_view()
            if target is self.page_discharge:
                self.update_discharge_view()
            if target is self.page_followup:
                self.update_followup_view()
            self.navigate(self.page_data, target)
            
    # ===== Helper pro grafy =====

    def add_bar_chart(self, layout, data, title, xlabel, ylabel,
                      figsize=(8,5), dpi=100, min_h=600):
        fig = Figure(figsize=figsize, dpi=dpi, facecolor='none')
        ax  = fig.add_subplot(111, facecolor='none')
        data.plot(kind='bar', ax=ax)
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)

        # zvýraznit osu
        ax.spines['left'].set_linewidth(1.2)
        ax.spines['left'].set_color('#0D1B2A')
        ax.yaxis.set_ticks_position('left')

        # navýšíme limit osy Y o 10 %, aby štítky nevycházely ven
        max_h = data.max()
        ax.set_ylim(0, max_h * 1.1)

        # přidat text nad sloupce s malým odsazením (2 % max výšky)
        for rect in ax.patches:
            h = rect.get_height()
            ax.text(
                rect.get_x() + rect.get_width()/2,
                h + max_h * 0.02,
                f"{int(h)}",
                ha='center', va='bottom'
            )

        fig.tight_layout()
        canvas = FigureCanvas(fig)
        canvas.setMinimumHeight(min_h)
        layout.addWidget(canvas)

    def add_histogram(self, layout, data, bins, title, xlabel, ylabel,
                      figsize=(8,5), dpi=100, min_h=600):
        fig = Figure(figsize=figsize, dpi=dpi, facecolor='none')
        ax  = fig.add_subplot(111, facecolor='none')
        counts, edges, patches = ax.hist(data.dropna(), bins=bins)
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)

        # zvýraznit osu
        ax.spines['left'].set_linewidth(1.2)
        ax.spines['left'].set_color('#0D1B2A')
        ax.yaxis.set_ticks_position('left')

        # xticky na hranice, xticklabels apod.
        ax.set_xticks(edges)
        ax.set_xticklabels([f"{int(e)}" for e in edges], rotation=45)

        # navýšíme limit osy Y o 40 %
        max_h = counts.max()
        ax.set_ylim(0, max_h * 1.4)

        # popisky nad sloupci
        for rect, cnt in zip(patches, counts):
            ax.text(
                rect.get_x() + rect.get_width()/2,
                cnt + max_h * 0.02,
                f"{int(cnt)}",
                ha='center', va='bottom'
            )

        fig.tight_layout()
        canvas = FigureCanvas(fig)
        canvas.setMinimumHeight(min_h)
        layout.addWidget(canvas)
        
    def add_stats_table(self, layout, stats):
        table = QTableWidget(len(stats), 2)
        table.setHorizontalHeaderLabels(['Metric','Value'])
        for row, (k, v) in enumerate(stats.items()):
            item_k = QTableWidgetItem(k)
            item_v = QTableWidgetItem(str(v))
            item_v.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            table.setItem(row, 0, item_k)
            table.setItem(row, 1, item_v)

        table.verticalHeader().setVisible(False)
        table.setShowGrid(False)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionMode(QAbstractItemView.NoSelection)
        table.setAlternatingRowColors(True)
        table.setStyleSheet("""
            QTableWidget {
                background-color: transparent;
                alternate-background-color: rgba(255,255,255,0.1);
            }
            QHeaderView::section {
                background-color: black;
                color: #E0E1DD;
                padding: 4px;
                font-weight: bold;
            }
        """)
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        font = QFont()
        font.setBold(True)
        header.setFont(font)

        # nastavíme minimální výšku: záhlaví + všechny řádky
        row_h       = table.verticalHeader().defaultSectionSize()
        header_h    = header.height() or 30
        min_height  = header_h + table.rowCount() * row_h + 2
        table.setMinimumHeight(min_height)

        layout.addWidget(table)

    # ===== Operativní data =====

    def create_oper_page(self):
        w      = QWidget()
        layout = QVBoxLayout(w)

        title = QLabel("Operative Data – Visualization and Table")
        title.setObjectName("titleLabel")
        title.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title)
        
        self.oper_header = QLabel()
        self.oper_header.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.oper_header)

        # zobrazíme vybraný typ
        self.oper_type_label = QLabel()
        self.oper_type_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.oper_type_label)

        # skrytý rozsah dat
        self.date_from = QDateEdit(calendarPopup=True)
        self.date_from.dateChanged.connect(self.update_oper_view)
        self.date_to   = QDateEdit(calendarPopup=True)
        self.date_to.dateChanged.connect(self.update_oper_view)

        # scroll area pro grafy/tabulku
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        self.oper_layout = QVBoxLayout(container)
        self.oper_layout.setSpacing(20)
        scroll.setStyleSheet("background: transparent;")
        container.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        scroll.setWidget(container)
        layout.addWidget(scroll)

        return w

    def update_oper_view(self):
        # 1) Aktualizovat header s typem a rokem
        ty = self.current_op_type or "All types"
        yr = self.selected_year    or "All years"
        self.oper_header.setText(f"Type: {ty} ┃ Year: {yr}")

        # 2) Vyčistit existující widgety
        for i in reversed(range(self.oper_layout.count())):
            w = self.oper_layout.itemAt(i).widget()
            if w:
                w.setParent(None)

        # 3) Načíst a filtrovat DataFrame podle roku, typu a rozsahu
        df = self.oper_df.copy()
        if self.selected_year and self.selected_year != "2021-2025":
            try:
                yr_int = int(self.selected_year)
                df = df[df['OperationDate'] == yr_int]
            except ValueError:
                pass
        if self.current_op_type:
            df = df[df['OperationType'] == self.current_op_type]
        start = self.date_from.date().year()
        end   = self.date_to.date().year()
        df = df[(df['OperationDate'] >= start) & (df['OperationDate'] <= end)]

        # 4) Pokud není co kreslit, zobrazíme hlášku
        if df.empty:
            lbl = QLabel("No data available for the selected type/year.")
            lbl.setAlignment(QtCore.Qt.AlignCenter)
            self.oper_layout.addWidget(lbl)
            return

        # 5) Rozbalitelné grafy
        # 5a) Indication for Surgery
        self.add_collapsible_chart(
            self.oper_layout,
            'Indication for Surgery',
            lambda lay: self.add_bar_chart(
                lay,
                df['Indication'].value_counts(),
                'Indication for Surgery', 'Indication', 'Count'
            )
        )

        # 5b) Grafy specifické pro jednotlivé typy
        if self.current_op_type == 'GHR':
            self.add_collapsible_chart(
                self.oper_layout,
                'Side of the Hernia',
                lambda lay: self.add_bar_chart(
                    lay,
                    df['Side'].fillna('Unknown').value_counts(),
                    'Side of the Hernia', 'Side', 'Count'
                )
            )
            self.add_collapsible_chart(
                self.oper_layout,
                'Previous Repairs (Right)',
                lambda lay: self.add_bar_chart(
                    lay,
                    df['PrevRepairsRight'].fillna(0).astype(int).value_counts().sort_index(),
                    'Previous Repairs (Right)', 'Number of Repairs', 'Count'
                )
            )
            self.add_collapsible_chart(
                self.oper_layout,
                'Previous Repairs (Left)',
                lambda lay: self.add_bar_chart(
                    lay,
                    df['PrevRepairsLeft'].fillna(0).astype(int).value_counts().sort_index(),
                    'Previous Repairs (Left)', 'Number of Repairs', 'Count'
                )
            )
            self.add_collapsible_chart(
                self.oper_layout,
                'Groin Hernia Type (Right)',
                lambda lay: self.add_bar_chart(
                    lay,
                    df['HerniaTypeRight'].fillna('Unknown').value_counts(),
                    'Groin Hernia Type (Right)', 'Hernia Type', 'Count'
                )
            )
            self.add_collapsible_chart(
                self.oper_layout,
                'Groin Hernia Type (Left)',
                lambda lay: self.add_bar_chart(
                    lay,
                    df['HerniaTypeLeft'].fillna('Unknown').value_counts(),
                    'Groin Hernia Type (Left)', 'Hernia Type', 'Count'
                )
            )

        elif self.current_op_type == 'PHR':
            self.add_collapsible_chart(
                self.oper_layout,
                'Type of Stoma',
                lambda lay: self.add_bar_chart(
                    lay,
                    df['StomaType'].fillna('Unknown').value_counts(),
                    'Type of Stoma', 'Stoma Type', 'Count'
                )
            )
            total_repairs = (df['PrevRepairsRight'].fillna(0) + df['PrevRepairsLeft'].fillna(0)).astype(int)
            self.add_collapsible_chart(
                self.oper_layout,
                'Number of Previous Repairs',
                lambda lay: self.add_bar_chart(
                    lay,
                    total_repairs.value_counts().sort_index(),
                    'Number of Previous Repairs', 'Number of Repairs', 'Count'
                )
            )

        elif self.current_op_type == 'PVHR':
            self.add_collapsible_chart(
                self.oper_layout,
                'PVHR Type Specification',
                lambda lay: self.add_bar_chart(
                    lay,
                    df['PVHR_Type'].fillna('Unknown').value_counts(),
                    'PVHR Type Specification', 'PVHR Type', 'Count'
                )
            )

        elif self.current_op_type == 'IVHR':
            total_repairs = (df['PrevRepairsRight'].fillna(0) + df['PrevRepairsLeft'].fillna(0)).astype(int)
            self.add_collapsible_chart(
                self.oper_layout,
                'Number of Previous Hernia Repairs',
                lambda lay: self.add_bar_chart(
                    lay,
                    total_repairs.value_counts().sort_index(),
                    'Number of Previous Hernia Repairs', 'Number of Repairs', 'Count'
                )
            )

        # 6) Přehledová tabulka se základními statistikami
        stats = {
            'Total ops':            len(df),
            'Avg duration (h)':     f"{df['OperationDuration_h'].mean():.2f}",
            'Min duration (h)':     f"{df['OperationDuration_h'].min():.2f}",
            'Max duration (h)':     f"{df['OperationDuration_h'].max():.2f}"
        }
        self.add_stats_table(self.oper_layout, stats)


    # ===== Preop, Discharge, Followup =====

    def create_preop_page(self):
        w      = QWidget()
        layout = QVBoxLayout(w)
        title  = QLabel("Preoperative Data – Visualization")
        title.setObjectName("titleLabel")
        title.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title)
        
        self.preop_header = QLabel()
        self.preop_header.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.preop_header)
        # Scroll area a kontejner, do kterého budeme vkládat grafy
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        self.preop_layout = QVBoxLayout(container)
        self.preop_layout.setSpacing(20)
        scroll.setStyleSheet("background: transparent;")
        container.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        scroll.setWidget(container)
        layout.addWidget(scroll)

        return w

    def update_preop_view(self):
        # Aktualizace headeru s vybraným typem a rokem
        ty = self.current_op_type or "All types"
        yr = self.selected_year or "All years"
        self.preop_header.setText(f"Type: {ty} ┃ Year: {yr}")

        # 1) Vyčistit stávající widgety
        for i in reversed(range(self.preop_layout.count())):
            w = self.preop_layout.itemAt(i).widget()
            if w:
                w.setParent(None)

        # 2) Filtr na rok
        df = self.preop_df.copy()
        if self.selected_year and self.selected_year != "2021-2025":
            try:
                yr_int = int(self.selected_year)
                df = df[df['Year'] == yr_int]
            except ValueError:
                pass

        # 3) Pokud je df prázdné, zobrazíme informaci
        if df.empty:
            lbl = QLabel("No data for selected year.")
            lbl.setAlignment(QtCore.Qt.AlignCenter)
            self.preop_layout.addWidget(lbl)
            return

        # 4) Přidání rozbalitelných grafů
        self.add_collapsible_chart(
            self.preop_layout,
            'Number of Men and Women',
            lambda lay: self.add_bar_chart(
                lay,
                df['Gender'].value_counts(),
                'Number of Men and Women', 'Gender', 'Count'
            )
        )
        self.add_collapsible_chart(
            self.preop_layout,
            'Age Distribution',
            lambda lay: self.add_histogram(
                lay,
                df['Age'], bins=10,
                title='Age Distribution', xlabel='Age', ylabel='Count'
            )
        )
        self.add_collapsible_chart(
            self.preop_layout,
            'BMI Distribution',
            lambda lay: self.add_histogram(
                lay,
                df['BMI'], bins=10,
                title='BMI Distribution', xlabel='BMI', ylabel='Count'
            )
        )
        self.add_collapsible_chart(
            self.preop_layout,
            'Comorbidities Before Surgery',
            lambda lay: self.add_bar_chart(
                lay,
                df[['Diabetes','Hypertension','Heart_Disease']].sum(),
                'Prevalence of Comorbidities', 'Comorbidity', 'Number of Patients'
            )
        )
        self.add_collapsible_chart(
            self.preop_layout,
            'Pre-operative Pain Score',
            lambda lay: self.add_histogram(
                lay,
                df['Preop_Pain_Score'], bins=10,
                title='Pre-operative Pain Score Distribution',
                xlabel='Pain Score', ylabel='Count'
            )
        )
        self.add_collapsible_chart(
            self.preop_layout,
            'Pre-operative Restrictions Score',
            lambda lay: self.add_histogram(
                lay,
                df['Preop_Restrictions_Score'], bins=10,
                title='Pre-operative Restrictions Score Distribution',
                xlabel='Restrictions Score', ylabel='Count'
            )
        )
        self.add_collapsible_chart(
            self.preop_layout,
            'Aesthetic Discomfort Score',
            lambda lay: self.add_histogram(
                lay,
                df['Aesthetic_Discomfort_Score'], bins=10,
                title='Aesthetic Discomfort Score Distribution',
                xlabel='Discomfort Score', ylabel='Count'
            )
        )

        # 5) Přehledová tabulka se základními statistikami
        stats = {
            'Total patients': len(df),
            'Males': df['Gender'].value_counts().get('Male', 0),
            'Females': df['Gender'].value_counts().get('Female', 0),
            'Mean age': f"{df['Age'].mean():.1f}",
            'Median age': f"{df['Age'].median():.1f}",
            'Mean BMI': f"{df['BMI'].mean():.1f}"
        }
        self.add_stats_table(self.preop_layout, stats)


    def create_discharge_page(self):
        w      = QWidget()
        layout = QVBoxLayout(w)
        title  = QLabel("Intrahospital Complications")
        title.setObjectName("titleLabel")
        title.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title)
        
        self.discharge_header = QLabel()
        self.discharge_header.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.discharge_header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        self.discharge_layout = QVBoxLayout(container)
        self.discharge_layout.setSpacing(20)
        scroll.setStyleSheet("background: transparent;")
        container.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        scroll.setWidget(container)
        layout.addWidget(scroll)

        return w

    def update_discharge_view(self):
        # 1) Aktualizovat header s typem a rokem
        ty = self.current_op_type or "All types"
        yr = self.selected_year    or "All years"
        self.discharge_header.setText(f"Type: {ty} ┃ Year: {yr}")

        # 2) Vyčistit existující widgety
        for i in reversed(range(self.discharge_layout.count())):
            w = self.discharge_layout.itemAt(i).widget()
            if w:
                w.setParent(None)

        # 3) Zkopírovat a filtrovat DataFrame podle roku
        df = self.discharge_df.copy()
        if self.selected_year and self.selected_year != "2021-2025":
            try:
                yr_int = int(self.selected_year)
                df = df[df['Year'] == yr_int]
            except ValueError:
                pass

        # 4) Pokud po filtraci není žádný řádek, zobrazíme zprávu
        if df.empty:
            lbl = QLabel("No discharge data for selected year.")
            lbl.setAlignment(QtCore.Qt.AlignCenter)
            self.discharge_layout.addWidget(lbl)
            return

        # 5) Vypočítat data pro grafy
        occ_counts = df['ComplicationOccurrence'] \
                        .map({0: 'No', 1: 'Yes'}) \
                        .value_counts()
        type_counts = df['ComplicationType'] \
                          .fillna('None') \
                          .value_counts()

        # 6) Přidat rozbalitelné grafy
        self.add_collapsible_chart(
            self.discharge_layout,
            'Occurrence of Intrahospital Complications',
            lambda lay: self.add_bar_chart(
                lay,
                occ_counts,
                'Occurrence of Intrahospital Complications',
                'Occurrence',
                'Count'
            )
        )
        self.add_collapsible_chart(
            self.discharge_layout,
            'Type of Intrahospital Complications',
            lambda lay: self.add_bar_chart(
                lay,
                type_counts,
                'Type of Intrahospital Complications',
                'Complication Type',
                'Count'
            )
        )

    def create_followup_page(self):
        w      = QWidget()
        layout = QVBoxLayout(w)
        title  = QLabel("Follow-Up Complications")
        title.setObjectName("titleLabel")
        title.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title)

        self.followup_header = QLabel()
        self.followup_header.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.followup_header)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        self.followup_layout = QVBoxLayout(container)
        self.followup_layout.setSpacing(20)
        scroll.setStyleSheet("background: transparent;")
        container.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        scroll.setWidget(container)
        layout.addWidget(scroll)

        return w

    def update_followup_view(self):
        # 1) Aktualizovat header s typem a rokem
        ty = self.current_op_type or "All types"
        yr = self.selected_year    or "All years"
        self.followup_header.setText(f"Type: {ty} ┃ Year: {yr}")

        # 2) Vyčistit existující widgety
        for i in reversed(range(self.followup_layout.count())):
            w = self.followup_layout.itemAt(i).widget()
            if w:
                w.setParent(None)

        # 3) Zkopírovat a filtrovat DataFrame podle roku
        df = self.followup_df.copy()
        if self.selected_year and self.selected_year != "2021-2025":
            try:
                yr_int = int(self.selected_year)
                df = df[df['Year'] == yr_int]
            except ValueError:
                pass

        # 4) Pokud po filtraci není žádný řádek, zobrazíme zprávu
        if df.empty:
            lbl = QLabel("No follow-up data for selected year.")
            lbl.setAlignment(QtCore.Qt.AlignCenter)
            self.followup_layout.addWidget(lbl)
            return

        # 5) Připravit data pro grafy
        occ = df['FollowUpOccurrence'] \
                  .map({0: 'No', 1: 'Yes'}) \
                  .value_counts()
        types = df['FollowUpType'] \
                   .fillna('None') \
                   .value_counts()

        # 6) Přidat rozbalitelné grafy
        self.add_collapsible_chart(
            self.followup_layout,
            'Occurrence of Follow-Up Complications',
            lambda lay: self.add_bar_chart(
                lay,
                occ,
                'Occurrence of Follow-Up Complications',
                'Occurrence',
                'Count'
            )
        )
        self.add_collapsible_chart(
            self.followup_layout,
            'Type of Follow-Up Complications',
            lambda lay: self.add_bar_chart(
                lay,
                types,
                'Type of Follow-Up Complications',
                'Complication Type',
                'Count'
            )
        )

if __name__ == "__main__":
    app    = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())