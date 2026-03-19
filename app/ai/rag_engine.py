import requests
from app.ai.embedder import search
from app.db.database import get_all_months, get_summary, get_category_breakdown

LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"

SYSTEM_PROMPT = """You are a personal finance assistant helping analyze bank transactions.
You will be given ALL transactions and a summary as context.

Rules:
- Always use Indian Rupees (₹)
- Calculate totals accurately from ALL transactions given
- Be concise and specific
- Never make up transactions not in the context
- When asked about categories, use the pre-calculated category totals provided
- Format numbers as ₹X,XXX.XX
"""


def build_context(query: str, month_id: int = None) -> str:
    """Build full context — category summary + relevant transactions."""

    context_lines = []

    # ── Part 1: full category breakdown (always included) ─────────
    if month_id:
        months  = get_all_months()
        month   = next((m for m in months if m["id"] == month_id), None)
        summary = get_summary(month_id)
        cats    = get_category_breakdown(month_id)

        if month:
            context_lines.append(f"=== {month['label']} Summary ===")
            context_lines.append(f"Total Income:    ₹{summary['total_income']:,.2f}")
            context_lines.append(f"Total Expense:   ₹{summary['total_expense']:,.2f}")
            context_lines.append(f"Net Savings:     ₹{summary['net_savings']:,.2f}")
            context_lines.append(f"Closing Balance: ₹{summary['closing_balance']:,.2f}")
            context_lines.append("")

        if cats:
            context_lines.append("=== Spending by Category (EXACT TOTALS) ===")
            for c in cats:
                context_lines.append(
                    f"  {c['category']}: ₹{c['total']:,.2f}"
                )
            context_lines.append("")

    # ── Part 2: relevant transactions from vector search ──────────
    docs = search(query, month_id=month_id, top_k=25)

    if docs:
        context_lines.append("=== Relevant Transactions ===")
        for i, doc in enumerate(docs, 1):
            context_lines.append(f"{i}. {doc}")
    else:
        context_lines.append("No relevant transactions found.")

    return "\n".join(context_lines)


def ask(
    question: str,
    month_id: int = None,
    model: str = "phi-3-mini-4k-instruct",
    stream: bool = False,
    on_token=None,
):
    context = build_context(question, month_id)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": f"Context:\n{context}\n\nQuestion: {question}"},
    ]

    payload = {
        "model":       model,
        "messages":    messages,
        "temperature": 0.3,
        "max_tokens":  512,
        "stream":      False,
    }

    try:
        resp = requests.post(
            LM_STUDIO_URL,
            json=payload,
            timeout=120
        )
        resp.raise_for_status()
        answer = resp.json()["choices"][0]["message"]["content"]

        if on_token:
            on_token(answer)

        return answer

    except requests.exceptions.ConnectionError:
        error = (
            "⚠️ Cannot connect to LM Studio.\n\n"
            "Please make sure:\n"
            "1. LM Studio is open\n"
            "2. A model is loaded\n"
            "3. Local server is started (green button in LM Studio)"
        )
        if on_token:
            on_token(error)
        return error

    except requests.exceptions.Timeout:
        error = "⚠️ Request timed out. The model may be loading — try again."
        if on_token:
            on_token(error)
        return error

    except Exception as e:
        error = f"⚠️ Error: {str(e)}"
        if on_token:
            on_token(error)
        return error