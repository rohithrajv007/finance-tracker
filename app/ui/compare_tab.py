from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QFrame, QScrollArea, QSizePolicy,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import matplotlib
matplotlib.use("QtAgg")
import numpy as np

from app.db.database import (
    get_all_months, get_summary,
    get_category_breakdown, get_monthly_comparison
)

BG     = "#F7F6F2"
CARD   = "#FFFFFF"
GREEN  = "#4A9B6F"
BLUE   = "#5B8DB8"
AMBER  = "#C4883A"
RED    = "#C4554A"
PURPLE = "#9B6F9B"
TEXT   = "#2D2D2A"
MUTED  = "#8A8A82"
BORDER = "#E8E6E0"

CHART_COLORS = [
    "#4A9B6F", "#5B8DB8", "#C4883A", "#9B6F9B",
    "#6F9B9B", "#C4554A", "#8DB85B", "#B85B8D"
]


def _shadow(widget, blur=16, offset=2, opacity=0.07):
    fx = QGraphicsDropShadowEffect()
    fx.setBlurRadius(blur)
    fx.setOffset(0, offset)
    fx.setColor(QColor(0, 0, 0, int(255 * opacity)))
    widget.setGraphicsEffect(fx)
    return widget


def style_axes(ax, fig):
    fig.patch.set_facecolor(CARD)
    ax.set_facecolor("#FAFAF8")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(BORDER)
    ax.spines["bottom"].set_color(BORDER)
    ax.tick_params(colors=MUTED, labelsize=8)
    ax.grid(axis="y", color=BORDER, linewidth=0.8,
            linestyle="--", alpha=0.7)
    ax.set_axisbelow(True)


def make_chart_card(title, fig, canvas):
    frame = QFrame()
    frame.setStyleSheet(f"""
        QFrame {{
            background: {CARD};
            border-radius: 14px;
            border: 1px solid {BORDER};
        }}
    """)
    _shadow(frame)
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(16, 14, 16, 14)
    layout.setSpacing(8)
    title_lbl = QLabel(title)
    title_lbl.setStyleSheet(
        f"color: {TEXT}; font-size: 13px; "
        "font-family: 'Segoe UI Semibold', 'Segoe UI'; "
        "font-weight: 600; background: transparent;"
    )
    layout.addWidget(title_lbl)
    layout.addWidget(canvas)
    return frame


def stat_card(title, val_left, val_right, color, change_pct=None):
    frame = QFrame()
    frame.setStyleSheet(f"""
        QFrame {{
            background: {CARD};
            border-radius: 12px;
            border: 1px solid {BORDER};
            border-top: 3px solid {color};
        }}
    """)
    _shadow(frame)
    frame.setFixedHeight(108)
    frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    layout = QVBoxLayout(frame)
    layout.setContentsMargins(16, 12, 16, 12)
    layout.setSpacing(4)

    lbl_title = QLabel(title)
    lbl_title.setStyleSheet(
        f"color: {MUTED}; font-size: 10px; letter-spacing: 1px; "
        "font-family: 'Segoe UI'; background: transparent;"
    )

    row = QHBoxLayout()
    row.setSpacing(6)

    lbl_left = QLabel(val_left)
    lbl_left.setStyleSheet(
        f"color: {TEXT}; font-size: 16px; "
        "font-family: 'Segoe UI Semibold', 'Segoe UI'; "
        "font-weight: 600; background: transparent;"
    )
    sep = QLabel("→")
    sep.setStyleSheet(f"color: {MUTED}; font-size: 14px; background: transparent;")

    lbl_right = QLabel(val_right)
    lbl_right.setStyleSheet(
        f"color: {color}; font-size: 16px; "
        "font-family: 'Segoe UI Semibold', 'Segoe UI'; "
        "font-weight: 600; background: transparent;"
    )

    row.addWidget(lbl_left)
    row.addWidget(sep)
    row.addWidget(lbl_right)
    row.addStretch()

    layout.addWidget(lbl_title)
    layout.addLayout(row)

    if change_pct is not None:
        arrow = "▲" if change_pct >= 0 else "▼"
        clr   = RED if change_pct >= 0 else GREEN
        chg   = QLabel(f"{arrow} {abs(change_pct):.1f}% vs previous")
        chg.setStyleSheet(
            f"color: {clr}; font-size: 11px; "
            "font-family: 'Segoe UI'; background: transparent;"
        )
        layout.addWidget(chg)

    return frame


