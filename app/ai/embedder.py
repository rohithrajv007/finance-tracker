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
            f"via {mode}. Category: {category}. Balance after: ₹{balance:,.2f}."
        )
    else:
        return (
            f"On {date} ({month_label}), received ₹{credit:,.2f} from {paid_to} "
            f"via {mode}. Category: {category}. Balance after: ₹{balance:,.2f}."
        )


# ── embed and store ───────────────────────────────────────────────────────────
def embed_month(month_id: int, month_label: str, transactions: list):
    """Embed all transactions for a month and save to disk."""
    if not transactions:
        return

    model = _get_model()

    # load existing store
    existing_vectors, existing_meta = _load_store()

    # remove old entries for this month (clean re-import)
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

    # build new entries
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

    # merge with existing
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
    """
    Search for relevant transactions using cosine similarity.
    Returns list of natural language transaction sentences.
    """
    vectors, metadata = _load_store()

    if vectors is None or len(metadata) == 0:
        return []

    model     = _get_model()
    query_vec = model.encode([query])[0]

    # filter by month if specified
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

    # cosine similarity
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


# ── delete month embeddings ───────────────────────────────────────────────────
def delete_month_embeddings(month_id: int):
    """Remove all embeddings for a month."""
    vectors, metadata = _load_store()