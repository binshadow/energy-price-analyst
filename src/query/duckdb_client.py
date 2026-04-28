from pathlib import Path

import duckdb
import pandas as pd

from src.utils.config import GOLD_PATH, SILVER_PATH, BRONZE_PATH


def get_data_paths() -> dict[str, Path]:
    """
    Central access to warehouse layer paths from config.
    """
    return {
        "bronze": BRONZE_PATH,
        "silver": SILVER_PATH,
        "gold": GOLD_PATH,
    }


def run_query(sql: str) -> pd.DataFrame:
    """
    Run a read-only DuckDB query and return results as a DataFrame.
    """
    sql_clean = sql.strip().lower()

    blocked_keywords = [
        "insert ",
        "update ",
        "delete ",
        "drop ",
        "create ",
        "alter ",
        "copy ",
        "attach ",
    ]

    if any(keyword in sql_clean for keyword in blocked_keywords):
        raise ValueError("Only read-only SELECT queries are allowed.")

    with duckdb.connect(database=":memory:") as conn:
        return conn.execute(sql).fetchdf()