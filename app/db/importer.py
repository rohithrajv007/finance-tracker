import json
from pathlib import Path
from datetime import datetime
from app.db.database import get_connection, month_exists


def parse_month_year(transactions: list) -> tuple[int, int]:
    """Auto-detect month and year from the first transaction's date."""
    first_date = transactions[0]["date"]   # format: "01-09-2025"
    parts = first_date.split("-")
    day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
    return month, year


def import_json(file_path: str) -> dict:
    """
    Import a JSON transaction file into the database.

    Returns a result dict with keys:
        success (bool), message (str), month_id (int), summary (dict)
    """
    path = Path(file_path)

    if not path.exists():
        return {"success": False, "message": f"File not found: {file_path}"}

    with open(path, "r", encoding="utf-8") as f:
        transactions = json.load(f)

    if not transactions:
        return {"success": False, "message": "JSON file is empty."}

    month, year = parse_month_year(transactions)

    month_names_short = [
        "", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
    ]
    month_names_full = [
        "", "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]

    if month_exists(month, year):
        label = f"{month_names_short[month]} {year}"
        return {
            "success": False,
            "message": f"{label} is already imported. Delete it first to re-import."
        }

    label = f"{month_names_full[month]} {year}"

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Insert month record
        cursor.execute("""
            INSERT INTO months (month, year, label, file_name, imported_at)
            VALUES (?, ?, ?, ?, ?)
        """, (month, year, label, path.name, datetime.now().isoformat()))

        month_id = cursor.lastrowid

        # Bulk insert transactions
        rows = []
        for t in transactions:
            rows.append((
                month_id,
                t.get("date", ""),
                t.get("year", year),
                t.get("description", ""),
                t.get("mode_of_transaction", ""),
                t.get("paid_to", ""),
                float(t.get("debit",   0.0)),
                float(t.get("credit",  0.0)),
                float(t.get("balance", 0.0)),
                t.get("category", "Others"),
            ))

        cursor.executemany("""
            INSERT INTO transactions
                (month_id, date, year, description, mode_of_transaction,
                 paid_to, debit, credit, balance, category)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, rows)

        conn.commit()

        # ── fetch inserted rows with real DB ids for embedding ────
        inserted = conn.execute(
            "SELECT * FROM transactions WHERE month_id = ?", (month_id,)
        ).fetchall()
        inserted_dicts = [dict(r) for r in inserted]

        conn.close()

        # ── embed into ChromaDB (after conn is closed) ─────────────
        try:
            from app.ai.embedder import embed_month
            embed_month(month_id, label, inserted_dicts)
        except Exception as embed_err:
            # embedding failure should not break the import
            print(f"Warning: embedding failed — {embed_err}")

        total_income  = sum(float(t.get("credit", 0)) for t in transactions)
        total_expense = sum(float(t.get("debit",  0)) for t in transactions)

        return {
            "success":  True,
            "message":  f"Imported {len(rows)} transactions for {label}.",
            "month_id": month_id,
            "summary": {
                "label":         label,
                "count":         len(rows),
                "total_income":  round(total_income,  2),
                "total_expense": round(total_expense, 2),
                "net_savings":   round(total_income - total_expense, 2),
            }
        }

    except Exception as e:
        conn.rollback()
        conn.close()
        return {"success": False, "message": f"Import failed: {str(e)}"}