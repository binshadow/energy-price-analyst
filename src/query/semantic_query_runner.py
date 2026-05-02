# src/query/semantic_query_runner.py


import duckdb
import pandas as pd

from src.ai.sql_generator import generate_sql
from src.query.sql_guard import validate_sql
from src.utils.config import GOLD_PATH



def run_semantic_query(question: str) -> tuple[str, pd.DataFrame]:
    """
    Converts a natural-language question into SQL, validates it,
    runs it against the gold warehouse, and returns both SQL and results.
    """

    sql = generate_sql(question)
    validate_sql(sql)

    gold_root = GOLD_PATH.as_posix()

    fact_market_price_path = f"{gold_root}/facts/fact_market_price/**/*.parquet"
    dim_market_path = f"{gold_root}/dimensions/dim_market.parquet"
    dim_market_product_path = f"{gold_root}/dimensions/dim_market_product.parquet"
    dim_zone_path = f"{gold_root}/dimensions/dim_zone.parquet"

    conn = duckdb.connect()

    conn.execute(f"""
        CREATE OR REPLACE VIEW fact_market_price AS
        SELECT * FROM read_parquet('{fact_market_price_path}');
    """)

    conn.execute(f"""
        CREATE OR REPLACE VIEW dim_market AS
        SELECT * FROM read_parquet('{dim_market_path}');
    """)

    conn.execute(f"""
        CREATE OR REPLACE VIEW dim_market_product AS
        SELECT * FROM read_parquet('{dim_market_product_path}');
    """)

    conn.execute(f"""
        CREATE OR REPLACE VIEW dim_zone AS
        SELECT * FROM read_parquet('{dim_zone_path}');
    """)

    df = conn.execute(sql).fetchdf()

    conn.close()

    return sql, df