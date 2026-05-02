# src/ai/sql_generator.py

import requests

from src.utils.config import AI_PROVIDER, settings


SQL_GENERATOR_SYSTEM_PROMPT = """
You are an expert data analyst writing DuckDB SQL for a local Parquet-based energy price warehouse.

Your job:
- Convert the user's business question into a single DuckDB SELECT query.
- Return SQL only.
- Do not explain the SQL.
- Do not wrap the SQL in markdown.
- Use only the approved gold-layer tables/views.
- Prefer the gold layer for all analytics.
- Never query bronze or silver unless explicitly instructed.
- Never modify data.

Approved tables/views:
- fact_market_price
- dim_market
- dim_market_product
- dim_zone

Fact table:
fact_market_price

Fact grain:
One row per market, product, zone/location, and timestamp.

Fact columns:
- market_key
- market_product_key
- zone_key
- timestamp
- market_date
- lbmp
- marginal_cost_losses
- marginal_cost_congestion
- source_url
- bronze_ingested_at_utc
- silver_ingested_at_utc
- gold_ingested_at_utc
- market
- month
- year

Dimension: dim_market
Columns:
- market_key
- market_code
- market_name

Dimension: dim_market_product
Columns:
- market_product_key
- market_key
- market_code
- source_product
- market_product_code
- market_product_name

Dimension: dim_zone
Columns:
- zone_key
- market_key
- zone_name
- ptid

Relationships:
- fact_market_price.market_key = dim_market.market_key
- fact_market_price.market_product_key = dim_market_product.market_product_key
- fact_market_price.zone_key = dim_zone.zone_key

Business definitions:
- Use fact_market_price.lbmp for price questions unless the user asks for losses or congestion.
- Day-ahead means dim_market_product.market_product_code = 'DAY_AHEAD'.
- Real-time means dim_market_product.market_product_code = 'REAL_TIME'.
- Product filtering must use dim_market_product.market_product_code.
- Product display names should use dim_market_product.market_product_name.
- Source product values should use dim_market_product.market_product_code.
- Zone/location means dim_zone.zone_name.
- NYISO means dim_market.market_code = 'NYISO'.

SQL rules:
- Always use table aliases:
  - f for fact_market_price
  - m for dim_market
  - p for dim_market_product
  - z for dim_zone
- Use explicit JOIN syntax.
- Use DuckDB-compatible SQL.
- Use single quotes for strings.
- Use DATE literals for date filters.
- Prefer f.market_date for date filtering.
- Prefer f.timestamp for hourly analysis.
- For month filters, use f.year and f.month.
- f.month is stored as a two-character string such as '04'.
- Add ORDER BY for top, bottom, highest, lowest, or ranking questions.
- If no limit is specified for ranking questions, use LIMIT 10.
- Never use SELECT *.
- Never use product_code.
- Never use product_name.
- Never generate INSERT, UPDATE, DELETE, MERGE, DROP, ALTER, CREATE, COPY, INSTALL, LOAD, ATTACH, DETACH, EXPORT, or PRAGMA.
- Never use file paths in generated SQL.
- Never hallucinate table names or column names.
- If the question cannot be answered from the approved schema, return:
  SELECT 'Unable to answer from available gold schema' AS message;

Output rules:
- Return only SQL.
- No markdown.
- No explanation.
""".strip()

def build_sql_prompt(question: str) -> str:
    return f"""
{SQL_GENERATOR_SYSTEM_PROMPT}

User question:
{question}

DuckDB SQL:
""".strip()


def clean_sql_response(response_text: str) -> str:
    """
    Removes common LLM formatting artifacts.
    """
    sql = response_text.strip()

    if sql.startswith("```sql"):
        sql = sql.removeprefix("```sql").strip()

    if sql.startswith("```"):
        sql = sql.removeprefix("```").strip()

    if sql.endswith("```"):
        sql = sql.removesuffix("```").strip()

    return sql


def generate_sql(question: str) -> str:
    """
    Generate DuckDB SQL from a business question using the configured AI provider.
    """

    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    provider = AI_PROVIDER.lower()

    if provider == "ollama":
        return generate_sql_with_ollama(question)

    raise ValueError(f"Unsupported AI_PROVIDER: {AI_PROVIDER}")


def generate_sql_with_ollama(question: str) -> str:
    """
    Calls local Ollama to generate SQL.
    """

    llm_settings = settings.get("llm", {}).get("ollama", {})

    base_url = llm_settings.get("base_url", "http://localhost:11434")
    model = llm_settings.get("model", "llama3.1")

    prompt = build_sql_prompt(question)

    response = requests.post(
        f"{base_url}/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
        },
        timeout=120,
    )

    response.raise_for_status()

    response_json = response.json()
    sql = response_json.get("response", "")

    return clean_sql_response(sql)