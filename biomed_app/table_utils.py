# table_utils.py
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
from PyQt5.QtGui import QFont
from PyQt5 import QtCore

def make_stats_table(stats: dict):
    table = QTableWidget(len(stats), 2)
    table.setHorizontalHeaderLabels(["Metric","Value"])
    for row, (k,v) in enumerate(stats.items()):
        item_k = QTableWidgetItem(k)
        item_v = QTableWidgetItem(str(v))
        item_v.setTextAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        table.setItem(row,0,item_k)
        table.setItem(row,1,item_v)

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
    hdr = table.horizontalHeader()
    hdr.setSectionResizeMode(0, QHeaderView.Stretch)
    hdr.setSectionResizeMode(1, QHeaderView.ResizeToContents)
    font = QFont(); font.setBold(True); hdr.setFont(font)

    # výška = záhlaví + řádky
    row_h = table.verticalHeader().defaultSectionSize()
    hdr_h = hdr.height() or 30
    table.setMinimumHeight(hdr_h + table.rowCount()*row_h + 2)

    return table
