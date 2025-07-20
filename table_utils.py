# table_utils.py
from PyQt5.QtWidgets import (
    QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QSizePolicy
)
from PyQt5.QtGui import QFont
from PyQt5 import QtCore


def make_stats_table(stats: dict):
    table = QTableWidget(len(stats), 2)
    table.setHorizontalHeaderLabels(["Metric", "Value"])

    for row, (k, v) in enumerate(stats.items()):
        item_k = QTableWidgetItem(k)
        item_v = QTableWidgetItem(str(v))
        item_v.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        table.setItem(row, 0, item_k)
        table.setItem(row, 1, item_v)

    table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

    hdr = table.horizontalHeader()
    hdr.setSectionResizeMode(0, QHeaderView.ResizeToContents)
    hdr.setSectionResizeMode(1, QHeaderView.Stretch)

    table.setShowGrid(True)
    table.setGridStyle(QtCore.Qt.SolidLine)
    table.setStyleSheet("""
        QTableWidget {
            background-color: transparent;
            alternate-background-color: rgba(255,255,255,0.1);
        }
        QTableWidget::item {
            border: 1px solid #CCCCCC;
        }
        QHeaderView::section {
            background-color: black;
            color: #E0E1DD;
            font-weight: bold;
            border: 1px solid #666;
        }
    """)

    table.verticalHeader().setVisible(False)
    table.setEditTriggers(QAbstractItemView.NoEditTriggers)
    table.setSelectionMode(QAbstractItemView.NoSelection)
    table.setAlternatingRowColors(True)

    font = QFont()
    font.setBold(True)
    hdr.setFont(font)

    row_h = table.verticalHeader().defaultSectionSize()
    hdr_h = hdr.height() or 30
    table.setMinimumHeight(hdr_h + table.rowCount()*row_h + 2)

    return table
