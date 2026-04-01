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

        CREATE VIRTUAL TABLE IF NOT EXISTS transactions_fts
        USING fts5(
            transaction_id,
            month_id,
            month_label,
            date,
            paid_to,
            description,
            category,
            mode_of_transaction,
            debit,
            credit,
            content='',
            tokenize='unicode61 remove_diacritics 1'
        );
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
    """Return income + expense for every imported month."""
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


# ── FTS5 functions ────────────────────────────────────────────────────────────

def index_transactions_fts(month_id: int, month_label: str,
                            transactions: list):
    """
    Insert transactions into FTS5 virtual table for full text search.
    Clears existing entries for this month before re-indexing.
    """
    conn = get_connection()

    # clear existing FTS entries for this month first
    conn.execute(
        "DELETE FROM transactions_fts WHERE month_id = ?",
        (str(month_id),)
    )

    rows = []
    for t in transactions:
        rows.append((
            str(t.get("id", "")),
            str(month_id),
            month_label,
            t.get("date", ""),
            t.get("paid_to", ""),
            t.get("description", ""),
            t.get("category", ""),
            t.get("mode_of_transaction", ""),
            str(t.get("debit",  0)),
            str(t.get("credit", 0)),
        ))

    conn.executemany("""
        INSERT INTO transactions_fts
            (transaction_id, month_id, month_label, date,
             paid_to, description, category,
             mode_of_transaction, debit, credit)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, rows)

    conn.commit()
    conn.close()
    print(f"FTS5 indexed {len(rows)} transactions for {month_label}.")


def search_fts(query: str, month_id: int = None,
               limit: int = 25) -> list:
    """
    Full text search using FTS5.
    Returns list of matching transaction dicts.

    Supports:
    - Exact match:   "INOX"
    - Prefix match:  "muru*"
    - Phrase match:  "PVR INOX"
    - AND search:    "entertainment UPI"
    """
    conn = get_connection()

    # clean query for FTS5 — escape special chars
    clean_query = query.strip()

    # build safe FTS5 query
    # try exact phrase first, fallback to prefix on each word
    words   = clean_query.split()
    fts_query = " OR ".join([f'"{w}"' for w in words if w])

    try:
        if month_id:
            rows = conn.execute(f"""
                SELECT *
                FROM transactions_fts
                WHERE transactions_fts MATCH ?
                  AND month_id = ?
                ORDER BY rank
                LIMIT ?
            """, (fts_query, str(month_id), limit)).fetchall()
        else:
            rows = conn.execute(f"""
                SELECT *
                FROM transactions_fts
                WHERE transactions_fts MATCH ?
                ORDER BY rank
                LIMIT ?
            """, (fts_query, limit)).fetchall()

        conn.close()
        return [dict(r) for r in rows]

    except Exception as e:
        # if FTS query syntax fails fallback to LIKE search
        print(f"FTS5 query failed ({e}), falling back to LIKE search")
        conn.close()
        return search_fts_fallback(query, month_id, limit)


def search_fts_fallback(query: str, month_id: int = None,
                         limit: int = 25) -> list:
    """
    Fallback LIKE search if FTS5 query syntax fails.
    """
    conn = get_connection()
    like_query = f"%{query}%"

    if month_id:
        rows = conn.execute("""
            SELECT * FROM transactions_fts
            WHERE (paid_to LIKE ?
               OR description LIKE ?
               OR category LIKE ?)
              AND month_id = ?
            LIMIT ?
        """, (like_query, like_query, like_query,
              str(month_id), limit)).fetchall()
    else:
        rows = conn.execute("""
            SELECT * FROM transactions_fts
            WHERE paid_to LIKE ?
               OR description LIKE ?
               OR category LIKE ?
            LIMIT ?
        """, (like_query, like_query,
              like_query, limit)).fetchall()

    conn.close()
    return [dict(r) for r in rows]


def delete_fts_index(month_id: int):
    """Remove FTS5 entries for a month."""
    conn = get_connection()
    conn.execute(
        "DELETE FROM transactions_fts WHERE month_id = ?",
        (str(month_id),)
    )
    conn.commit()
    conn.close()
    print(f"FTS5 index deleted for month_id={month_id}.")