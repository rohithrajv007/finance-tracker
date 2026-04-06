from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton, QScrollArea
)
from PyQt6.QtCore import Qt


class LMStudioGuideTab(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        # Title
        title = QLabel("LM Studio Setup Guide")
        title.setStyleSheet("font-size: 22px; font-weight: bold;")
        layout.addWidget(title)

        # Scroll area (important for long content)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        content_widget = QWidget()
        content_layout = QVBoxLayout()

        # Guide Text
        guide_text = QTextEdit()
        guide_text.setReadOnly(True)

        guide_text.setText("""
STEP 1: Download LM Studio
-----------------------------------
1. Go to: https://lmstudio.ai
2. Click "Download for Windows"
3. Install the application

STEP 2: Open LM Studio
-----------------------------------
1. Launch LM Studio after installation

STEP 3: Download AI Model
-----------------------------------
1. Click Search (🔍 icon)
2. Search: phi-3-mini-4k-instruct
3. Download Q4_K_M version (~2.4GB)

STEP 4: Start Local Server
-----------------------------------
1. Go to "Local Server" tab
2. Select the downloaded model
3. Click "Start Server"

Server URL:
http://localhost:1234

STEP 5: Connect to This App
-----------------------------------
1. Open Settings tab
2. Enter:
   URL: http://localhost:1234
   Model: phi-3-mini-4k-instruct
3. Click "Test Connection"

DONE ✅

Notes:
- Keep LM Studio running while using AI Chat
- First response may take 20–40 seconds
        """)

        content_layout.addWidget(guide_text)

        content_widget.setLayout(content_layout)
        scroll.setWidget(content_widget)

        layout.addWidget(scroll)

        self.setLayout(layout)