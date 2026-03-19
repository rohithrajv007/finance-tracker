import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent.parent.parent / "data" / "finance.db"
DB_PATH.parent.mkdir(exist_ok=True)


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create all tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS months (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            month       INTEGER NOT NULL,
            year        INTEGER NOT NULL,
            label       TEXT NOT NULL,
            file_name   TEXT,
            imported_at TEXT NOT NULL,
            UNIQUE(month, year)
        );

        CREATE TABLE IF NOT EXISTS transactions (
            id                   INTEGER PRIMARY KEY AUTOINCREMENT,
            month_id             INTEGER NOT NULL REFERENCES months(id),
            date                 TEXT NOT NULL,
            year                 INTEGER,
            description          TEXT,
            mode_of_transaction  TEXT,
            paid_to              TEXT,
            debit                REAL DEFAULT 0.0,
            credit               REAL DEFAULT 0.0,
            balance              REAL DEFAULT 0.0,
            category             TEXT
        );

        CREATE TABLE IF NOT EXISTS chat_history (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            role        TEXT NOT NULL,
            content     TEXT NOT NULL,
            created_at  TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_transactions_month
            ON transactions(month_id);

        CREATE INDEX IF NOT EXISTS idx_transactions_category
            ON transactions(category);
    """)

    conn.commit()
    conn.close()
    print(f"Database ready at: {DB_PATH}")


def get_all_months():
    """Return list of all imported months, newest first."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM months ORDER BY year DESC, month DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_transactions(month_id):
    """Return all transactions for a given month_id."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM transactions WHERE month_id = ? ORDER BY date",
        (month_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def month_exists(month, year):
    """Check if a month/year is already imported."""
    conn = get_connection()
    row = conn.execute(
        "SELECT id FROM months WHERE month = ? AND year = ?",
        (month, year)
    ).fetchone()
    conn.close()
    return row is not None


def get_summary(month_id):
    """Return total income, expense, and closing balance for a month."""
    conn = get_connection()
    row = conn.execute("""
        SELECT
            ROUND(SUM(credit), 2)  AS total_income,
            ROUND(SUM(debit), 2)   AS total_expense,
            ROUND(SUM(credit) - SUM(debit), 2) AS net_savings
        FROM transactions
        WHERE month_id = ?
    """, (month_id,)).fetchone()

    balance_row = conn.execute("""
        SELECT balance FROM transactions
        WHERE month_id = ?
        ORDER BY date DESC, id DESC
        LIMIT 1
    """, (month_id,)).fetchone()

    conn.close()

    return {
        "total_income":    row["total_income"]  or 0,
        "total_expense":   row["total_expense"] or 0,
        "net_savings":     row["net_savings"]   or 0,
        "closing_balance": balance_row["balance"] if balance_row else 0,
    }


def get_category_breakdown(month_id):
    """Return total debit grouped by category."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT category, ROUND(SUM(debit), 2) AS total
        FROM transactions
        WHERE month_id = ? AND debit > 0
        GROUP BY category
        ORDER BY total DESC
    """, (month_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_daily_spend(month_id):
    """Return total debit per day."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT date, ROUND(SUM(debit), 2) AS total_debit
        FROM transactions
        WHERE month_id = ?
        GROUP BY date
        ORDER BY date
    """, (month_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_balance_trend(month_id):
    """Return last balance entry per day (running balance)."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT date, balance
        FROM transactions
        WHERE month_id = ?
          AND id IN (
              SELECT MAX(id) FROM transactions
              WHERE month_id = ?
              GROUP BY date
          )
        ORDER BY date
    """, (month_id, month_id)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_top_payees(month_id, limit=10):
    """Return top N payees by total debit."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT paid_to, ROUND(SUM(debit), 2) AS total
        FROM transactions
        WHERE month_id = ? AND debit > 0
        GROUP BY paid_to
        ORDER BY total DESC
        LIMIT ?
    """, (month_id, limit)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_monthly_comparison():
    """Return income + expense for every imported month (for compare view)."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT
            m.label,
            m.month,
            m.year,
            ROUND(SUM(t.credit), 2) AS total_income,
            ROUND(SUM(t.debit), 2)  AS total_expense
        FROM months m
        JOIN transactions t ON t.month_id = m.id
        GROUP BY m.id
        ORDER BY m.year, m.month
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def save_chat_message(role: str, content: str):
    """Save a chat message to history."""
    conn = get_connection()
    conn.execute(
        "INSERT INTO chat_history (role, content, created_at) VALUES (?, ?, ?)",
        (role, content, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()


def get_chat_history(limit: int = 50) -> list:
    """Return last N chat messages oldest first."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT role, content, created_at FROM chat_history "
        "ORDER BY id DESC LIMIT ?",
        (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in reversed(rows)]