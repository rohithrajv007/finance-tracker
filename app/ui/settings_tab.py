from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QScrollArea,
    QComboBox, QMessageBox, QSizePolicy,
    QGraphicsDropShadowEffect, QListWidget,
    QListWidgetItem
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont

import app.settings as settings
from app.db.database import get_all_months, get_connection
from app.ai.embedder import delete_month_embeddings

BG     = "#F7F6F2"
CARD   = "#FFFFFF"
GREEN  = "#4A9B6F"
BLUE   = "#5B8DB8"
AMBER  = "#C4883A"
RED    = "#C4554A"
TEXT   = "#2D2D2A"
MUTED  = "#8A8A82"
BORDER = "#E8E6E0"


def _shadow(widget, blur=14, offset=2, opacity=0.07):
    fx = QGraphicsDropShadowEffect()
    fx.setBlurRadius(blur)
    fx.setOffset(0, offset)
    fx.setColor(QColor(0, 0, 0, int(255 * opacity)))
    widget.setGraphicsEffect(fx)
    return widget


def section_card(title: str) -> tuple:
    """Returns (card_frame, content_layout)"""
    card = QFrame()
    card.setStyleSheet(f"""
        QFrame {{
            background: {CARD};
            border-radius: 14px;
            border: 1px solid {BORDER};
        }}
    """)
    _shadow(card)

    outer = QVBoxLayout(card)
    outer.setContentsMargins(24, 20, 24, 20)
    outer.setSpacing(16)

    title_lbl = QLabel(title)
    title_lbl.setStyleSheet(
        f"color: {TEXT}; font-size: 14px; font-weight: 600; "
        "font-family: 'Segoe UI Semibold', 'Segoe UI'; "
        "background: transparent; border: none;"
    )
    outer.addWidget(title_lbl)

    divider = QFrame()
    divider.setFixedHeight(1)
    divider.setStyleSheet(f"background: {BORDER}; border: none;")
    outer.addWidget(divider)

    return card, outer


