from src.utils.config import GOLD_PATH
from src.query.duckdb_client import run_query


def get_fact_market_price_path() -> str:
    return str(GOLD_PATH / "facts" / "fact_market_price" / "**" / "*.parquet")


def summarize_market_prices():
    path = get_fact_market_price_path()

    sql = f"""
    SELECT
        market_key,
        market_product_key,
        COUNT(*) AS row_count,
        MIN(timestamp) AS min_timestamp,
        MAX(timestamp) AS max_timestamp,
        AVG(lbmp) AS avg_lbmp,
        MIN(lbmp) AS min_lbmp,
        MAX(lbmp) AS max_lbmp
    FROM read_parquet('{path}')
    GROUP BY
        market_key,
        market_product_key
    ORDER BY
        market_key,
        market_product_key
    """

    return run_query(sql)


def get_top_lbmp_prices(limit: int = 20):
    path = get_fact_market_price_path()

    sql = f"""
    SELECT
        market_key,
        market_product_key,
        zone_key,
        timestamp,
        market_date,
        lbmp
    FROM read_parquet('{path}')
    ORDER BY lbmp DESC
    LIMIT {limit}
    """

    return run_query(sql)