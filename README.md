<<<<<<< HEAD
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
=======
# 🌿 Finance Tracker

A fully **local**, **private** personal finance desktop application built with Python and PyQt6.
No internet required after setup. All your data stays on your device forever.

![Python](https://img.shields.io/badge/Python-3.10-blue)
![PyQt6](https://img.shields.io/badge/PyQt6-6.x-green)
![License](https://img.shields.io/badge/license-MIT-brightgreen)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)
![AI](https://img.shields.io/badge/AI-Local%20LLM-orange)

---

## ✨ Features

- **📊 Dashboard** — KPI cards, category pie chart, daily spend, balance trend, top payees
- **📋 Transactions** — searchable, filterable transaction table with debit/credit coloring
- **📈 Compare** — month-over-month comparison with charts and category diff table
- **🤖 AI Chat** — local RAG chatbot powered by LM Studio, answers questions about your spending
- **⚙️ Settings** — save LM Studio config, toggle light/dark theme, delete months
- **🔒 100% Offline** — no cloud, no subscriptions, no data sharing ever

---

## 🖥️ Tech Stack

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

## 📋 System Requirements

- **OS:** Windows 10 or Windows 11 (64-bit)
- **RAM:** Minimum 8GB (16GB recommended for larger AI models)
- **Storage:** ~5GB free space (for model + app + data)
- **Python:** 3.10.x (specific version required)
- **Internet:** Only needed for initial installation and model download

---

## 🚀 Complete Installation Guide

Follow every step in order. Do not skip any step.

---

### Part 1 — Install Python 3.10

> ⚠️ You must use Python 3.10 specifically. Python 3.11+ causes issues with PyTorch.

**Step 1.** Download Python 3.10.11 from the official website:
```
https://www.python.org/downloads/release/python-31011/
```

Scroll down to **Files** section → click **Windows installer (64-bit)**

**Step 2.** Run the installer:
- ✅ Check **"Add Python to PATH"** at the bottom
- Click **Install Now**
- Wait for installation to complete
- Click **Close**

**Step 3.** Verify installation — open Command Prompt and run:
```bash
py -3.10 --version
```
You should see: `Python 3.10.11`

---

### Part 2 — Install Git

**Step 1.** Download Git:
```
https://git-scm.com/download/win
```

**Step 2.** Run the installer with all default options → click **Install** → **Finish**

**Step 3.** Verify:
```bash
git --version
```
You should see: `git version 2.x.x`

---

### Part 3 — Clone the Repository

**Step 1.** Open Command Prompt and navigate to where you want the project:
```bash
cd C:\Users\YourName\Documents
```

**Step 2.** Clone the repo:
```bash
git clone https://github.com/YOUR_USERNAME/finance-tracker.git
cd finance-tracker
```

---

### Part 4 — Create Virtual Environment

**Step 1.** Create a virtual environment using Python 3.10 specifically:
```bash
py -3.10 -m venv venv
```

**Step 2.** Activate it:
```bash
venv\Scripts\activate
```

You should see `(venv)` at the start of your terminal line.

> ⚠️ You must activate the venv every time you open a new terminal before running the app.

---

### Part 5 — Install Python Dependencies

Run these commands **one by one** in order. Do not run them all at once.

**Step 1.** Core UI and database packages:
```bash
pip install PyQt6 matplotlib sqlalchemy
```

**Step 2.** NumPy (pinned version — important):
```bash
pip install numpy==1.26.4
```

**Step 3.** PyTorch CPU version (pinned version — important):
```bash
pip install torch==2.3.0+cpu --index-url https://download.pytorch.org/whl/cpu
```
> This downloads ~160MB. Wait for it to complete fully.

**Step 4.** Transformers and tokenizers:
```bash
pip install transformers==4.40.0
pip install tokenizers
```

**Step 5.** Sentence transformers (for AI embeddings):
```bash
pip install sentence-transformers==3.0.0
```

**Step 6.** Remaining packages:
```bash
pip install requests pillow filelock fsspec tqdm packaging
```

**Step 7.** Verify everything installed correctly:
```bash
python -c "import torch; from sentence_transformers import SentenceTransformer; import PyQt6; print('ALL OK')"
```
You should see: `ALL OK`

---

### Part 6 — Install LM Studio

LM Studio is the app that runs the AI model locally on your computer.

**Step 1.** Download LM Studio from the official website:
```
https://lmstudio.ai
```
Click **Download for Windows** → run the installer → follow the steps.

**Step 2.** Open LM Studio after installation.

**Step 3.** Download the AI model:
- Click the **Search** tab (🔍 magnifying glass icon on the left sidebar)
- In the search box type: `phi-3-mini-4k-instruct`
- Click the result from **Microsoft**
- On the right side click **Download** next to the `Q4_K_M` version
- Wait for the download to complete (~2.4 GB)

> 💡 **Alternative models by RAM:**
> | Your RAM | Recommended Model |
> |---|---|
> | 4GB | phi-3-mini-4k-instruct (Q4_K_M) |
> | 8GB | Mistral-7B-Instruct (Q4_K_M) |
> | 16GB+ | Gemma-3-12B (Q4_K_M) |

**Step 4.** Start the local server:
- Click the **Local Server** tab (`↔` icon on the left sidebar)
- Click **Select a model to load** dropdown
- Select the model you just downloaded
- Wait for it to say **Model Loaded**
- Click the green **Start Server** button
- You should see: `Server running on http://localhost:1234`

**Step 5.** Get your exact model name (you will need this later):
```bash
python -c "import requests; r = requests.get('http://localhost:1234/v1/models'); print([m['id'] for m in r.json()['data']])"
```
Copy the model name exactly — for example: `phi-3-mini-4k-instruct`

> ⚠️ LM Studio must be running with the server started every time you want to use the AI Chat feature. The rest of the app works without it.

---

### Part 7 — First Run Setup

**Step 1.** Make sure your venv is activated:
```bash
cd C:\Users\YourName\Documents\finance-tracker
venv\Scripts\activate
```

**Step 2.** Run the app:
```bash
python main.py
```

The app will open. On first run it will:
- Create the SQLite database at `data/finance.db`
- Create a default settings file at `data/settings.json`
- Download the embedding model (~90MB) on first AI Chat use

**Step 3.** Configure Settings:
- Click the **Settings** tab
- Set **LM Studio URL** to: `http://localhost:1234`
- Set **Model Name** to your exact model name from Step 5 above
- Click **Save Settings**
- Click **Test Connection** — should show ✓ Connected

---

### Part 8 — Import Your First Month

**Step 1.** Prepare your transaction JSON file in this format:
```json
[
  {
    "date": "01-09-2025",
    "year": "2025",
    "description": "UPI/DR/123456/EXAMPLE/Payment",
    "mode_of_transaction": "UPI",
    "paid_to": "UPI DR EXAMPLE",
    "debit": 500.0,
    "credit": 0.0,
    "balance": 5000.0,
    "category": "Food & Dining"
  },
  {
    "date": "05-09-2025",
    "year": "2025",
    "description": "UPI/CR/789012/SALARY/Credit",
    "mode_of_transaction": "UPI",
    "paid_to": "UPI CR SALARY",
    "debit": 0.0,
    "credit": 50000.0,
    "balance": 55000.0,
    "category": "Salary & Income"
  }
]
```

**Supported categories:**
- `Salary & Income`
- `Food & Dining`
- `Bills & Utilities`
- `Entertainment`
- `Shopping & E-commerce`
- `Transfer (P2P)`
- `Others`

**Step 2.** Click **＋ Import Month** in the sidebar

**Step 3.** Select your JSON file → click Open

**Step 4.** A success message shows income, expense and savings summary

**Step 5.** Click the month in the sidebar to load the dashboard

---

## 🤖 Using AI Chat

**Step 1.** Make sure LM Studio is running with server started

**Step 2.** Click **AI Chat** tab

**Step 3.** Select a month from the **Month filter** dropdown

**Step 4.** The model name is pre-filled — verify it matches your LM Studio model

**Step 5.** Type your question and press **Enter** or click **Send**

**Example questions you can ask:**
```
How much did I spend on entertainment?
Which category cost me the most?
What was my closing balance?
How much did I receive this month?
Who did I pay the most money to?
How much did I spend on food this month?
What are my top 5 expenses?
How much did I spend on bills?
```

> ⏳ Responses take 20–40 seconds on CPU. This is normal for local AI models.

---

## 📁 Project Structure
```
finance_tracker/
├── app/
│   ├── ai/
│   │   ├── embedder.py          # numpy vector store
│   │   └── rag_engine.py        # LM Studio RAG pipeline
│   ├── db/
│   │   ├── database.py          # SQLite queries
│   │   └── importer.py          # JSON import pipeline
│   ├── ui/
│   │   ├── main_window.py       # main app window
│   │   ├── dashboard_tab.py     # charts and KPIs
│   │   ├── transactions_tab.py  # transaction table
│   │   ├── compare_tab.py       # month comparison
│   │   ├── chat_tab.py          # AI chat UI
│   │   └── settings_tab.py      # settings page
│   └── settings.py              # settings manager
├── assets/
│   └── icon.ico
├── data/                        # created at runtime
│   ├── finance.db               # SQLite database
│   ├── settings.json            # saved settings
│   └── vectors/                 # AI embeddings
├── main.py                      # app entry point
├── requirements.txt
├── finance_tracker.spec         # PyInstaller config
├── CHANGELOG.md
└── README.md
```

---

## 🔧 Troubleshooting

| Problem | Solution |
|---|---|
| `py -3.10` not found | Install Python 3.10.11 from python.org |
| `torch` DLL error | Run `pip install torch==2.3.0+cpu --index-url https://download.pytorch.org/whl/cpu` |
| `numpy` version conflict | Run `pip install numpy==1.26.4` |
| AI Chat crashes | ChromaDB conflict — already fixed with numpy vector store |
| Cannot connect to LM Studio | Open LM Studio → Local Server tab → Start Server |
| App says model not found | Check exact model name with the python command in Part 6 Step 5 |
| SmartScreen blocks .exe | Right click → Properties → check Unblock → OK |
| Charts not loading | Select a month from the sidebar first |
| Re-embed after reinstall | Run `python reembed.py` |

---

## 🔒 Privacy

- ✅ All transaction data stored locally in `data/finance.db`
- ✅ All AI embeddings stored locally in `data/vectors/`
- ✅ LM Studio runs 100% offline on your machine
- ✅ Zero telemetry, zero analytics, zero cloud sync
- ✅ No account required, no login, no subscription

---

## 🏗️ Building the .exe

To build a standalone Windows executable:
```bash
venv\Scripts\activate
pyinstaller finance_tracker.spec --clean
```

Output will be in `dist\FinanceTracker\`.
Double click `FinanceTracker.exe` to run.

To share with others — zip the entire `FinanceTracker` folder:
```bash
powershell Compress-Archive -Path dist\FinanceTracker -DestinationPath FinanceTracker_v1.0.zip
```

---

## 📝 License

MIT License — free to use, modify, and distribute.

---

## 🙏 Acknowledgements

- [PyQt6](https://pypi.org/project/PyQt6/) — Desktop UI framework
- [LM Studio](https://lmstudio.ai) — Local LLM runner
- [sentence-transformers](https://www.sbert.net/) — Text embeddings
- [Matplotlib](https://matplotlib.org/) — Charts and visualizations
- [SQLite](https://www.sqlite.org/) — Local database
- [PyInstaller](https://pyinstaller.org/) — Windows packaging
>>>>>>> 4c4d3e681fe166ca2ea8f5ca5e19cfe78c896fd9