def input_row(label: str, placeholder: str,
              value: str = "", password: bool = False) -> tuple:
    """Returns (row_widget, QLineEdit)"""
    row = QWidget()
    row.setStyleSheet("background: transparent; border: none;")
    layout = QHBoxLayout(row)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(16)

    lbl = QLabel(label)
    lbl.setFixedWidth(160)
    lbl.setStyleSheet(
        f"color: {TEXT}; font-size: 13px; "
        "font-family: 'Segoe UI'; background: transparent; border: none;"
    )

    edit = QLineEdit()
    edit.setPlaceholderText(placeholder)
    edit.setText(value)
    edit.setFixedHeight(38)
    if password:
        edit.setEchoMode(QLineEdit.EchoMode.Password)
    edit.setStyleSheet(f"""
        QLineEdit {{
            border: 1.5px solid {BORDER};
            border-radius: 8px;
            padding: 6px 14px;
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

    layout.addWidget(lbl)
    layout.addWidget(edit)
    return row, edit


class SettingsTab(QWidget):
    # emitted when settings that affect other tabs change
    settings_changed = pyqtSignal(dict)
    month_deleted    = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"background: {BG};")
        self._build_ui()
        self._load_settings()

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
        title_row = QHBoxLayout()
        page_title = QLabel("Settings")
        page_title.setStyleSheet(
            f"color: {TEXT}; font-size: 22px; font-weight: 600; "
            "font-family: 'Segoe UI Semibold', 'Segoe UI'; "
            "background: transparent;"
        )
        title_row.addWidget(page_title)
        title_row.addStretch()
        self.main_layout.addLayout(title_row)

        # ── AI Configuration ──────────────────────────────────────
        ai_card, ai_layout = section_card("🤖  AI Configuration")

        url_row, self.url_edit = input_row(
            "LM Studio URL",
            "http://localhost:1234",
            settings.get("lm_studio_url")
        )
        model_row, self.model_edit = input_row(
            "Model Name",
            "phi-3-mini-4k-instruct",
            settings.get("model_name")
        )

        # test connection button
        test_row = QWidget()
        test_row.setStyleSheet("background: transparent; border: none;")
        test_layout = QHBoxLayout(test_row)
        test_layout.setContentsMargins(0, 0, 0, 0)
        test_layout.setSpacing(12)

        self.test_btn = QPushButton("Test Connection")
        self.test_btn.setFixedHeight(38)
        self.test_btn.setFixedWidth(160)
        self.test_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.test_btn.setStyleSheet(f"""
            QPushButton {{
                background: {BLUE};
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-family: 'Segoe UI', sans-serif;
            }}
            QPushButton:hover {{ background: #4A7BA8; }}
        """)
        self.test_btn.clicked.connect(self._test_connection)

        self.connection_status = QLabel("")
        self.connection_status.setStyleSheet(
            f"color: {MUTED}; font-size: 12px; "
            "background: transparent; border: none;"
        )

        test_layout.addWidget(self.test_btn)
        test_layout.addWidget(self.connection_status)
        test_layout.addStretch()

        ai_layout.addWidget(url_row)
        ai_layout.addWidget(model_row)
        ai_layout.addWidget(test_row)
        self.main_layout.addWidget(ai_card)

        # ── Appearance ────────────────────────────────────────────
        appear_card, appear_layout = section_card("🎨  Appearance")

        theme_row = QWidget()
        theme_row.setStyleSheet("background: transparent; border: none;")
        theme_layout = QHBoxLayout(theme_row)
        theme_layout.setContentsMargins(0, 0, 0, 0)
        theme_layout.setSpacing(16)

        theme_lbl = QLabel("Theme")
        theme_lbl.setFixedWidth(160)
        theme_lbl.setStyleSheet(
            f"color: {TEXT}; font-size: 13px; "
            "font-family: 'Segoe UI'; background: transparent; border: none;"
        )

        self.theme_combo = QComboBox()
        self.theme_combo.setFixedHeight(38)
        self.theme_combo.setFixedWidth(180)
        self.theme_combo.addItems(["Light", "Dark"])
        self.theme_combo.setStyleSheet(f"""
            QComboBox {{
                border: 1.5px solid {BORDER};
                border-radius: 8px;
                padding: 6px 14px;
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
                selection-background-color: {GREEN};
                selection-color: white;
                border: 1px solid {BORDER};
            }}
        """)

        theme_note = QLabel(
            "Dark theme restarts the app to apply fully."
        )
        theme_note.setStyleSheet(
            f"color: {MUTED}; font-size: 11px; "
            "background: transparent; border: none;"
        )

        theme_layout.addWidget(theme_lbl)
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addWidget(theme_note)
        theme_layout.addStretch()

        appear_layout.addWidget(theme_row)
        self.main_layout.addWidget(appear_card)

        # ── Data Management ───────────────────────────────────────
        data_card, data_layout = section_card("🗄️  Data Management")

        del_lbl = QLabel("Select a month to delete:")
        del_lbl.setStyleSheet(
            f"color: {TEXT}; font-size: 13px; "
            "font-family: 'Segoe UI'; background: transparent; border: none;"
        )

        self.month_list = QListWidget()
        self.month_list.setFixedHeight(140)
        self.month_list.setStyleSheet(f"""
            QListWidget {{
                border: 1.5px solid {BORDER};
                border-radius: 8px;
                background: #FAFAF8;
                font-size: 13px;
                font-family: 'Segoe UI', sans-serif;
                color: {TEXT};
                outline: none;
            }}
            QListWidget::item {{
                padding: 8px 14px;
                border-radius: 6px;
            }}
            QListWidget::item:selected {{
                background: #FFF0F0;
                color: {RED};
            }}
            QListWidget::item:hover:!selected {{
                background: #F5F4F0;
            }}
        """)

        del_btn_row = QHBoxLayout()
        del_btn_row.setSpacing(12)

        self.del_btn = QPushButton("🗑  Delete Selected Month")
        self.del_btn.setFixedHeight(38)
        self.del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.del_btn.setStyleSheet(f"""
            QPushButton {{
                background: #FFF0F0;
                color: {RED};
                border: 1.5px solid {RED};
                border-radius: 8px;
                font-size: 13px;
                font-family: 'Segoe UI', sans-serif;
                padding: 0 20px;
            }}
            QPushButton:hover {{
                background: {RED};
                color: white;
            }}
            QPushButton:disabled {{
                background: #F5F4F0;
                color: {MUTED};
                border: 1.5px solid {BORDER};
            }}
        """)
        self.del_btn.clicked.connect(self._delete_month)

        self.del_status = QLabel("")
        self.del_status.setStyleSheet(
            f"color: {MUTED}; font-size: 12px; "
            "background: transparent; border: none;"
        )

        del_btn_row.addWidget(self.del_btn)
        del_btn_row.addWidget(self.del_status)
        del_btn_row.addStretch()

        data_layout.addWidget(del_lbl)
        data_layout.addWidget(self.month_list)
        data_layout.addLayout(del_btn_row)
        self.main_layout.addWidget(data_card)

        # ── About ─────────────────────────────────────────────────
        about_card, about_layout = section_card("ℹ️  About")

        about_text = QLabel(
            "Finance Tracker v1.0\n"
            "A fully local, private personal finance app.\n"
            "No internet required. All data stays on your device.\n\n"
            "Built with PyQt6 · SQLite · sentence-transformers · LM Studio"
        )
        about_text.setStyleSheet(
            f"color: {MUTED}; font-size: 12px; line-height: 1.6; "
            "font-family: 'Segoe UI'; background: transparent; border: none;"
        )
        about_layout.addWidget(about_text)
        self.main_layout.addWidget(about_card)

        # ── Save button ───────────────────────────────────────────
        save_row = QHBoxLayout()
        save_row.addStretch()

        self.save_btn = QPushButton("Save Settings")
        self.save_btn.setFixedHeight(44)
        self.save_btn.setFixedWidth(160)
        self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_btn.setStyleSheet(f"""
            QPushButton {{
                background: {GREEN};
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 14px;
                font-family: 'Segoe UI Semibold', 'Segoe UI';
                font-weight: 600;
            }}
            QPushButton:hover {{ background: #3D8A5E; }}
            QPushButton:pressed {{ background: #357A54; }}
        """)
        self.save_btn.clicked.connect(self._save_settings)

        self.save_status = QLabel("")
        self.save_status.setStyleSheet(
            f"color: {GREEN}; font-size: 12px; "
            "background: transparent; border: none;"
        )

        save_row.addWidget(self.save_status)
        save_row.addWidget(self.save_btn)
        self.main_layout.addLayout(save_row)
        self.main_layout.addStretch()

    # ── public ────────────────────────────────────────────────────
    def refresh_months(self):
        self.month_list.clear()
        months = get_all_months()
        for m in months:
            item = QListWidgetItem(f"  {m['label']}")
            item.setData(Qt.ItemDataRole.UserRole, m["id"])
            self.month_list.addItem(item)

    # ── private ───────────────────────────────────────────────────
    def _load_settings(self):
        s = settings.load()
        self.url_edit.setText(s.get("lm_studio_url", "http://localhost:1234"))
        self.model_edit.setText(s.get("model_name", "phi-3-mini-4k-instruct"))
        theme = s.get("theme", "light")
        self.theme_combo.setCurrentText("Dark" if theme == "dark" else "Light")
        self.refresh_months()

    def _save_settings(self):
        s = {
            "lm_studio_url": self.url_edit.text().strip(),
            "model_name":    self.model_edit.text().strip(),
            "theme":         self.theme_combo.currentText().lower(),
        }
        settings.save(s)
        self.save_status.setText("✓  Saved!")
        self.save_status.setStyleSheet(
            f"color: {GREEN}; font-size: 12px; "
            "background: transparent; border: none;"
        )
        QTimer_clear = lambda: self.save_status.setText("")
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(3000, QTimer_clear)
        self.settings_changed.emit(s)

    def _test_connection(self):
        import requests
        url = self.url_edit.text().strip()
        self.connection_status.setText("Testing...")
        self.connection_status.setStyleSheet(
            f"color: {MUTED}; font-size: 12px; "
            "background: transparent; border: none;"
        )
        try:
            resp = requests.get(f"{url}/v1/models", timeout=5)
            models = resp.json().get("data", [])
            names  = [m["id"] for m in models]
            self.connection_status.setText(
                f"✓  Connected — models: {', '.join(names)}"
            )
            self.connection_status.setStyleSheet(
                f"color: {GREEN}; font-size: 12px; "
                "background: transparent; border: none;"
            )
        except Exception as e:
            self.connection_status.setText(f"✗  Failed: {str(e)[:60]}")
            self.connection_status.setStyleSheet(
                f"color: {RED}; font-size: 12px; "
                "background: transparent; border: none;"
            )

    def _delete_month(self):
        item = self.month_list.currentItem()
        if not item:
            self.del_status.setText("Select a month first.")
            return

        label     = item.text().strip()
        month_id  = item.data(Qt.ItemDataRole.UserRole)

        reply = QMessageBox.question(
            self,
            "Delete Month",
            f"Permanently delete all data for '{label}'?\n\n"
            "This will remove all transactions and AI embeddings "
            "for this month. This cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            # delete embeddings
            delete_month_embeddings(month_id)

            # delete from DB
            conn = get_connection()
            conn.execute(
                "DELETE FROM transactions WHERE month_id = ?", (month_id,)
            )
            conn.execute(
                "DELETE FROM months WHERE id = ?", (month_id,)
            )
            conn.commit()
            conn.close()

            self.del_status.setText(f"✓  '{label}' deleted.")
            self.del_status.setStyleSheet(
                f"color: {GREEN}; font-size: 12px; "
                "background: transparent; border: none;"
            )
            self.refresh_months()
            self.month_deleted.emit()

        except Exception as e:
            self.del_status.setText(f"✗  Error: {str(e)[:60]}")
            self.del_status.setStyleSheet(
                f"color: {RED}; font-size: 12px; "
                "background: transparent; border: none;"
            )