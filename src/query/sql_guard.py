# src/query/sql_guard.py

BLOCKED_KEYWORDS = [
    "insert",
    "update",
    "delete",
    "drop",
    "alter",
    "create",
    "truncate",
    "merge",
    "replace",
    "copy",
    "attach",
    "detach",
]


def validate_sql(sql: str) -> None:
    """
    Basic safety check for AI-generated SQL.

    Only SELECT queries are allowed.
    """

    if not sql or not sql.strip():
        raise ValueError("SQL cannot be empty.")

    sql_clean = sql.strip().lower()

    if not sql_clean.startswith("select"):
        raise ValueError("Only SELECT queries are allowed.")

    for keyword in BLOCKED_KEYWORDS:
        if f" {keyword} " in f" {sql_clean} ":
            raise ValueError(f"Blocked SQL keyword found: {keyword}")

    if ";" in sql_clean.rstrip(";"):
        raise ValueError("Multiple SQL statements are not allowed.")