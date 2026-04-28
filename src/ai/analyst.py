# src/ai/analyst.py
from src.ai.sql_generator import generate_sql
from src.query.runner import run_query

from src.query.price_queries import (
    summarize_market_prices,
    get_top_lbmp_prices,
)


def ask_question(question: str):
    """
    Hybrid analyst:
    1. Try deterministic rules (fast + safe)
    2. Fall back to LLM SQL generation
    """

    question_clean = question.strip().lower()

    if not question_clean:
        raise ValueError("Question cannot be empty.")

    # -------------------------
    # RULE-BASED ROUTING (KEEP THIS)
    # -------------------------
    if any(term in question_clean for term in ["summary", "summarize", "overview"]):
        return summarize_market_prices()

    if any(term in question_clean for term in ["top", "highest", "spike", "spikes"]):
        return get_top_lbmp_prices(limit=20)

    # -------------------------
    # LLM FALLBACK (NEW)
    # -------------------------
    sql = generate_sql(question)
    df = run_query(sql)

    return df