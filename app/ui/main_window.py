from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QListWidget, QPushButton, QTabWidget, QLabel,
    QFileDialog, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

from app.db.database import init_db, get_all_months
from app.db.importer import import_json
from app.ui.dashboard_tab import DashboardTab
from app.ui.transactions_tab import TransactionsTab
from app.ui.compare_tab import CompareTab
from app.ui.chat_tab import ChatTab
from app.ui.settings_tab import SettingsTab
import app.settings as settings
from app.ui.lm_studio_guide_tab import LMStudioGuideTab
BG_BASE      = "#F7F6F2"
BG_SIDEBAR   = "#2C3E35"
ACCENT_GREEN = "#4A9B6F"
TEXT_PRIMARY = "#2D2D2A"
MUTED        = "#8A8A82"
BORDER       = "#E8E6E0"
SIDEBAR_TEXT = "#D4E8DC"
SIDEBAR_MUTED= "#7A9E87"

DARK_BG_BASE    = "#1A1D1B"
DARK_BG_SIDEBAR = "#141714"
DARK_CARD       = "#242724"
DARK_TEXT       = "#E8EDE9"
DARK_MUTED      = "#7A8A7C"
DARK_BORDER     = "#2E352F"


def get_app_style(theme: str) -> str:
    if theme == "dark":
        bg      = DARK_BG_BASE
        tab_bg  = DARK_CARD
        tab_sel = DARK_BG_BASE
        text    = DARK_TEXT
        muted   = DARK_MUTED
        border  = DARK_BORDER
    else:
        bg      = BG_BASE
        tab_bg  = "#EFEFEB"
        tab_sel = BG_BASE
        text    = TEXT_PRIMARY
        muted   = MUTED
        border  = BORDER

    return f"""
        QMainWindow {{ background: {bg}; }}

        #sidebar {{
            background: {BG_SIDEBAR if theme == "light" else DARK_BG_SIDEBAR};
        }}
        #appTitle {{
            color: #E8F5EC;
            font-size: 15px;
            font-family: 'Segoe UI Semibold', 'Segoe UI', sans-serif;
            padding: 4px 0 16px 0;
            letter-spacing: 0.5px;
        }}
        #sectionLabel {{
            color: {SIDEBAR_MUTED};
            font-size: 9px;
            font-family: 'Segoe UI', sans-serif;
            letter-spacing: 2px;
            padding: 12px 0 4px 2px;
        }}
        #importBtn {{
            background: {ACCENT_GREEN};
            color: #FFFFFF;
            border: none;
            border-radius: 8px;
            padding: 10px 14px;
            font-size: 13px;
            font-family: 'Segoe UI Semibold', 'Segoe UI', sans-serif;
            text-align: left;
        }}
        #importBtn:hover {{ background: #3D8A5E; }}
        #importBtn:pressed {{ background: #357A54; }}

        #monthList {{
            background: transparent;
            border: none;
            color: {SIDEBAR_TEXT};
            font-size: 13px;
            font-family: 'Segoe UI', sans-serif;
            outline: none;
        }}
        #monthList::item {{
            padding: 9px 10px;
            border-radius: 8px;
            margin: 1px 0;
            color: {SIDEBAR_TEXT};
        }}
        #monthList::item:selected {{
            background: rgba(74,155,111,0.35);
            color: #E8F5EC;
        }}
        #monthList::item:hover:!selected {{
            background: rgba(255,255,255,0.07);
        }}

        QTabWidget::pane {{
            border: none;
            background: {bg};
        }}
        QTabBar {{
            background: {"#FFFFFF" if theme == "light" else DARK_CARD};
            border-bottom: 1px solid {border};
        }}
        QTabBar::tab {{
            background: transparent;
            color: {muted};
            padding: 12px 24px;
            font-size: 13px;
            font-family: 'Segoe UI', sans-serif;
            border: none;
            border-bottom: 3px solid transparent;
            margin-bottom: -1px;
        }}
        QTabBar::tab:selected {{
            color: {ACCENT_GREEN};
            border-bottom: 3px solid {ACCENT_GREEN};
            font-family: 'Segoe UI Semibold', 'Segoe UI', sans-serif;
        }}
        QTabBar::tab:hover:!selected {{
            color: {text};
            background: {bg};
        }}

        QScrollBar:vertical {{
            background: transparent;
            width: 6px;
            margin: 0;
        }}
        QScrollBar::handle:vertical {{
            background: #C8C5BC;
            border-radius: 3px;
            min-height: 30px;
        }}
        QScrollBar::handle:vertical:hover {{ background: #A8A59C; }}
        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {{ height: 0px; }}
        QScrollBar:horizontal {{
            background: transparent;
            height: 6px;
        }}
        QScrollBar::handle:horizontal {{
            background: #C8C5BC;
            border-radius: 3px;
        }}
        QScrollBar::add-line:horizontal,
        QScrollBar::sub-line:horizontal {{ width: 0px; }}
    """


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Finance Tracker")
        self.setMinimumSize(1280, 780)
        self.current_month_id = None
        self.months_data      = []
        self._theme           = settings.get("theme") or "light"

        init_db()
        self._build_ui()
        self._apply_theme()
        self._load_months()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ── Sidebar ───────────────────────────────────────────────
        sidebar = QFrame()
        sidebar.setFixedWidth(230)
        sidebar.setObjectName("sidebar")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(16, 20, 16, 20)
        sidebar_layout.setSpacing(4)

        title_widget = QWidget()
        title_layout = QHBoxLayout(title_widget)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(8)

        emoji_lbl = QLabel("🌿")
        emoji_lbl.setStyleSheet(
            "font-size: 20px; background: transparent;"
        )
        title_lbl = QLabel("Finance Tracker")
        title_lbl.setObjectName("appTitle")

        title_layout.addWidget(emoji_lbl)
        title_layout.addWidget(title_lbl)
        title_layout.addStretch()
        sidebar_layout.addWidget(title_widget)
        sidebar_layout.addSpacing(8)

        import_btn = QPushButton("＋  Import Month")
        import_btn.setObjectName("importBtn")
        import_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        import_btn.setFixedHeight(42)
        import_btn.clicked.connect(self._on_import)
        sidebar_layout.addWidget(import_btn)

        months_label = QLabel("MONTHS")
        months_label.setObjectName("sectionLabel")
        sidebar_layout.addWidget(months_label)

        self.month_list = QListWidget()
        self.month_list.setObjectName("monthList")
        self.month_list.currentRowChanged.connect(self._on_month_selected)
        self.month_list.setSpacing(2)
        sidebar_layout.addWidget(self.month_list)

        version_lbl = QLabel("v1.0  •  Local & Private")
        version_lbl.setStyleSheet(
            f"color: {SIDEBAR_MUTED}; font-size: 10px; "
            "background: transparent; padding-top: 8px;"
        )
        version_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(version_lbl)

        root_layout.addWidget(sidebar)

        # ── Main content ──────────────────────────────────────────
        content_area = QWidget()
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)

        self.dashboard_tab    = DashboardTab()
        self.transactions_tab = TransactionsTab()
        self.compare_tab      = CompareTab()
        self.chat_tab         = ChatTab()
        self.settings_tab     = SettingsTab()
        self.lm_guide_tab     = LMStudioGuideTab()


        self.tabs.addTab(self.dashboard_tab,    "  Dashboard  ")
        self.tabs.addTab(self.transactions_tab, "  Transactions  ")
        self.tabs.addTab(self.compare_tab,      "  Compare  ")
        self.tabs.addTab(self.chat_tab,         "  AI Chat  ")
        self.tabs.addTab(self.settings_tab,     "  Settings  ")
        self.tabs.addTab(self.lm_guide_tab,     "LM Studio Guide") 

        self.tabs.currentChanged.connect(self._on_tab_changed)

        # wire settings signals
        self.settings_tab.settings_changed.connect(self._on_settings_changed)
        self.settings_tab.month_deleted.connect(self._on_month_deleted)

        content_layout.addWidget(self.tabs)
        root_layout.addWidget(content_area)

    def _apply_theme(self):
        self.setStyleSheet(get_app_style(self._theme))

    def _load_months(self):
        self.month_list.clear()
        self.months_data = get_all_months()
        for m in self.months_data:
            self.month_list.addItem(f"  {m['label']}")
        if self.months_data:
            self.month_list.setCurrentRow(0)
        self.chat_tab.refresh_months()
        self.settings_tab.refresh_months()

    def _on_tab_changed(self, index):
        if index == 2:
            self.compare_tab.refresh()
        elif index == 3:
            self.chat_tab.refresh_months()
        elif index == 4:
            self.settings_tab.refresh_months()

    def _on_month_selected(self, row):
        if row < 0 or row >= len(self.months_data):
            return
        month = self.months_data[row]
        self.current_month_id = month["id"]
        self.dashboard_tab.load(self.current_month_id)
        self.transactions_tab.load(self.current_month_id)
        if self.tabs.currentIndex() == 2:
            self.compare_tab.refresh()

    def _on_settings_changed(self, s: dict):
        # update model name in chat tab
        self.chat_tab.model_input.setText(s.get("model_name", ""))
        # apply theme if changed
        new_theme = s.get("theme", "light")
        if new_theme != self._theme:
            self._theme = new_theme
            self._apply_theme()

    def _on_month_deleted(self):
        self._load_months()
        self.compare_tab.refresh()
        self.chat_tab.refresh_months()

    def _on_import(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Transaction JSON", "", "JSON Files (*.json)"
        )
        if not file_path:
            return

        result = import_json(file_path)

        if result["success"]:
            s = result["summary"]
            QMessageBox.information(
                self, "Import Successful",
                f"✅  {result['message']}\n\n"
                f"Income :   ₹{s['total_income']:,.2f}\n"
                f"Expense:   ₹{s['total_expense']:,.2f}\n"
                f"Savings:   ₹{s['net_savings']:,.2f}"
            )
            self._load_months()
            self.compare_tab.refresh()
            self.chat_tab.refresh_months()
            self.settings_tab.refresh_months()
        else:
            QMessageBox.warning(self, "Import Failed", result["message"])