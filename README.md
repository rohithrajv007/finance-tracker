# 🌿 Finance Tracker

A fully **local**, **private** personal finance desktop application built with Python and PyQt6.
No internet required. All your data stays on your device.

![Python](https://img.shields.io/badge/Python-3.10-blue)
![PyQt6](https://img.shields.io/badge/PyQt6-6.x-green)
![License](https://img.shields.io/badge/license-MIT-brightgreen)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)

---

## ✨ Features

- **📊 Dashboard** — KPI cards, category pie chart, daily spend, balance trend, top payees
- **📋 Transactions** — searchable, filterable transaction table with debit/credit coloring
- **📈 Compare** — month-over-month comparison with charts and category diff table
- **🤖 AI Chat** — local RAG chatbot powered by LM Studio, answers questions about your spending
- **⚙️ Settings** — save LM Studio config, toggle light/dark theme, delete months
- **100% Offline** — no cloud, no subscriptions, no data sharing

---

## 🖥️ Screenshots

> Dashboard, Transactions, Compare, AI Chat tabs

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| UI Framework | PyQt6 |
| Database | SQLite |
| Charts | Matplotlib |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| Vector Search | NumPy cosine similarity |
| Local LLM | LM Studio (phi-3-mini-4k-instruct) |
| Packaging | PyInstaller |

---

## 📋 Requirements

- Windows 10/11 (64-bit)
- Python 3.10.x
- [LM Studio](https://lmstudio.ai) with a model loaded and server running

---

## 🚀 Installation

### Option A — Run from source

**1. Clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/finance-tracker.git
cd finance-tracker
```

**2. Create virtual environment**
```bash
py -3.10 -m venv venv
venv\Scripts\activate
```

**3. Install dependencies**
```bash
pip install PyQt6 matplotlib sqlalchemy
pip install torch==2.3.0+cpu --index-url https://download.pytorch.org/whl/cpu
pip install numpy==1.26.4
pip install sentence-transformers==3.0.0
pip install transformers==4.40.0
pip install requests pillow
```

**4. Run the app**
```bash
python main.py
```

### Option B — Download .exe

Download the latest release from the
[Releases](https://github.com/YOUR_USERNAME/finance-tracker/releases) page.
Extract the zip and double click `FinanceTracker.exe`.

> If Windows blocks the file: right click → Properties → check Unblock → OK

---

## 📥 How to Use

### 1. Import your transactions
- Export your bank statement as JSON (using the categorization script)
- Click **＋ Import Month** in the sidebar
- Select your JSON file

### JSON format expected
```json
[
  {
    "date": "01-09-2025",
    "year": "2025",
    "description": "UPI/DR/...",
    "mode_of_transaction": "UPI",
    "paid_to": "UPI DR EXAMPLE",
    "debit": 500.0,
    "credit": 0.0,
    "balance": 5000.0,
    "category": "Food & Dining"
  }
]
```

### 2. View your dashboard
Click any month in the sidebar to load charts and KPIs.

### 3. Use AI Chat
- Open **LM Studio** → load a model → start local server
- Go to **AI Chat** tab → select month → type your question

**Example questions:**
```
How much did I spend on entertainment?
Which category cost me the most?
What was my closing balance?
How much did I receive this month?
```

---

## 🤖 AI Setup (LM Studio)

1. Download [LM Studio](https://lmstudio.ai)
2. Search and download `phi-3-mini-4k-instruct` (Q4_K_M, ~2.4GB)
3. Go to **Local Server** tab → load model → click **Start Server**
4. Server runs at `http://localhost:1234`
5. In Finance Tracker Settings → set model name to `phi-3-mini-4k-instruct`

**Recommended models by RAM:**

| RAM | Model |
|---|---|
| 4GB | phi-3-mini-4k-instruct |
| 8GB | Qwen3 4B or Mistral 7B |
| 16GB | Gemma 3 12B |

---

## 📁 Project Structure
```
finance_tracker/
├── app/
│   ├── ai/
│   │   ├── embedder.py       # numpy vector store
│   │   └── rag_engine.py     # LM Studio RAG pipeline
│   ├── db/
│   │   ├── database.py       # SQLite queries
│   │   └── importer.py       # JSON import pipeline
│   └── ui/
│       ├── main_window.py    # main app window
│       ├── dashboard_tab.py  # charts and KPIs
│       ├── transactions_tab.py
│       ├── compare_tab.py
│       ├── chat_tab.py       # AI chat UI
│       └── settings_tab.py
├── assets/
│   └── icon.ico
├── data/                     # created at runtime
│   ├── finance.db
│   ├── settings.json
│   └── vectors/
├── main.py
├── requirements.txt
├── finance_tracker.spec
└── README.md
```

---

## 🔒 Privacy

- All data stored locally in `data/finance.db`
- Embeddings stored locally in `data/vectors/`
- LM Studio runs 100% offline on your machine
- Zero telemetry, zero cloud sync, zero ads

---

## 📝 License

MIT License — free to use, modify, and distribute.

---

## 🙏 Acknowledgements

- [PyQt6](https://pypi.org/project/PyQt6/)
- [LM Studio](https://lmstudio.ai)
- [sentence-transformers](https://www.sbert.net/)
- [Matplotlib](https://matplotlib.org/)
