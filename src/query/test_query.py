from src.utils.config import GOLD_PATH
from src.query.duckdb_client import run_query


def test_gold_connection():
    path = str(GOLD_PATH / "facts" / "fact_market_price" / "**" / "*.parquet")

    sql = f"""
    SELECT *
    FROM read_parquet('{path}')
    LIMIT 10
    """

    return run_query(sql)