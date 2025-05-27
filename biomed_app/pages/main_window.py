# pages/main_window.py
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QStackedWidget
)
from PyQt5 import QtCore
from data_loader import (
    load_oper_data, load_preop_data,
    load_discharge_data, load_followup_data
)
from pages.ops_page       import OpsPage
from pages.year_page      import YearPage
from pages.data_page      import DataPage
from pages.operative_page import OperativePage
from pages.preop_page     import PreopPage
from pages.discharge_page import DischargePage
from pages.followup_page  import FollowupPage

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Biomedical Data Analyzer")
        self.resize(1000,800)

        # load data
        self.oper_df      = load_oper_data()
        self.preop_df     = load_preop_data()
        self.discharge_df = load_discharge_data()
        self.followup_df  = load_followup_data()

        # user selections
        self.current_op_type = None
        self.selected_year   = None

        # back button
        self.back_btn = QPushButton("Back")
        self.back_btn.clicked.connect(self.go_back)
        self.back_btn.setVisible(False)

        # instantiate pages
        self.ops_page       = OpsPage(self)
        self.year_page      = YearPage(self)
        self.data_page      = DataPage(self)
        self.oper_page      = OperativePage(self, self.oper_df)
        self.preop_page     = PreopPage(self, self.preop_df)
        self.discharge_page = DischargePage(self, self.discharge_df)
        self.followup_page  = FollowupPage(self, self.followup_df)

        # stack
        self.stack = QStackedWidget()
        for p in [
            self.ops_page, self.year_page, self.data_page,
            self.oper_page, self.preop_page,
            self.discharge_page, self.followup_page
        ]:
            self.stack.addWidget(p)

        # layout
        container = QWidget()
        main_lay = QVBoxLayout(container)
        top_bar = QHBoxLayout()
        top_bar.addStretch()
        top_bar.addWidget(self.back_btn)
        main_lay.addLayout(top_bar)
        main_lay.addWidget(self.stack)
        self.setCentralWidget(container)
        
    def go_back(self):
        hist = getattr(self, "_history", [])
        if hist:
            page = hist.pop()
            self.stack.setCurrentWidget(page)
        self.back_btn.setVisible(bool(getattr(self, "_history", [])))

    def _navigate(self, frm, to):
        self._history = getattr(self, "_history", [])
        self._history.append(frm)
        self.back_btn.setVisible(True)
        self.stack.setCurrentWidget(to)

    def show_year_page(self, op_type):
        self.current_op_type = op_type
        # year_page.py má v __init__ atribut self.lbl
        self.year_page.lbl.setText(f"Selected Type: {op_type}")
        self._navigate(self.ops_page, self.year_page)

    def show_data_page(self, year):
        self.selected_year = year
        # data_page.py má atribut self.lbl
        self.data_page.lbl.setText(f"Year: {year}")

        # pokud chcete přednastavit rozsah QDateEdit na OperativePage
        if year != "2021-2025":
            try:
                yr = int(year)
                # nastavíme SpinBoxy
                self.oper_page.year_from.setValue(yr)
                self.oper_page.year_to.setValue(yr)
            except ValueError:
                pass
        else:
            # zjistíme rozsah let
            min_y = int(self.oper_df["Date of Operation"].dt.year.min())
            max_y = int(self.oper_df["Date of Operation"].dt.year.max())
            self.oper_page.year_from.setValue(min_y)
            self.oper_page.year_to.setValue(max_y)


        self._navigate(self.year_page, self.data_page)

    def show_category_page(self, category):
        mapping = {
            "Operative data":                       self.oper_page,
            "Preoperative data":                    self.preop_page,
            "Postoperative data (hospitalization)": self.discharge_page,
            "Long-term postoperative data":         self.followup_page
        }
        target = mapping.get(category)
        if not target:
            return

        # zavoláme update_view před zobrazením
        if target is self.oper_page:
            self.oper_page.update_view()
        elif target is self.preop_page:
            self.preop_page.update_view()
        elif target is self.discharge_page:
            self.discharge_page.update_view()
        elif target is self.followup_page:
            self.followup_page.update_view()

        self._navigate(self.data_page, target)
