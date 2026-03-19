from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QScrollArea, QSizePolicy, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("QtAgg")

from app.db.database import (
    get_summary, get_category_breakdown,
    get_daily_spend, get_balance_trend, get_top_payees
)

# ── palette ────────────────────────────────────────────────────────────────────
BG       = "#F7F6F2"
CARD     = "#FFFFFF"
GREEN    = "#4A9B6F"
BLUE     = "#5B8DB8"
AMBER    = "#C4883A"
RED      = "#C4554A"
MUTED    = "#8A8A82"
TEXT     = "#2D2D2A"
BORDER   = "#E8E6E0"

CHART_COLORS = [
    "#4A9B6F", "#5B8DB8", "#C4883A", "#9B6F9B",
    "#6F9B9B", "#C4554A", "#8DB85B", "#B85B8D"
]

def _shadow(widget, blur=18, offset=2, opacity=0.08):
    fx = QGraphicsDropShadowEffect()
    fx.setBlurRadius(blur)
    fx.setOffset(0, offset)
    fx.setColor(QColor(0, 0, 0, int(255 * opacity)))
    widget.setGraphicsEffect(fx)
    return widget


def make_kpi_card(title, value, subtitle, color, icon):
    frame = QFrame()
    frame.setStyleSheet(f"""
        QFrame {{
            background: {CARD};
            border-radius: 14px;
            border: 1px solid {BORDER};
        }}
    """)
    _shadow(frame)
    frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    frame.setFixedHeight(110)

    layout = QHBoxLayout(frame)
    layout.setContentsMargins(20, 16, 20, 16)
    layout.setSpacing(16)

    # icon circle
    icon_lbl = QLabel(icon)
    icon_lbl.setFixedSize(44, 44)
    icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    icon_lbl.setStyleSheet(f"""
        QLabel {{
            background: {color}18;
            border-radius: 22px;
            font-size: 20px;
        }}
    """)

    # text
    text_widget = QWidget()
    text_widget.setStyleSheet("background: transparent;")
    text_layout = QVBoxLayout(text_widget)
    text_layout.setContentsMargins(0, 0, 0, 0)
    text_layout.setSpacing(3)

    lbl_title = QLabel(title)
    lbl_title.setStyleSheet(
        f"color: {MUTED}; font-size: 11px; font-family: 'Segoe UI';"
        "letter-spacing: 0.5px; background: transparent;"
    )

    lbl_value = QLabel(value)
    lbl_value.setStyleSheet(
        f"color: {TEXT}; font-size: 20px; font-family: 'Segoe UI Semibold',"
        f"'Segoe UI'; font-weight: 600; background: transparent;"
    )

    lbl_sub = QLabel(subtitle)
    lbl_sub.setStyleSheet(
        f"color: {color}; font-size: 11px; font-family: 'Segoe UI';"
        "background: transparent;"
    )

    text_layout.addWidget(lbl_title)
    text_layout.addWidget(lbl_value)
    text_layout.addWidget(lbl_sub)

    layout.addWidget(icon_lbl)
    layout.addWidget(text_widget)
    return frame


def make_chart_card(title, figure, canvas):
    """Wrap a matplotlib canvas in a styled card."""
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
        f"color: {TEXT}; font-size: 13px; font-family: 'Segoe UI Semibold',"
        "'Segoe UI'; font-weight: 600; background: transparent;"
    )
    layout.addWidget(title_lbl)
    layout.addWidget(canvas)
    return frame


def style_axes(ax, fig):
    """Apply consistent calm styling to a matplotlib axes."""
    fig.patch.set_facecolor(CARD)
    ax.set_facecolor("#FAFAF8")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(BORDER)
    ax.spines["bottom"].set_color(BORDER)
    ax.tick_params(colors=MUTED, labelsize=8)
    ax.yaxis.label.set_color(MUTED)
    ax.xaxis.label.set_color(MUTED)
    ax.grid(axis="y", color=BORDER, linewidth=0.8, linestyle="--", alpha=0.7)
    ax.set_axisbelow(True)


class DashboardTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"background: {BG};")
        self._build_ui()

    def _build_ui(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"""
            QScrollArea {{ border: none; background: {BG}; }}
        """)

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
        page_title = QLabel("Overview")
        page_title.setStyleSheet(
            f"color: {TEXT}; font-size: 22px; font-family: 'Segoe UI Semibold',"
            "'Segoe UI'; font-weight: 600; background: transparent;"
        )
        self.main_layout.addWidget(page_title)

        # KPI cards row
        self.kpi_row = QHBoxLayout()
        self.kpi_row.setSpacing(16)
        self.main_layout.addLayout(self.kpi_row)

        # charts row 1
        row1 = QHBoxLayout()
        row1.setSpacing(16)

        self.fig1 = Figure(figsize=(5, 3.2), tight_layout=True)
        self.ax1  = self.fig1.add_subplot(111)
        self.cv1  = FigureCanvas(self.fig1)
        self.cv1.setMinimumHeight(240)

        self.fig2 = Figure(figsize=(5, 3.2), tight_layout=True)
        self.ax2  = self.fig2.add_subplot(111)
        self.cv2  = FigureCanvas(self.fig2)
        self.cv2.setMinimumHeight(240)

        row1.addWidget(make_chart_card("Spending by Category", self.fig1, self.cv1))
        row1.addWidget(make_chart_card("Daily Spend", self.fig2, self.cv2))
        self.main_layout.addLayout(row1)

        # charts row 2
        row2 = QHBoxLayout()
        row2.setSpacing(16)

        self.fig3 = Figure(figsize=(5, 3.2), tight_layout=True)
        self.ax3  = self.fig3.add_subplot(111)
        self.cv3  = FigureCanvas(self.fig3)
        self.cv3.setMinimumHeight(240)

        self.fig4 = Figure(figsize=(5, 3.2), tight_layout=True)
        self.ax4  = self.fig4.add_subplot(111)
        self.cv4  = FigureCanvas(self.fig4)
        self.cv4.setMinimumHeight(240)

        row2.addWidget(make_chart_card("Balance Trend", self.fig3, self.cv3))
        row2.addWidget(make_chart_card("Top Payees", self.fig4, self.cv4))
        self.main_layout.addLayout(row2)

        self.main_layout.addStretch()

    def load(self, month_id: int):
        self._update_kpi(month_id)
        self._draw_pie(month_id)
        self._draw_daily(month_id)
        self._draw_balance(month_id)
        self._draw_payees(month_id)

    def _clear_kpi(self):
        while self.kpi_row.count():
            item = self.kpi_row.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _update_kpi(self, month_id):
        self._clear_kpi()
        s = get_summary(month_id)
        savings_color = GREEN if s["net_savings"] >= 0 else RED
        cards = [
            ("Total Income",    f"₹{s['total_income']:,.0f}",
             "credited this month",   GREEN,  "💰"),
            ("Total Expense",   f"₹{s['total_expense']:,.0f}",
             "debited this month",    RED,    "💸"),
            ("Net Savings",     f"₹{s['net_savings']:,.0f}",
             "income minus expense",  savings_color, "📈"),
            ("Closing Balance", f"₹{s['closing_balance']:,.2f}",
             "final balance",         AMBER,  "🏦"),
        ]
        for title, value, sub, color, icon in cards:
            self.kpi_row.addWidget(make_kpi_card(title, value, sub, color, icon))

    def _draw_pie(self, month_id):
        self.ax1.clear()
        data = get_category_breakdown(month_id)
        if not data:
            self.ax1.text(0.5, 0.5, "No data", ha="center",
                          va="center", color=MUTED)
            self.cv1.draw()
            return

        labels = [d["category"] for d in data]
        values = [d["total"]    for d in data]

        self.fig1.patch.set_facecolor(CARD)
        wedges, _, autotexts = self.ax1.pie(
            values,
            labels=None,
            autopct="%1.0f%%",
            colors=CHART_COLORS[:len(labels)],
            startangle=140,
            wedgeprops={"edgecolor": CARD, "linewidth": 2.5},
            pctdistance=0.75,
        )
        for at in autotexts:
            at.set_fontsize(8)
            at.set_color(CARD)
            at.set_fontweight("bold")

        self.ax1.legend(
            labels,
            loc="lower center",
            bbox_to_anchor=(0.5, -0.18),
            ncol=2,
            fontsize=8,
            frameon=False,
            labelcolor=TEXT,
        )
        self.fig1.tight_layout()
        self.cv1.draw()

    def _draw_daily(self, month_id):
        self.ax2.clear()
        data = get_daily_spend(month_id)
        if not data:
            self.ax2.text(0.5, 0.5, "No data", ha="center",
                          va="center", color=MUTED)
            self.cv2.draw()
            return

        days  = [d["date"].split("-")[0] for d in data]
        spend = [d["total_debit"] for d in data]

        style_axes(self.ax2, self.fig2)
        bars = self.ax2.bar(
            days, spend,
            color=BLUE, alpha=0.75, width=0.6,
            zorder=3
        )
        # highlight max bar
        if spend:
            max_i = spend.index(max(spend))
            bars[max_i].set_color(AMBER)
            bars[max_i].set_alpha(0.9)

        self.ax2.set_xlabel("Day of Month", fontsize=9)
        self.ax2.set_ylabel("₹ Spent",      fontsize=9)
        self.ax2.tick_params(axis="x", rotation=45, labelsize=7)
        self.fig2.tight_layout()
        self.cv2.draw()

    def _draw_balance(self, month_id):
        self.ax3.clear()
        data = get_balance_trend(month_id)
        if not data:
            self.ax3.text(0.5, 0.5, "No data", ha="center",
                          va="center", color=MUTED)
            self.cv3.draw()
            return

        days    = list(range(len(data)))
        balance = [d["balance"] for d in data]
        labels  = [d["date"].split("-")[0] for d in data]

        style_axes(self.ax3, self.fig3)
        self.ax3.plot(
            days, balance,
            color=GREEN, linewidth=2.2,
            marker="o", markersize=3.5,
            markerfacecolor=CARD,
            markeredgecolor=GREEN,
            markeredgewidth=1.5,
            zorder=4
        )
        self.ax3.fill_between(days, balance, alpha=0.08, color=GREEN)
        self.ax3.set_xticks(days[::max(1, len(days)//8)])
        self.ax3.set_xticklabels(
            labels[::max(1, len(labels)//8)],
            rotation=45, fontsize=7
        )
        self.ax3.set_ylabel("₹ Balance", fontsize=9)
        self.fig3.tight_layout()
        self.cv3.draw()

    def _draw_payees(self, month_id):
        self.ax4.clear()
        data = get_top_payees(month_id, limit=8)
        if not data:
            self.ax4.text(0.5, 0.5, "No data", ha="center",
                          va="center", color=MUTED)
            self.cv4.draw()
            return

        names  = [d["paid_to"][:22] for d in reversed(data)]
        totals = [d["total"]         for d in reversed(data)]

        style_axes(self.ax4, self.fig4)
        bars = self.ax4.barh(
            names, totals,
            color=CHART_COLORS[:len(names)],
            alpha=0.80,
            height=0.6,
            zorder=3
        )
        self.ax4.set_xlabel("₹ Total Debited", fontsize=9)
        self.ax4.tick_params(axis="y", labelsize=8)
        self.ax4.spines["left"].set_visible(False)
        self.ax4.tick_params(axis="y", length=0)
        self.fig4.tight_layout()
        self.cv4.draw()