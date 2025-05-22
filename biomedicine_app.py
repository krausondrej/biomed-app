import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedWidget, QScrollArea, QDateEdit,
    QTableWidget, QTableWidgetItem
)
from PyQt5 import QtCore
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

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
            QPushButton { background-color: #415A77; color: #E0E1DD; border: none; border-radius: 5px; padding: 8px; font-size: 16px; }
            QPushButton:hover { background-color: #1B263B; }
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
            self.navigate(self.page_data, target)

    # ===== Helper pro grafy =====

    def add_bar_chart(self, layout, data, title, xlabel, ylabel, figsize=(8,5), dpi=100, min_h=400):
        fig = Figure(figsize=figsize, dpi=dpi)
        ax  = fig.add_subplot(111)
        data.plot(kind='bar', ax=ax)
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        canvas = FigureCanvas(fig)
        canvas.setMinimumHeight(min_h)
        layout.addWidget(canvas)

    def add_histogram(self, layout, data, bins, title, xlabel, ylabel, figsize=(8,5), dpi=100, min_h=400):
        fig = Figure(figsize=figsize, dpi=dpi)
        ax  = fig.add_subplot(111)
        ax.hist(data.dropna(), bins=bins)
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        canvas = FigureCanvas(fig)
        canvas.setMinimumHeight(min_h)
        layout.addWidget(canvas)

    # ===== Operativní data =====

    def create_oper_page(self):
        w      = QWidget()
        layout = QVBoxLayout(w)

        title = QLabel("Operative Data – Visualization and Table")
        title.setObjectName("titleLabel")
        title.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title)

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
        scroll.setWidget(container)
        layout.addWidget(scroll)

        return w

    def update_oper_view(self):
        # vyčistit layout
        for i in reversed(range(self.oper_layout.count())):
            w = self.oper_layout.itemAt(i).widget()
            if w:
                w.setParent(None)

        df = self.oper_df.copy()

        # filtr podle roku
        if self.selected_year and self.selected_year != "2021-2025":
            try:
                y = int(self.selected_year)
                df = df[df['OperationDate'] == y]
            except ValueError:
                pass

        # filtr podle typu
        if self.current_op_type:
            df = df[df['OperationType'] == self.current_op_type]
            self.oper_type_label.setText(f"Type: {self.current_op_type}")
        else:
            self.oper_type_label.setText("Type: All")

        # filtr podle rozsahu z QDateEdit
        start = self.date_from.date().year()
        end   = self.date_to.date().year()
        df = df[(df['OperationDate'] >= start) & (df['OperationDate'] <= end)]

        # pokud po filtrech není nic, zobrazíme hlášku
        if df.empty:
            msg = QLabel("No data available for the selected type/year.")
            msg.setAlignment(QtCore.Qt.AlignCenter)
            self.oper_layout.addWidget(msg)
            return

        # vykreslení grafů a tabulky
        self.add_bar_chart(
            self.oper_layout,
            df['Indication'].value_counts(),
            'Indication Counts', 'Indication', 'Count'
        )
        self.add_bar_chart(
            self.oper_layout,
            df['Side'].fillna('Unknown').value_counts(),
            'Side Distribution', 'Side', 'Count'
        )
        self.add_bar_chart(
            self.oper_layout,
            df['OperationType'].value_counts(),
            'Operation Type Distribution', 'Operation Type', 'Count'
        )
        self.add_histogram(
            self.oper_layout,
            df['OperationDuration_h'], bins=10,
            title='Operation Duration Distribution',
            xlabel='Duration (h)', ylabel='Count'
        )

        stats = {
            'Total operations':       len(df),
            'Average duration (h)':   f"{df['OperationDuration_h'].mean():.2f}",
            'Min duration (h)':       f"{df['OperationDuration_h'].min():.2f}",
            'Max duration (h)':       f"{df['OperationDuration_h'].max():.2f}"
        }
        table = QTableWidget(len(stats), 2)
        table.setHorizontalHeaderLabels(['Metric', 'Value'])
        for row, (k, v) in enumerate(stats.items()):
            table.setItem(row, 0, QTableWidgetItem(k))
            table.setItem(row, 1, QTableWidgetItem(str(v)))
        table.resizeColumnsToContents()
        self.oper_layout.addWidget(table)

    # ===== Preop, Discharge, Followup =====

    def create_preop_page(self):
        w      = QWidget()
        layout = QVBoxLayout(w)
        title  = QLabel("Preoperative Data – Visualization")
        title.setObjectName("titleLabel")
        title.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title)
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        cont   = QWidget(); vbox = QVBoxLayout(cont); vbox.setSpacing(20)
        self.add_bar_chart(vbox, self.preop_df['Gender'].value_counts(),
                           'Number of Males and Females', 'Gender', 'Count')
        self.add_histogram(vbox, self.preop_df['Age'], bins=10,
                           title='Age Distribution', xlabel='Age', ylabel='Count')
        self.add_histogram(vbox, self.preop_df['BMI'], bins=10,
                           title='BMI Distribution', xlabel='BMI', ylabel='Count')
        com = ['Diabetes','Hypertension','Heart_Disease']
        self.add_bar_chart(vbox, self.preop_df[com].sum(),
                           'Prevalence of Comorbidities', 'Comorbidity', 'Number of Patients')
        scroll.setWidget(cont); layout.addWidget(scroll)
        return w

    def create_discharge_page(self):
        w      = QWidget()
        layout = QVBoxLayout(w)
        title  = QLabel("Postoperative Data (Hospital Stay)")
        title.setObjectName("titleLabel")
        title.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title)
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        cont   = QWidget(); vbox = QVBoxLayout(cont); vbox.setSpacing(20)
        self.add_histogram(vbox, self.discharge_df['LengthOfStay_days'], bins=10,
                           title='Length of Stay Distribution', xlabel='Days', ylabel='Count')
        scroll.setWidget(cont); layout.addWidget(scroll)
        return w

    def create_followup_page(self):
        w      = QWidget()
        layout = QVBoxLayout(w)
        title  = QLabel("Long-Term Postoperative Data")
        title.setObjectName("titleLabel")
        title.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title)
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        cont   = QWidget(); vbox = QVBoxLayout(cont); vbox.setSpacing(20)
        self.add_bar_chart(vbox, self.followup_df['Recurrence'].value_counts(),
                           'Recurrence Rates', 'Recurrence', 'Count')
        scroll.setWidget(cont); layout.addWidget(scroll)
        return w

if __name__ == "__main__":
    app    = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
