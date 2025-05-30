# pages/main_window.py
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QStackedWidget, QSpacerItem, QSizePolicy,
    QMessageBox, QFrame
)
from data_loader import (
    load_oper_data, load_preop_data,
    load_discharge_data, load_followup_data
)
from pages.ops_page import OpsPage
from pages.year_page import YearPage
from pages.data_page import DataPage
from pages.operative_page import OperativePage
from pages.preop_page import PreopPage
from pages.discharge_page import DischargePage
from pages.followup_page import FollowupPage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Biomedical Data Analyzer")
        self.resize(1000, 800)

        self.oper_df = load_oper_data()
        self.preop_df = load_preop_data()
        self.discharge_df = load_discharge_data()
        self.followup_df = load_followup_data()

        self.current_op_type = None
        self.selected_year = None

        self._history = []

        self.ops_page = OpsPage(self)
        self.year_page = YearPage(self)
        self.data_page = DataPage(self)
        self.oper_page = OperativePage(self, self.oper_df)
        self.preop_page = PreopPage(self, self.preop_df)
        self.discharge_page = DischargePage(self, self.discharge_df)
        self.followup_page = FollowupPage(self, self.followup_df)

        self.nav_frame = QFrame()
        self.nav_frame.setObjectName("navBar")
        nav_layout = QHBoxLayout(self.nav_frame)
        nav_layout.setContentsMargins(15, 5, 15, 5)
        nav_layout.setSpacing(20)

        self.back_btn = QPushButton("Back")
        self.back_btn.setObjectName("navButton")
        self.back_btn.clicked.connect(self.go_back)
        nav_layout.addWidget(self.back_btn)

        self.btn_type = QPushButton("Type Operation")
        self.btn_type.setObjectName("navButton")
        self.btn_type.clicked.connect(self.show_operation_selection)
        nav_layout.addWidget(self.btn_type)

        self.btn_year = QPushButton("Select Year")
        self.btn_year.setObjectName("navButton")
        self.btn_year.clicked.connect(self.show_year_selection)
        nav_layout.addWidget(self.btn_year)

        nav_layout.addItem(QSpacerItem(
            0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.stack = QStackedWidget()
        for page in [
            self.ops_page, self.year_page, self.data_page,
            self.oper_page, self.preop_page,
            self.discharge_page, self.followup_page
        ]:
            self.stack.addWidget(page)

        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.nav_frame)
        main_layout.addWidget(self.stack)
        self.setCentralWidget(container)

        self.stack.setCurrentWidget(self.ops_page)
        self.update_nav_buttons()

        self.setStyleSheet("""
            /* Navigation bar background */
            QFrame#navBar {
                background-color: #FFFFFF;
                border-bottom: 1px solid #333333;
            }
            /* Navigation buttons */
            QPushButton#navButton {
                font-size: 14px;
                padding: 8px 12px;
                background: transparent;
                text-align: left;
                color: #333333;
            }
            QPushButton#navButton:hover {
                background-color: #F5F5F5;
                border-radius: 4px;
            }
            QPushButton#navButton:pressed {
                background-color: rgba(255,255,255,0.25);
            }
        """)

    def update_nav_buttons(self):
        """Set visibility of nav_frame and nav buttons based on current page."""
        cw = self.stack.currentWidget()

        if cw is self.ops_page:
            self.nav_frame.setVisible(False)
            return

        self.nav_frame.setVisible(True)

        if cw is self.year_page:
            self.back_btn.setVisible(bool(self._history))
            self.btn_type.setVisible(True)
            self.btn_year.setVisible(False)
            return

        self.back_btn.setVisible(bool(self._history))
        self.btn_type.setVisible(True)
        self.btn_year.setVisible(True)
        self.btn_year.setEnabled(bool(self.current_op_type))

    def go_back(self):
        if self._history:
            prev = self._history.pop()
            self.stack.setCurrentWidget(prev)
        self.update_nav_buttons()

    def _navigate(self, destination):
        self._history.append(self.stack.currentWidget())
        self.stack.setCurrentWidget(destination)
        self.update_nav_buttons()

    def show_operation_selection(self):
        self._navigate(self.ops_page)

    def show_year_selection(self):
        if not self.current_op_type:
            QMessageBox.warning(
                self,
                "No operation type selected",
                "Please select an operation type first."
            )
            self.show_operation_selection()
            return
        self.year_page.lbl.setText(f"Selected Type: {self.current_op_type}")
        self._navigate(self.year_page)

    def show_year_page(self, op_type):
        self.current_op_type = op_type
        self.year_page.lbl.setText(f"Selected Type: {op_type}")
        self._navigate(self.year_page)

    def show_data_page(self, year):
        self.selected_year = year
        self.data_page.update_view()
        self._navigate(self.data_page)

    def show_category_page(self, category):
        mapping = {
            "Operative data": self.oper_page,
            "Preoperative data": self.preop_page,
            "Discharge data": self.discharge_page,
            "Follow Up data": self.followup_page
        }
        target = mapping.get(category)
        if not target:
            return
        target.update_view()
        self._navigate(target)

    def show_oper_page(self):
        self.oper_page.update_view()
        self._navigate(self.oper_page)

    def show_preop_page(self):
        self.preop_page.update_view()
        self._navigate(self.preop_page)

    def show_discharge_page(self):
        self.discharge_page.update_view()
        self._navigate(self.discharge_page)

    def show_followup_page(self):
        self.followup_page.update_view()
        self._navigate(self.followup_page)
