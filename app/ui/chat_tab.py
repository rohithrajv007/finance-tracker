from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel,
    QComboBox, QFrame, QScrollArea, QSizePolicy,
    QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QColor

from app.db.database import get_all_months, save_chat_message
from app.ai.rag_engine import build_context

BG     = "#F7F6F2"
CARD   = "#FFFFFF"
GREEN  = "#4A9B6F"
BLUE   = "#5B8DB8"
AMBER  = "#C4883A"
RED    = "#C4554A"
TEXT   = "#2D2D2A"
MUTED  = "#8A8A82"
BORDER = "#E8E6E0"
SIDEBAR= "#2C3E35"

USER_BUBBLE  = "#2C3E35"
AI_BUBBLE    = "#FFFFFF"
CHAT_BG      = "#F0F4F1"


class ModelPreloadWorker(QThread):
    def run(self):
        try:
            from app.ai.embedder import _get_model
            _get_model()
        except Exception as e:
            print(f"Preload warning: {e}")


class LLMWorker(QThread):
    response_ready = pyqtSignal(str)
    finished       = pyqtSignal()

    def __init__(self, question, context, model_name):
        super().__init__()
        self.question   = question
        self.context    = context
        self.model_name = model_name

    def run(self):
        try:
            import requests
            SYSTEM_PROMPT = """You are a personal finance assistant.
Analyze the provided transaction context and answer clearly.
Rules:
- Use Indian Rupees (₹) always
- Calculate totals accurately from the context
- Be concise and specific
- Never make up data not in the context
- Use pre-calculated category totals when available
"""
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": f"Context:\n{self.context}\n\nQuestion: {self.question}"},
            ]
            payload = {
                "model":       self.model_name,
                "messages":    messages,
                "temperature": 0.3,
                "max_tokens":  512,
                "stream":      False,
            }
            resp = requests.post(
                "http://localhost:1234/v1/chat/completions",
                json=payload,
                timeout=120
            )
            resp.raise_for_status()
            answer = resp.json()["choices"][0]["message"]["content"]
            self.response_ready.emit(answer)

        except requests.exceptions.ConnectionError:
            self.response_ready.emit(
                "⚠️ Cannot connect to LM Studio.\n\n"
                "Please make sure:\n"
                "1. LM Studio is open\n"
                "2. A model is loaded\n"
                "3. Local server is started"
            )
        except requests.exceptions.Timeout:
            self.response_ready.emit(
                "⚠️ Request timed out. Try again in a moment."
            )
        except Exception as e:
            self.response_ready.emit(f"⚠️ Error: {str(e)}")
        finally:
            self.finished.emit()


class MessageBubble(QFrame):
    def __init__(self, text: str, is_user: bool):
        super().__init__()
        self.is_user = is_user
        self._setup(text)

    def _setup(self, text: str):
        if self.is_user:
            self.setStyleSheet(f"""
                QFrame {{
                    background: {USER_BUBBLE};
                    border-radius: 16px 16px 4px 16px;
                    border: none;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QFrame {{
                    background: {AI_BUBBLE};
                    border-radius: 16px 16px 16px 4px;
                    border: 1px solid {BORDER};
                }}
            """)
            fx = QGraphicsDropShadowEffect()
            fx.setBlurRadius(10)
            fx.setOffset(0, 2)
            fx.setColor(QColor(0, 0, 0, 12))
            self.setGraphicsEffect(fx)

        self.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Minimum
        )
        self.setMaximumWidth(680)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(0)

        self.label = QLabel(text)
        self.label.setWordWrap(True)
        self.label.setFont(QFont("Segoe UI", 11))
        self.label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        if self.is_user:
            self.label.setStyleSheet(
                "color: #E8F5EC; background: transparent; line-height: 1.5;"
            )
        else:
            self.label.setStyleSheet(
                f"color: {TEXT}; background: transparent; line-height: 1.5;"
            )
        layout.addWidget(self.label)

    def update_text(self, text: str):
        self.label.setText(text)


