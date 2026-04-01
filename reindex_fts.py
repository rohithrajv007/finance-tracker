from app.db.database import (
    init_db, get_all_months,
    get_transactions, index_transactions_fts,
    delete_fts_index
)

print("Step 1: Init DB...")
init_db()

months = get_all_months()
if not months:
    print("No months found. Import a JSON first.")
else:
    for month in months:
        print(f"Indexing {month['label']}...")
        delete_fts_index(month["id"])
        transactions = get_transactions(month["id"])
        index_transactions_fts(month["id"], month["label"], transactions)
        print(f"Done — {len(transactions)} transactions indexed.")

print("\nAll months FTS5 indexed successfully!")