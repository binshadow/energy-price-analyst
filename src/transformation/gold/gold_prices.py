from __future__ import annotations

from datetime import date, datetime, timezone
from pathlib import Path

import pandas as pd

from src.transformation.gold.reference_data import MARKET_CONFIG
from src.utils.config import GOLD_PATH, SILVER_PATH

def get_gold_fact_path(market: str, market_date: date) -> Path:
    return (
        GOLD_PATH
        / "facts"
        / "fact_market_price"
        / f"market={market}"
        / f"year={market_date.year}"
        / f"month={market_date.month:02d}"
        / f"{market_date.strftime('%Y%m%d')}.parquet"
    )


def get_gold_dimension_path(dimension_name: str) -> Path:
    return GOLD_PATH / "dimensions" / f"{dimension_name}.parquet"


def extract_market_date_from_path(path: Path) -> date:
    return datetime.strptime(path.stem, "%Y%m%d").date()


def list_silver_price_files() -> list[Path]:
    silver_files: list[Path] = []

    for market in MARKET_CONFIG:
        market_path = SILVER_PATH / f"market={market}"

        if not market_path.exists():
            continue

        silver_files.extend(
            sorted(market_path.glob("product=*/year=*/month=*/*.parquet"))
        )

    return sorted(silver_files)


def parse_silver_file_parts(path: Path) -> dict[str, str | date]:
    parts = path.parts

    market = next(part.split("=", 1)[1] for part in parts if part.startswith("market="))
    product = next(part.split("=", 1)[1] for part in parts if part.startswith("product="))
    market_date = extract_market_date_from_path(path)

    return {
        "market": market,
        "product": product,
        "market_date": market_date,
    }


def get_missing_gold_inputs() -> list[Path]:
    missing_files: list[Path] = []

    for silver_file in list_silver_price_files():
        file_parts = parse_silver_file_parts(silver_file)

        market = str(file_parts["market"])
        market_date = file_parts["market_date"]

        gold_fact_path = get_gold_fact_path(
            market=market,
            market_date=market_date,
        )

        if not gold_fact_path.exists():
            missing_files.append(silver_file)

    return sorted(missing_files)


def read_missing_silver_files(silver_files: list[Path]) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []

    for silver_file in silver_files:
        file_parts = parse_silver_file_parts(silver_file)

        market = str(file_parts["market"])
        product = str(file_parts["product"])

        df = pd.read_parquet(silver_file)

        df["market"] = market
        df["source_product"] = product

        frames.append(df)

    if not frames:
        return pd.DataFrame()

    return pd.concat(frames, ignore_index=True)


def add_gold_keys(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["market_code"] = df["market"].str.upper()

    df["market_key"] = df["market_code"]
    df["market_product_key"] = df["market_code"] + "|" + df["source_product"]
    df["zone_key"] = df["market_code"] + "|" + df["ptid"].astype(str)

    return df


def build_dim_market(df: pd.DataFrame) -> pd.DataFrame:
    rows = []

    for market, config in MARKET_CONFIG.items():
        market_code = config["market_code"]

        if market_code in set(df["market_code"].unique()):
            rows.append(
                {
                    "market_key": market_code,
                    "market_code": market_code,
                    "market_name": config["market_name"],
                }
            )

    return pd.DataFrame(rows).drop_duplicates()


def build_dim_market_product(df: pd.DataFrame) -> pd.DataFrame:
    rows = []

    for market, config in MARKET_CONFIG.items():
        market_code = config["market_code"]

        for product, product_config in config["products"].items():
            market_product_key = f"{market_code}|{product}"

            if market_product_key in set(df["market_product_key"].unique()):
                rows.append(
                    {
                        "market_product_key": market_product_key,
                        "market_key": market_code,
                        "market_code": market_code,
                        "source_product": product,
                        "market_product_code": product_config["market_product_code"],
                        "market_product_name": product_config["market_product_name"],
                    }
                )

    return pd.DataFrame(rows).drop_duplicates()


def build_dim_zone(df: pd.DataFrame) -> pd.DataFrame:
    dim_zone = (
        df[
            [
                "zone_key",
                "market_key",
                "market_code",
                "ptid",
                "zone_name",
            ]
        ]
        .drop_duplicates()
        .rename(
            columns={
                "ptid": "zone_id",
            }
        )
    )

    return dim_zone


def build_fact_market_price(df: pd.DataFrame) -> pd.DataFrame:
    fact = df[
        [
            "market_key",
            "market_product_key",
            "zone_key",
            "timestamp",
            "market_date",
            "lbmp",
            "marginal_cost_losses",
            "marginal_cost_congestion",
            "source_url",
            "bronze_ingested_at_utc",
            "silver_ingested_at_utc",
        ]
    ].copy()

    fact["gold_ingested_at_utc"] = datetime.now(timezone.utc)

    return fact


def merge_with_existing_dimension(
    new_dimension: pd.DataFrame,
    dimension_name: str,
    natural_key_columns: list[str],
) -> pd.DataFrame:
    dimension_path = get_gold_dimension_path(dimension_name)

    if dimension_path.exists():
        existing_dimension = pd.read_parquet(dimension_path)
        combined = pd.concat([existing_dimension, new_dimension], ignore_index=True)
    else:
        combined = new_dimension

    return combined.drop_duplicates(subset=natural_key_columns)


def write_gold_dimension(df: pd.DataFrame, dimension_name: str) -> Path:
    output_path = get_gold_dimension_path(dimension_name)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df.to_parquet(output_path, index=False)

    return output_path


def write_gold_fact(df: pd.DataFrame, market: str, market_date: date) -> Path:
    output_path = get_gold_fact_path(market=market, market_date=market_date)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df.to_parquet(output_path, index=False)

    return output_path


def run_gold_price_load() -> list[Path]:
    missing_silver_files = get_missing_gold_inputs()

    if not missing_silver_files:
        print("No missing Gold price dates found.")
        return []

    print(f"Found {len(missing_silver_files):,} Silver price files missing from Gold.")

    df_silver = read_missing_silver_files(missing_silver_files)

    if df_silver.empty:
        print("No Silver rows available to process.")
        return []

    df_gold_base = add_gold_keys(df_silver)

    dim_market = merge_with_existing_dimension(
        new_dimension=build_dim_market(df_gold_base),
        dimension_name="dim_market",
        natural_key_columns=["market_key"],
    )

    dim_market_product = merge_with_existing_dimension(
        new_dimension=build_dim_market_product(df_gold_base),
        dimension_name="dim_market_product",
        natural_key_columns=["market_product_key"],
    )

    dim_zone = merge_with_existing_dimension(
        new_dimension=build_dim_zone(df_gold_base),
        dimension_name="dim_zone",
        natural_key_columns=["zone_key"],
    )

    written_files: list[Path] = []

    written_files.append(write_gold_dimension(dim_market, "dim_market"))
    written_files.append(write_gold_dimension(dim_market_product, "dim_market_product"))
    written_files.append(write_gold_dimension(dim_zone, "dim_zone"))

    fact = build_fact_market_price(df_gold_base)

    for (market, market_date), df_fact_partition in fact.groupby(["market_key", "market_date"]):
        output_path = write_gold_fact(
            df=df_fact_partition,
            market=str(market).lower(),
            market_date=market_date,
        )

        print(f"  Wrote {len(df_fact_partition):,} rows to {output_path}")
        written_files.append(output_path)

    return written_files