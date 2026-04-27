from __future__ import annotations

from datetime import date, datetime, timezone
from pathlib import Path
from typing import Literal

import pandas as pd

from src.utils.config import BRONZE_PATH, SILVER_PATH
from src.ingestion.nyiso.mappings import NYISO_PRICE_COLUMN_RENAMES


NyisoProduct = Literal["day_ahead_lbmp", "real_time_lbmp"]


def get_bronze_file_path(product: NyisoProduct, market_date: date) -> Path:
    return (
        BRONZE_PATH
        / "market=nyiso"
        / f"product={product}"
        / f"year={market_date.year}"
        / f"month={market_date.month:02d}"
        / f"{market_date.strftime('%Y%m%d')}.parquet"
    )


def get_silver_file_path(product: NyisoProduct, market_date: date) -> Path:
    return (
        SILVER_PATH
        / "market=nyiso"
        / f"product={product}"
        / f"year={market_date.year}"
        / f"month={market_date.month:02d}"
        / f"{market_date.strftime('%Y%m%d')}.parquet"
    )


def extract_market_date_from_path(path: Path) -> date:
    return datetime.strptime(path.stem, "%Y%m%d").date()


def list_bronze_files(product: NyisoProduct) -> list[Path]:
    bronze_product_path = BRONZE_PATH / "market=nyiso" / f"product={product}"

    if not bronze_product_path.exists():
        return []

    return sorted(bronze_product_path.glob("year=*/month=*/*.parquet"))


def get_missing_silver_dates(product: NyisoProduct) -> list[date]:
    missing_dates: list[date] = []

    for bronze_file in list_bronze_files(product):
        market_date = extract_market_date_from_path(bronze_file)
        silver_file = get_silver_file_path(product, market_date)

        if not silver_file.exists():
            missing_dates.append(market_date)

    return sorted(missing_dates)


def transform_nyiso_bronze_to_silver(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # --- Rename columns using mapping ---
    df = df.rename(columns=NYISO_PRICE_COLUMN_RENAMES)

    # --- Standardize column names (safety layer if anything slips through) ---
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("/", "_")
        .str.replace("-", "_")
    )

    # --- Type conversions ---
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["market_date"] = pd.to_datetime(df["market_date"]).dt.date

    df["bronze_ingested_at_utc"] = pd.to_datetime(
        df["ingested_at_utc"],
        utc=True,
    )

    # --- Drop ingested_at_utc ---
    df.drop(columns=["ingested_at_utc"], inplace=True)

    # --- Add Silver metadata ---
    df["silver_ingested_at_utc"] = datetime.now(timezone.utc)

    return df


def write_silver_parquet(
    df: pd.DataFrame,
    product: NyisoProduct,
    market_date: date,
) -> Path:
    output_path = get_silver_file_path(product, market_date)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df.to_parquet(output_path, index=False)

    return output_path


def run_nyiso_silver_price_load(product: NyisoProduct) -> list[Path]:
    """
    Loads NYISO Bronze files into Silver for dates that do not already exist in Silver.
    """

    missing_dates = get_missing_silver_dates(product)
    written_files: list[Path] = []

    if not missing_dates:
        print(f"No missing NYISO Silver dates found for {product}.")
        return written_files

    print(f"Found {len(missing_dates):,} NYISO {product} Bronze dates missing from Silver.")

    for market_date in missing_dates:
        print(f"Loading NYISO Silver {product} for {market_date}...")

        bronze_path = get_bronze_file_path(product, market_date)

        df_bronze = pd.read_parquet(bronze_path)
        df_silver = transform_nyiso_bronze_to_silver(df_bronze)

        output_path = write_silver_parquet(
            df=df_silver,
            product=product,
            market_date=market_date,
        )

        print(f"  Wrote {len(df_silver):,} rows to {output_path}")
        written_files.append(output_path)

    return written_files