class ChatTab(QWidget):
    def __init__(self):
        super().__init__()
        self._worker        = None
        self._ai_bubble     = None
        self._full_response = ""
        self.setStyleSheet(f"background: {BG};")
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── top bar ───────────────────────────────────────────────
        top_bar = QFrame()
        top_bar.setFixedHeight(60)
        top_bar.setStyleSheet(f"""
            QFrame {{
                background: {CARD};
                border-bottom: 1px solid {BORDER};
            }}
        """)
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(24, 0, 24, 0)
        top_layout.setSpacing(14)

        lbl_month = QLabel("Month:")
        lbl_month.setStyleSheet(
            f"color: {MUTED}; font-size: 12px; "
            "font-family: 'Segoe UI'; background: transparent;"
        )

        combo_style = f"""
            QComboBox {{
                border: 1.5px solid {BORDER};
                border-radius: 8px;
                padding: 5px 14px;
                font-size: 13px;
                font-family: 'Segoe UI', sans-serif;
                color: {TEXT};
                background: #FAFAF8;
                min-width: 160px;
            }}
            QComboBox:focus {{ border: 1.5px solid {GREEN}; }}
            QComboBox::drop-down {{ border: none; width: 20px; }}
            QComboBox QAbstractItemView {{
                background: {CARD};
                color: {TEXT};
                border: 1px solid {BORDER};
                selection-background-color: {GREEN};
                selection-color: white;
            }}
        """
        self.month_combo = QComboBox()
        self.month_combo.setFixedHeight(36)
        self.month_combo.setStyleSheet(combo_style)

        lbl_model = QLabel("Model:")
        lbl_model.setStyleSheet(
            f"color: {MUTED}; font-size: 12px; "
            "font-family: 'Segoe UI'; background: transparent;"
        )

        self.model_input = QLineEdit()
        self.model_input.setFixedHeight(36)
        self.model_input.setMinimumWidth(200)
        self.model_input.setText("phi-3-mini-4k-instruct")
        self.model_input.setStyleSheet(f"""
            QLineEdit {{
                border: 1.5px solid {BORDER};
                border-radius: 8px;
                padding: 5px 14px;
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

        self.status_label = QLabel("● Ready")
        self.status_label.setStyleSheet(
            f"color: {GREEN}; font-size: 11px; "
            "font-family: 'Segoe UI'; background: transparent;"
        )

        clear_btn = QPushButton("Clear")
        clear_btn.setFixedHeight(34)
        clear_btn.setFixedWidth(70)
        clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        clear_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: 1.5px solid {BORDER};
                border-radius: 8px;
                font-size: 12px;
                font-family: 'Segoe UI', sans-serif;
                color: {MUTED};
            }}
            QPushButton:hover {{
                background: #FFF0F0;
                border: 1.5px solid {RED};
                color: {RED};
            }}
        """)
        clear_btn.clicked.connect(self._clear_chat)

        top_layout.addWidget(lbl_month)
        top_layout.addWidget(self.month_combo)
        top_layout.addSpacing(10)
        top_layout.addWidget(lbl_model)
        top_layout.addWidget(self.model_input)
        top_layout.addSpacing(6)
        top_layout.addWidget(self.status_label)
        top_layout.addStretch()
        top_layout.addWidget(clear_btn)
        layout.addWidget(top_bar)

        # ── chat area ─────────────────────────────────────────────
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background: {CHAT_BG};
            }}
            QScrollBar:vertical {{
                background: transparent;
                width: 6px;
            }}
            QScrollBar::handle:vertical {{
                background: #C0C8C2;
                border-radius: 3px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: #A0A8A2;
            }}
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{ height: 0px; }}
        """)

        self.messages_widget = QWidget()
        self.messages_widget.setStyleSheet(f"background: {CHAT_BG};")

        self.messages_layout = QVBoxLayout(self.messages_widget)
        self.messages_layout.setContentsMargins(28, 24, 28, 24)
        self.messages_layout.setSpacing(14)
        self.messages_layout.addStretch()

        self.scroll_area.setWidget(self.messages_widget)
        layout.addWidget(self.scroll_area, stretch=1)

        # welcome
        self._add_ai_message(
            "👋  Hello! I'm your Finance Assistant.\n\n"
            "Ask me anything about your transactions:\n"
            "  •  How much did I spend on entertainment?\n"
            "  •  What are my top expenses?\n"
            "  •  How much did I receive this month?\n"
            "  •  Which category cost me the most?\n\n"
            "Select a month above, then ask away."
        )

        # ── input bar ─────────────────────────────────────────────
        input_frame = QFrame()
        input_frame.setFixedHeight(72)
        input_frame.setStyleSheet(f"""
            QFrame {{
                background: {CARD};
                border-top: 1px solid {BORDER};
            }}
        """)
        input_layout = QHBoxLayout(input_frame)
        input_layout.setContentsMargins(24, 14, 24, 14)
        input_layout.setSpacing(12)

        self.input_box = QLineEdit()
        self.input_box.setFixedHeight(44)
        self.input_box.setPlaceholderText(
            "Ask anything about your transactions..."
        )
        self.input_box.setStyleSheet(f"""
            QLineEdit {{
                border: 1.5px solid {BORDER};
                border-radius: 22px;
                padding: 8px 22px;
                font-size: 13px;
                font-family: 'Segoe UI', sans-serif;
                color: {TEXT};
                background: {CHAT_BG};
            }}
            QLineEdit:focus {{
                border: 1.5px solid {GREEN};
                background: {CARD};
            }}
        """)
        self.input_box.returnPressed.connect(self._on_send)

        self.send_btn = QPushButton("Send  →")
        self.send_btn.setFixedSize(100, 44)
        self.send_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.send_btn.setStyleSheet(f"""
            QPushButton {{
                background: {GREEN};
                color: #FFFFFF;
                border: none;
                border-radius: 22px;
                font-size: 13px;
                font-family: 'Segoe UI Semibold', 'Segoe UI';
                font-weight: 600;
            }}
            QPushButton:hover {{ background: #3D8A5E; }}
            QPushButton:pressed {{ background: #357A54; }}
            QPushButton:disabled {{
                background: {BORDER};
                color: {MUTED};
            }}
        """)
        self.send_btn.clicked.connect(self._on_send)

        input_layout.addWidget(self.input_box)
        input_layout.addWidget(self.send_btn)
        layout.addWidget(input_frame)

        # preload
        self._preload_worker = ModelPreloadWorker()
        self._preload_worker.start()

    def refresh_months(self):
        months = get_all_months()
        self.month_combo.blockSignals(True)
        self.month_combo.clear()
        self.month_combo.addItem("All months", userData=None)
        for m in months:
            self.month_combo.addItem(m["label"], userData=m["id"])
        self.month_combo.blockSignals(False)

    def _selected_month_id(self):
        idx = self.month_combo.currentIndex()
        if idx <= 0:
            return None
        return self.month_combo.itemData(idx)

    def _add_user_message(self, text: str):
        bubble = MessageBubble(text, is_user=True)
        row = QHBoxLayout()
        row.addStretch()
        row.addWidget(bubble)
        self.messages_layout.insertLayout(
            self.messages_layout.count() - 1, row
        )
        self._scroll_to_bottom()

    def _add_ai_message(self, text: str = ""):
        bubble = MessageBubble(text, is_user=False)
        row = QHBoxLayout()
        row.addWidget(bubble)
        row.addStretch()
        self.messages_layout.insertLayout(
            self.messages_layout.count() - 1, row
        )
        self._ai_bubble = bubble
        self._scroll_to_bottom()
        return bubble

    def _scroll_to_bottom(self):
        QTimer.singleShot(
            60,
            lambda: self.scroll_area.verticalScrollBar().setValue(
                self.scroll_area.verticalScrollBar().maximum()
            )
        )

    def _clear_chat(self):
        while self.messages_layout.count() > 1:
            item = self.messages_layout.takeAt(0)
            if item.layout():
                while item.layout().count():
                    w = item.layout().takeAt(0)
                    if w.widget():
                        w.widget().deleteLater()
            elif item.widget():
                item.widget().deleteLater()
        self._add_ai_message(
            "Chat cleared. Ask me anything about your transactions!"
        )

    def _on_send(self):
        question = self.input_box.text().strip()
        if not question:
            return
        if self._worker and self._worker.isRunning():
            return

        self.input_box.clear()
        self.send_btn.setEnabled(False)
        self.send_btn.setText("...")
        self._set_status("● Searching...", AMBER)
        self._full_response = ""

        self._add_user_message(question)
        save_chat_message("user", question)

        month_id = self._selected_month_id()
        try:
            context = build_context(question, month_id)
        except Exception as e:
            self._add_ai_message(f"⚠️ Search error: {str(e)}")
            self._reset_input()
            return

        self._set_status("● Thinking...", BLUE)
        self._add_ai_message("⏳  Thinking... (20–40 seconds on CPU)")

        model_name = self.model_input.text().strip() or "phi-3-mini-4k-instruct"

        self._worker = LLMWorker(question, context, model_name)
        self._worker.response_ready.connect(self._on_response)
        self._worker.finished.connect(self._on_finished)
        self._worker.start()

    def _on_response(self, response: str):
        self._full_response = response
        if self._ai_bubble:
            self._ai_bubble.update_text(self._full_response)
        save_chat_message("assistant", self._full_response)
        self._scroll_to_bottom()

    def _on_finished(self):
        self._reset_input()
        self._set_status("● Ready", GREEN)

    def _reset_input(self):
        self.send_btn.setEnabled(True)
        self.send_btn.setText("Send  →")
        self.input_box.setFocus()
        self._scroll_to_bottom()

    def _set_status(self, text: str, color: str):
        self.status_label.setText(text)
        self.status_label.setStyleSheet(
            f"color: {color}; font-size: 11px; "
            "font-family: 'Segoe UI'; background: transparent;"
        )