class CompareTab(QWidget):
    def __init__(self):
        super().__init__()
        self._months_data = []
        self.setStyleSheet(f"background: {BG};")
        self._build_ui()

    def _build_ui(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"QScrollArea {{ border: none; background: {BG}; }}")

        container = QWidget()
        container.setStyleSheet(f"background: {BG};")
        scroll.setWidget(container)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

        self.main_layout = QVBoxLayout(container)
        self.main_layout.setContentsMargins(28, 24, 28, 28)
        self.main_layout.setSpacing(20)

        # page title
        page_title = QLabel("Compare Months")
        page_title.setStyleSheet(
            f"color: {TEXT}; font-size: 22px; "
            "font-family: 'Segoe UI Semibold', 'Segoe UI'; "
            "font-weight: 600; background: transparent;"
        )
        self.main_layout.addWidget(page_title)

        # picker card
        picker = QFrame()
        picker.setStyleSheet(f"""
            QFrame {{
                background: {CARD};
                border-radius: 12px;
                border: 1px solid {BORDER};
            }}
        """)
        _shadow(picker)
        picker_layout = QHBoxLayout(picker)
        picker_layout.setContentsMargins(20, 14, 20, 14)
        picker_layout.setSpacing(14)

        lbl = QLabel("Compare")
        lbl.setStyleSheet(
            f"color: {TEXT}; font-size: 13px; "
            "font-family: 'Segoe UI Semibold', 'Segoe UI'; "
            "font-weight: 600; background: transparent;"
        )

        combo_style = f"""
            QComboBox {{
                border: 1.5px solid {BORDER};
                border-radius: 8px;
                padding: 6px 14px;
                font-size: 13px;
                font-family: 'Segoe UI', sans-serif;
                color: {TEXT};
                background: #FAFAF8;
                min-width: 150px;
            }}
            QComboBox:focus {{ border: 1.5px solid {GREEN}; }}
            QComboBox::drop-down {{ border: none; width: 24px; }}
            QComboBox QAbstractItemView {{
                background: {CARD};
                color: {TEXT};
                border: 1px solid {BORDER};
                selection-background-color: {GREEN};
                selection-color: white;
            }}
        """
        self.combo_left  = QComboBox()
        self.combo_right = QComboBox()
        self.combo_left.setStyleSheet(combo_style)
        self.combo_right.setStyleSheet(combo_style)

        vs = QLabel("vs")
        vs.setStyleSheet(
            f"color: {MUTED}; font-size: 14px; "
            "font-weight: bold; background: transparent;"
        )
        vs.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.combo_left.currentIndexChanged.connect(self._on_selection_changed)
        self.combo_right.currentIndexChanged.connect(self._on_selection_changed)

        picker_layout.addWidget(lbl)
        picker_layout.addWidget(self.combo_left)
        picker_layout.addWidget(vs)
        picker_layout.addWidget(self.combo_right)
        picker_layout.addStretch()
        self.main_layout.addWidget(picker)

        # stat cards row
        self.cards_row = QHBoxLayout()
        self.cards_row.setSpacing(14)
        self.main_layout.addLayout(self.cards_row)

        # charts row 1
        row1 = QHBoxLayout()
        row1.setSpacing(16)

        self.fig1 = Figure(figsize=(5.5, 3.5), tight_layout=True)
        self.ax1  = self.fig1.add_subplot(111)
        self.cv1  = FigureCanvas(self.fig1)
        self.cv1.setMinimumHeight(250)

        self.fig2 = Figure(figsize=(5.5, 3.5), tight_layout=True)
        self.ax2  = self.fig2.add_subplot(111)
        self.cv2  = FigureCanvas(self.fig2)
        self.cv2.setMinimumHeight(250)

        row1.addWidget(make_chart_card("Income vs Expense vs Savings", self.fig1, self.cv1))
        row1.addWidget(make_chart_card("Category Spend Comparison",    self.fig2, self.cv2))
        self.main_layout.addLayout(row1)

        # charts row 2
        row2 = QHBoxLayout()
        row2.setSpacing(16)

        self.fig3 = Figure(figsize=(5.5, 3.2), tight_layout=True)
        self.ax3  = self.fig3.add_subplot(111)
        self.cv3  = FigureCanvas(self.fig3)
        self.cv3.setMinimumHeight(230)

        self.fig4 = Figure(figsize=(5.5, 3.2), tight_layout=True)
        self.ax4  = self.fig4.add_subplot(111)
        self.cv4  = FigureCanvas(self.fig4)
        self.cv4.setMinimumHeight(230)

        row2.addWidget(make_chart_card("All Months — Income vs Expense", self.fig3, self.cv3))
        row2.addWidget(make_chart_card("Net Savings per Month",          self.fig4, self.cv4))
        self.main_layout.addLayout(row2)

        # diff table
        self.diff_table = self._make_diff_table()
        table_card = QFrame()
        table_card.setStyleSheet(f"""
            QFrame {{
                background: {CARD};
                border-radius: 14px;
                border: 1px solid {BORDER};
            }}
        """)
        _shadow(table_card)
        tc_layout = QVBoxLayout(table_card)
        tc_layout.setContentsMargins(0, 0, 0, 0)

        tbl_title = QLabel("  Category Breakdown")
        tbl_title.setStyleSheet(
            f"color: {TEXT}; font-size: 13px; padding: 14px 16px 8px 16px;"
            "font-family: 'Segoe UI Semibold', 'Segoe UI'; "
            "font-weight: 600; background: transparent;"
        )
        tc_layout.addWidget(tbl_title)
        tc_layout.addWidget(self.diff_table)
        self.main_layout.addWidget(table_card)
        self.main_layout.addStretch()

    def refresh(self):
        self._months_data = get_all_months()
        self._populate_combos()
        self._draw_all_months_trend()
        self._draw_savings_trend()

    def _populate_combos(self):
        labels = [m["label"] for m in self._months_data]
        self.combo_left.blockSignals(True)
        self.combo_right.blockSignals(True)
        self.combo_left.clear()
        self.combo_right.clear()
        for lbl in labels:
            self.combo_left.addItem(lbl)
            self.combo_right.addItem(lbl)
        if len(labels) >= 2:
            self.combo_left.setCurrentIndex(1)
            self.combo_right.setCurrentIndex(0)
        elif len(labels) == 1:
            self.combo_left.setCurrentIndex(0)
            self.combo_right.setCurrentIndex(0)
        self.combo_left.blockSignals(False)
        self.combo_right.blockSignals(False)
        self._on_selection_changed()

    def _selected_months(self):
        li = self.combo_left.currentIndex()
        ri = self.combo_right.currentIndex()
        if li < 0 or ri < 0 or not self._months_data:
            return None, None
        return self._months_data[li], self._months_data[ri]

    def _on_selection_changed(self):
        ml, mr = self._selected_months()
        if not ml or not mr:
            return
        self._update_stat_cards(ml, mr)
        self._draw_grouped_bar(ml, mr)
        self._draw_category_overlap(ml, mr)
        self._update_diff_table(ml, mr)

    def _clear_cards(self):
        while self.cards_row.count():
            item = self.cards_row.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _update_stat_cards(self, ml, mr):
        self._clear_cards()
        sl = get_summary(ml["id"])
        sr = get_summary(mr["id"])

        def pct(old, new):
            return ((new - old) / old * 100) if old != 0 else None

        cards = [
            ("INCOME",  f"₹{sl['total_income']:,.0f}",
             f"₹{sr['total_income']:,.0f}",
             GREEN, pct(sl["total_income"],  sr["total_income"])),
            ("EXPENSE", f"₹{sl['total_expense']:,.0f}",
             f"₹{sr['total_expense']:,.0f}",
             RED,   pct(sl["total_expense"], sr["total_expense"])),
            ("SAVINGS", f"₹{sl['net_savings']:,.0f}",
             f"₹{sr['net_savings']:,.0f}",
             BLUE,  pct(sl["net_savings"],   sr["net_savings"])),
            ("BALANCE", f"₹{sl['closing_balance']:,.0f}",
             f"₹{sr['closing_balance']:,.0f}",
             AMBER, None),
        ]
        for title, vl, vr, color, chg in cards:
            self.cards_row.addWidget(stat_card(title, vl, vr, color, chg))

    def _draw_grouped_bar(self, ml, mr):
        self.ax1.clear()
        sl = get_summary(ml["id"])
        sr = get_summary(mr["id"])
        labels  = ["Income", "Expense", "Savings"]
        vals_l  = [sl["total_income"],  sl["total_expense"], sl["net_savings"]]
        vals_r  = [sr["total_income"],  sr["total_expense"], sr["net_savings"]]
        x       = np.arange(len(labels))
        w       = 0.35
        style_axes(self.ax1, self.fig1)
        b1 = self.ax1.bar(x - w/2, vals_l, w, label=ml["label"],
                           color=GREEN, alpha=0.75, zorder=3)
        b2 = self.ax1.bar(x + w/2, vals_r, w, label=mr["label"],
                           color=BLUE,  alpha=0.75, zorder=3)
        for bar in list(b1) + list(b2):
            h = bar.get_height()
            if h > 0:
                self.ax1.text(
                    bar.get_x() + bar.get_width() / 2, h * 1.01,
                    f"₹{h/1000:.1f}k", ha="center", va="bottom",
                    fontsize=7, color=MUTED
                )
        self.ax1.set_xticks(x)
        self.ax1.set_xticklabels(labels, fontsize=10, color=TEXT)
        self.ax1.set_ylabel("₹", fontsize=9)
        self.ax1.legend(fontsize=8, frameon=False, labelcolor=TEXT)
        self.fig1.tight_layout()
        self.cv1.draw()

    def _draw_category_overlap(self, ml, mr):
        self.ax2.clear()
        dl = {d["category"]: d["total"] for d in get_category_breakdown(ml["id"])}
        dr = {d["category"]: d["total"] for d in get_category_breakdown(mr["id"])}
        all_cats = sorted(set(list(dl.keys()) + list(dr.keys())))
        vals_l   = [dl.get(c, 0) for c in all_cats]
        vals_r   = [dr.get(c, 0) for c in all_cats]
        x        = np.arange(len(all_cats))
        w        = 0.35
        style_axes(self.ax2, self.fig2)
        self.ax2.bar(x - w/2, vals_l, w, label=ml["label"],
                     color=PURPLE, alpha=0.75, zorder=3)
        self.ax2.bar(x + w/2, vals_r, w, label=mr["label"],
                     color=AMBER,  alpha=0.75, zorder=3)
        self.ax2.set_xticks(x)
        self.ax2.set_xticklabels(
            [c[:10] for c in all_cats],
            fontsize=7, rotation=30, ha="right", color=TEXT
        )
        self.ax2.set_ylabel("₹", fontsize=9)
        self.ax2.legend(fontsize=8, frameon=False, labelcolor=TEXT)
        self.fig2.tight_layout()
        self.cv2.draw()

    def _draw_all_months_trend(self):
        self.ax3.clear()
        data = get_monthly_comparison()
        if len(data) < 1:
            self.ax3.text(0.5, 0.5, "Import 2+ months to see trend",
                          ha="center", va="center",
                          fontsize=10, color=MUTED)
            self.cv3.draw()
            return
        labels   = [d["label"]         for d in data]
        incomes  = [d["total_income"]  for d in data]
        expenses = [d["total_expense"] for d in data]
        x = range(len(labels))
        style_axes(self.ax3, self.fig3)
        self.ax3.plot(x, incomes,  marker="o", color=GREEN,
                      linewidth=2, markersize=5,
                      markerfacecolor=CARD, markeredgewidth=1.5,
                      label="Income",  zorder=4)
        self.ax3.plot(x, expenses, marker="o", color=RED,
                      linewidth=2, markersize=5,
                      markerfacecolor=CARD, markeredgewidth=1.5,
                      label="Expense", zorder=4)
        self.ax3.fill_between(x, incomes,  alpha=0.07, color=GREEN)
        self.ax3.fill_between(x, expenses, alpha=0.07, color=RED)
        self.ax3.set_xticks(list(x))
        self.ax3.set_xticklabels(labels, fontsize=8,
                                  rotation=20, ha="right", color=TEXT)
        self.ax3.set_ylabel("₹", fontsize=9)
        self.ax3.legend(fontsize=8, frameon=False, labelcolor=TEXT)
        self.fig3.tight_layout()
        self.cv3.draw()

    def _draw_savings_trend(self):
        self.ax4.clear()
        data = get_monthly_comparison()
        if len(data) < 1:
            self.ax4.text(0.5, 0.5, "Import 2+ months to see trend",
                          ha="center", va="center",
                          fontsize=10, color=MUTED)
            self.cv4.draw()
            return
        labels  = [d["label"] for d in data]
        savings = [d["total_income"] - d["total_expense"] for d in data]
        colors  = [GREEN if s >= 0 else RED for s in savings]
        style_axes(self.ax4, self.fig4)
        self.ax4.bar(labels, savings, color=colors, alpha=0.8,
                     width=0.5, zorder=3)
        self.ax4.axhline(0, color=BORDER, linewidth=1.2, linestyle="--")
        self.ax4.set_ylabel("₹", fontsize=9)
        self.ax4.tick_params(axis="x", rotation=20, labelsize=8)
        self.fig4.tight_layout()
        self.cv4.draw()

    def _make_diff_table(self):
        tbl = QTableWidget(0, 5)
        tbl.setHorizontalHeaderLabels([
            "Category", "Month A (₹)", "Month B (₹)", "Diff (₹)", "Change"
        ])
        tbl.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        tbl.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        tbl.setAlternatingRowColors(True)
        tbl.verticalHeader().setVisible(False)
        tbl.setShowGrid(False)
        tbl.setMaximumHeight(240)
        tbl.setStyleSheet(f"""
            QTableWidget {{
                background: {CARD};
                border: none;
                font-size: 12px;
                font-family: 'Segoe UI', sans-serif;
                color: {TEXT};
                outline: none;
            }}
            QHeaderView::section {{
                background: #F5F4F0;
                color: {MUTED};
                padding: 8px 12px;
                font-size: 11px;
                letter-spacing: 0.5px;
                font-family: 'Segoe UI Semibold', 'Segoe UI';
                font-weight: 600;
                border: none;
                border-bottom: 1.5px solid {BORDER};
                text-transform: uppercase;
            }}
            QTableWidget::item {{
                padding: 7px 12px;
                color: {TEXT};
            }}
            QTableWidget::item:alternate {{ background: #FAFAF8; }}
            QTableWidget::item:selected {{
                background: #EAF4EF;
                color: {TEXT};
            }}
        """)
        return tbl

    def _update_diff_table(self, ml, mr):
        dl = {d["category"]: d["total"] for d in get_category_breakdown(ml["id"])}
        dr = {d["category"]: d["total"] for d in get_category_breakdown(mr["id"])}
        all_cats = sorted(set(list(dl.keys()) + list(dr.keys())))
        self.diff_table.setRowCount(len(all_cats))

        for i, cat in enumerate(all_cats):
            vl   = dl.get(cat, 0.0)
            vr   = dr.get(cat, 0.0)
            diff = vr - vl
            pct  = ((diff / vl) * 100) if vl else None

            self.diff_table.setItem(i, 0, QTableWidgetItem(cat))

            item_l = QTableWidgetItem(f"{vl:,.0f}")
            item_l.setTextAlignment(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            )
            item_r = QTableWidgetItem(f"{vr:,.0f}")
            item_r.setTextAlignment(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            )

            diff_item = QTableWidgetItem(f"{diff:+,.0f}")
            diff_item.setTextAlignment(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            )
            diff_item.setForeground(
                QColor(RED) if diff > 0 else
                QColor(GREEN) if diff < 0 else QColor(MUTED)
            )

            if pct is not None:
                arrow    = "▲" if pct >= 0 else "▼"
                pct_item = QTableWidgetItem(f"{arrow} {abs(pct):.1f}%")
                pct_item.setForeground(
                    QColor(RED) if pct >= 0 else QColor(GREEN)
                )
            else:
                pct_item = QTableWidgetItem("— new")
                pct_item.setForeground(QColor(MUTED))

            self.diff_table.setItem(i, 1, item_l)
            self.diff_table.setItem(i, 2, item_r)
            self.diff_table.setItem(i, 3, diff_item)
            self.diff_table.setItem(i, 4, pct_item)
            self.diff_table.setRowHeight(i, 36)