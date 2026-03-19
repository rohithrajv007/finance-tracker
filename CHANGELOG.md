# Changelog

All notable changes to Finance Tracker are documented here.

---

## [1.0.0] - 2026-03-18

### 🎉 Initial Release

#### Added
- **Dashboard tab** with 4 KPI cards (income, expense, savings, balance)
- **Category pie chart** — spending breakdown by category
- **Daily spend bar chart** — debit per day with highest day highlighted
- **Balance trend line chart** — running balance across the month
- **Top payees chart** — horizontal bar showing who received most money
- **Transactions tab** — full searchable, filterable transaction table
- **Compare tab** — side by side month comparison with grouped bar charts
- **Category diff table** — shows ▲▼ % change per category between months
- **All months trend** — income vs expense across all imported months
- **Net savings chart** — green/red bar per month
- **AI Chat tab** — local RAG chatbot using LM Studio
- **Semantic search** — numpy cosine similarity vector store
- **Settings tab** — save LM Studio URL and model name permanently
- **Light/Dark theme toggle**
- **Delete month** — removes transactions and embeddings from DB
- **JSON importer** — auto-detects month/year, duplicate check
- **Smooth scrolling** — OutCubic animated scroll on all tabs
- **Morning Mist design** — forest green sidebar, warm off-white background
- **PyInstaller packaging** — single folder .exe for Windows

#### Tech Stack
- PyQt6, SQLite, Matplotlib, sentence-transformers, NumPy, LM Studio, PyInstaller

---

## [Unreleased]

### Planned
- PDF/Excel export of transactions
- Budget setting and alerts
- Multiple bank account support
- Recurring transaction detection
- Monthly email/PDF report generation
