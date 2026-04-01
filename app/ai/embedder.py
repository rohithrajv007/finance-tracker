import json
import numpy as np
from pathlib import Path

# ── storage path ──────────────────────────────────────────────────────────────
VECTOR_PATH = Path(__file__).parent.parent.parent / "data" / "vectors"
VECTOR_PATH.mkdir(parents=True, exist_ok=True)

VECTORS_FILE  = VECTOR_PATH / "embeddings.npy"
METADATA_FILE = VECTOR_PATH / "metadata.json"

# ── lazy model ────────────────────────────────────────────────────────────────
_embed_model = None


def _get_model():
    global _embed_model
    if _embed_model is None:
        from sentence_transformers import SentenceTransformer
        print("Loading embedding model...")
        _embed_model = SentenceTransformer("all-MiniLM-L6-v2")
        print("Embedding model ready.")
    return _embed_model


# ── load / save vector store ──────────────────────────────────────────────────
def _load_store():
    """Load existing vectors and metadata from disk."""
    if VECTORS_FILE.exists() and METADATA_FILE.exists():
        vectors = np.load(str(VECTORS_FILE))
        with open(METADATA_FILE, "r", encoding="utf-8") as f:
            metadata = json.load(f)
        return vectors, metadata
    return None, []


def _save_store(vectors: np.ndarray, metadata: list):
    """Save vectors and metadata to disk."""
    np.save(str(VECTORS_FILE), vectors)
    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False)


# ── transaction → natural language ───────────────────────────────────────────
def transaction_to_text(t: dict) -> str:
    date        = t.get("date", "")
    paid_to     = t.get("paid_to", "Unknown")
    category    = t.get("category", "Others")
    mode        = t.get("mode_of_transaction", "")
    debit       = float(t.get("debit",  0))
    credit      = float(t.get("credit", 0))
    balance     = float(t.get("balance", 0))
    month_label = t.get("month_label", "")

    if debit > 0:
        return (
            f"On {date} ({month_label}), paid ₹{debit:,.2f} to {paid_to} "
            f"via {mode}. Category: {category}. "
            f"Balance after: ₹{balance:,.2f}."
        )
    else:
        return (
            f"On {date} ({month_label}), received ₹{credit:,.2f} "
            f"from {paid_to} via {mode}. Category: {category}. "
            f"Balance after: ₹{balance:,.2f}."
        )


# ── embed and store ───────────────────────────────────────────────────────────
def embed_month(month_id: int, month_label: str, transactions: list):
    """Embed all transactions for a month and save to disk."""
    if not transactions:
        return

    model = _get_model()

    existing_vectors, existing_meta = _load_store()

    # remove old entries for this month
    if existing_meta:
        keep_idx = [
            i for i, m in enumerate(existing_meta)
            if m.get("month_id") != month_id
        ]
        if keep_idx:
            existing_vectors = existing_vectors[keep_idx]
            existing_meta    = [existing_meta[i] for i in keep_idx]
        else:
            existing_vectors = None
            existing_meta    = []

    documents = []
    new_meta  = []

    for t in transactions:
        t["month_label"] = month_label
        text = transaction_to_text(t)
        documents.append(text)
        new_meta.append({
            "id":          t.get("id"),
            "month_id":    month_id,
            "month_label": month_label,
            "date":        t.get("date", ""),
            "category":    t.get("category", ""),
            "debit":       float(t.get("debit",  0)),
            "credit":      float(t.get("credit", 0)),
            "text":        text,
        })

    new_vectors = model.encode(documents, show_progress_bar=False)

    if existing_vectors is not None and len(existing_vectors) > 0:
        all_vectors = np.vstack([existing_vectors, new_vectors])
        all_meta    = existing_meta + new_meta
    else:
        all_vectors = new_vectors
        all_meta    = new_meta

    _save_store(all_vectors, all_meta)
    print(f"Embedded {len(documents)} transactions for {month_label}.")


# ── cosine similarity search ──────────────────────────────────────────────────
def search(query: str, month_id: int = None, top_k: int = 25) -> list:
    vectors, metadata = _load_store()

    if vectors is None or len(metadata) == 0:
        return []

    model     = _get_model()
    query_vec = model.encode([query])[0]

    if month_id is not None:
        indices = [
            i for i, m in enumerate(metadata)
            if m.get("month_id") == month_id
        ]
        if not indices:
            return []
        filtered_vectors = vectors[indices]
        filtered_meta    = [metadata[i] for i in indices]
    else:
        filtered_vectors = vectors
        filtered_meta    = metadata

    norms          = np.linalg.norm(filtered_vectors, axis=1, keepdims=True)
    norms          = np.where(norms == 0, 1, norms)
    normed_vectors = filtered_vectors / norms

    query_norm = np.linalg.norm(query_vec)
    if query_norm == 0:
        return []
    normed_query = query_vec / query_norm

    similarities = normed_vectors @ normed_query
    top_indices  = np.argsort(similarities)[::-1][:top_k]

    return [filtered_meta[i]["text"] for i in top_indices]


# ── hybrid search ─────────────────────────────────────────────────────────────
def hybrid_search(query: str, month_id: int = None, top_k: int = 25) -> list:
    fts_texts = []

    try:
        from app.db.database import search_fts
        fts_results = search_fts(query, month_id=month_id, limit=top_k)

        for r in fts_results:
            try:
                debit  = float(r.get("debit", 0) or 0)
            except (TypeError, ValueError):
                debit = 0.0

            try:
                credit = float(r.get("credit", 0) or 0)
            except (TypeError, ValueError):
                credit = 0.0

            date        = r.get("date", "") or ""
            paid_to     = r.get("paid_to", "") or ""
            category    = r.get("category", "") or ""
            mode        = r.get("mode_of_transaction", "") or ""
            month_label = r.get("month_label", "") or ""

            if not date or not paid_to:
                continue

            if debit > 0:
                text = (
                    f"On {date} ({month_label}), paid ₹{debit:,.2f} "
                    f"to {paid_to} via {mode}. Category: {category}."
                )
            else:
                text = (
                    f"On {date} ({month_label}), received ₹{credit:,.2f} "
                    f"from {paid_to} via {mode}. Category: {category}."
                )

            fts_texts.append(text)

    except Exception as e:
        print(f"FTS5 search warning: {e}")
        fts_texts = []

    # semantic search
    try:
        semantic_texts = search(query, month_id=month_id, top_k=top_k)
    except Exception as e:
        print(f"Semantic search warning: {e}")
        semantic_texts = []

    # merge + deduplicate
    seen = set()
    combined = []

    for text in fts_texts + semantic_texts:
        key = text[:60].strip().lower()
        if key not in seen:
            seen.add(key)
            combined.append(text)

    return combined[:top_k]


# ── delete embeddings ─────────────────────────────────────────────────────────
def delete_month_embeddings(month_id: int):
    vectors, metadata = _load_store()
    if not metadata:
        return

    keep_idx = [
        i for i, m in enumerate(metadata)
        if m.get("month_id") != month_id
    ]

    if keep_idx:
        new_vectors = vectors[keep_idx]
        new_meta    = [metadata[i] for i in keep_idx]
        _save_store(new_vectors, new_meta)
    else:
        if VECTORS_FILE.exists():
            VECTORS_FILE.unlink()
        if METADATA_FILE.exists():
            METADATA_FILE.unlink()

    print(f"Deleted embeddings for month_id={month_id}.")