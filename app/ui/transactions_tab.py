from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QLineEdit,
    QComboBox, QLabel, QHeaderView, QFrame,
    QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont
from app.db.database import get_transactions

BG    = "#F7F6F2"
CARD  = "#FFFFFF"
GREEN = "#4A9B6F"
RED   = "#C4554A"
TEXT  = "#2D2D2A"
MUTED = "#8A8A82"
BORDER= "#E8E6E0"


class TransactionsTab(QWidget):
    def __init__(self):
        super().__init__()
        self._all_rows = []
        self.setStyleSheet(f"background: {BG};")
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        # page title
        page_title = QLabel("Transactions")
        page_title.setStyleSheet(
            f"color: {TEXT}; font-size: 22px; font-family: 'Segoe UI Semibold',"
            "'Segoe UI'; font-weight: 600; background: transparent;"
        )
        layout.addWidget(page_title)

        # filter card
        filter_frame = QFrame()
        filter_frame.setStyleSheet(f"""
            QFrame {{
                background: {CARD};
                border-radius: 12px;
                border: 1px solid {BORDER};
            }}
        """)
        fx = QGraphicsDropShadowEffect()
        fx.setBlurRadius(14)
        fx.setOffset(0, 2)
        fx.setColor(QColor(0, 0, 0, 18))
        filter_frame.setGraphicsEffect(fx)

        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setContentsMargins(16, 12, 16, 12)
        filter_layout.setSpacing(12)

        search_icon = QLabel("🔍")
        search_icon.setStyleSheet("font-size: 14px; background: transparent;")

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search by payee or description...")
        self.search_box.setStyleSheet(f"""
            QLineEdit {{
                border: 1.5px solid {BORDER};
                border-radius: 8px;
                padding: 7px 14px;
                font-size: 13px;
                font-family: 'Segoe UI', sans-serif;
                color: {TEXT};
                background: #FAFAF8;
            }}
            QLineEdit:focus {{
                border: 1.5px solid {GREEN};
                background: {CARD};
            }}
        """)
        self.search_box.textChanged.connect(self._apply_filters)

        sep = QLabel("|")
        sep.setStyleSheet(f"color: {BORDER}; font-size: 18px; background: transparent;")

        cat_lbl = QLabel("Category:")
        cat_lbl.setStyleSheet(
            f"color: {MUTED}; font-size: 12px; font-family: 'Segoe UI';"
            "background: transparent; white-space: nowrap;"
        )

        self.category_filter = QComboBox()
        self.category_filter.setFixedHeight(36)
        self.category_filter.setMinimumWidth(180)
        self.category_filter.setStyleSheet(f"""
            QComboBox {{
                border: 1.5px solid {BORDER};
                border-radius: 8px;
                padding: 5px 14px;
                font-size: 13px;
                font-family: 'Segoe UI', sans-serif;
                color: {TEXT};
                background: #FAFAF8;
            }}
            QComboBox:focus {{ border: 1.5px solid {GREEN}; }}
            QComboBox::drop-down {{ border: none; width: 24px; }}
            QComboBox QAbstractItemView {{
                background: {CARD};
                color: {TEXT};
                border: 1px solid {BORDER};
                selection-background-color: {GREEN};
                selection-color: white;
                border-radius: 8px;
            }}
        """)
        self.category_filter.currentTextChanged.connect(self._apply_filters)

        self.count_lbl = QLabel("0 transactions")
        self.count_lbl.setStyleSheet(
            f"color: {MUTED}; font-size: 12px; background: transparent;"
        )

        filter_layout.addWidget(search_icon)
        filter_layout.addWidget(self.search_box)
        filter_layout.addWidget(sep)
        filter_layout.addWidget(cat_lbl)
        filter_layout.addWidget(self.category_filter)
        filter_layout.addStretch()
        filter_layout.addWidget(self.count_lbl)
        layout.addWidget(filter_frame)

        # table card
        table_frame = QFrame()
        table_frame.setStyleSheet(f"""
            QFrame {{
                background: {CARD};
                border-radius: 14px;
                border: 1px solid {BORDER};
            }}
        """)
        fx2 = QGraphicsDropShadowEffect()
        fx2.setBlurRadius(16)
        fx2.setOffset(0, 2)
        fx2.setColor(QColor(0, 0, 0, 15))
        table_frame.setGraphicsEffect(fx2)

        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(0, 0, 0, 0)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Date", "Paid To", "Category", "Mode",
            "Debit ₹", "Credit ₹", "Balance ₹"
        ])
        self.table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.ResizeToContents
        )
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background: {CARD};
                border: none;
                border-radius: 14px;
                font-size: 12px;
                font-family: 'Segoe UI', sans-serif;
                color: {TEXT};
                outline: none;
            }}
            QHeaderView::section {{
                background: #F5F4F0;
                color: {MUTED};
                padding: 10px 12px;
                font-size: 11px;
                font-family: 'Segoe UI Semibold', 'Segoe UI', sans-serif;
                font-weight: 600;
                letter-spacing: 0.5px;
                border: none;
                border-bottom: 1.5px solid {BORDER};
                text-transform: uppercase;
            }}
            QTableWidget::item {{
                padding: 8px 12px;
                border: none;
                color: {TEXT};
            }}
            QTableWidget::item:alternate {{
                background: #FAFAF8;
            }}
            QTableWidget::item:selected {{
                background: #EAF4EF;
                color: {TEXT};
            }}
        """)
        table_layout.addWidget(self.table)
        layout.addWidget(table_frame)

    def load(self, month_id: int):
        self._all_rows = get_transactions(month_id)
        self._populate_category_filter()
        self._render_table(self._all_rows)

    def _populate_category_filter(self):
        cats = sorted(set(
            r["category"] for r in self._all_rows if r["category"]
        ))
        self.category_filter.blockSignals(True)
        self.category_filter.clear()
        self.category_filter.addItem("All Categories")
        for c in cats:
            self.category_filter.addItem(c)
        self.category_filter.blockSignals(False)

    def _apply_filters(self):
        search = self.search_box.text().lower()
        cat    = self.category_filter.currentText()
        filtered = []
        for row in self._all_rows:
            if search and \
               search not in (row["paid_to"] or "").lower() and \
               search not in (row["description"] or "").lower():
                continue
            if cat != "All Categories" and row["category"] != cat:
                continue
            filtered.append(row)
        self._render_table(filtered)

    def _render_table(self, rows):
        self.table.setRowCount(len(rows))
        self.count_lbl.setText(f"{len(rows)} transactions")
        self.table.setRowHeight

        for i, row in enumerate(rows):
            debit  = row["debit"]
            credit = row["credit"]

            self.table.setItem(i, 0, QTableWidgetItem(row["date"]))
            self.table.setItem(i, 1, QTableWidgetItem(row["paid_to"] or ""))
            self.table.setItem(i, 2, QTableWidgetItem(row["category"] or ""))
            self.table.setItem(i, 3, QTableWidgetItem(
                row["mode_of_transaction"] or ""
            ))

            debit_item = QTableWidgetItem(
                f"{debit:,.2f}" if debit else "—"
            )
            debit_item.setForeground(
                QColor(RED) if debit else QColor(MUTED)
            )
            debit_item.setTextAlignment(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            )

            credit_item = QTableWidgetItem(
                f"{credit:,.2f}" if credit else "—"
            )
            credit_item.setForeground(
                QColor("#4A9B6F") if credit else QColor(MUTED)
            )
            credit_item.setTextAlignment(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            )

            balance_item = QTableWidgetItem(f"{row['balance']:,.2f}")
            balance_item.setTextAlignment(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            )
            balance_item.setForeground(QColor(TEXT))

            self.table.setItem(i, 4, debit_item)
            self.table.setItem(i, 5, credit_item)
            self.table.setItem(i, 6, balance_item)

            self.table.setRowHeight(i, 38)