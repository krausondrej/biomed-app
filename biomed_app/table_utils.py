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

    # Naplnění buněk
    for row, (k, v) in enumerate(stats.items()):
        item_k = QTableWidgetItem(k)
        item_v = QTableWidgetItem(str(v))
        item_v.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        table.setItem(row, 0, item_k)
        table.setItem(row, 1, item_v)

    # Nastavení velikostní politiky tak, aby se tabulka roztahovala na šířku
    table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

    # Režimy roztažení sloupců:
    #   Metric – podle obsahu, Value – vyplní zbývající prostor
    hdr = table.horizontalHeader()
    hdr.setSectionResizeMode(0, QHeaderView.ResizeToContents)
    hdr.setSectionResizeMode(1, QHeaderView.Stretch)

    # Vzhled
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

    # Skrýt vertikální hlavičku, zamknout úpravy i výběr
    table.verticalHeader().setVisible(False)
    table.setEditTriggers(QAbstractItemView.NoEditTriggers)
    table.setSelectionMode(QAbstractItemView.NoSelection)
    table.setAlternatingRowColors(True)

    # Tučný font pro záhlaví
    font = QFont()
    font.setBold(True)
    hdr.setFont(font)

    # Spočítat výšku a šířku
    row_h = table.verticalHeader().defaultSectionSize()
    hdr_h = hdr.height() or 30
    table.setMinimumHeight(hdr_h + table.rowCount()*row_h + 2)

    return table
