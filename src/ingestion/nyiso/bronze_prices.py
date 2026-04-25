from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Literal

import pandas as pd
import requests

from src.utils.config import BRONZE_PATH, settings


NyisoProduct = Literal["day_ahead_lbmp", "real_time_lbmp"]


PRODUCT_CONFIG = {
    "day_ahead_lbmp": {
        "dataset": "damlbmp",
        "file_suffix": "damlbmp_zone",
    },
    "real_time_lbmp": {
        "dataset": "realtime",
        "file_suffix": "realtime_zone",
    },
}


def build_nyiso_daily_url(product: NyisoProduct, market_date: date) -> str:
    product_config = PRODUCT_CONFIG[product]
    base_url = settings["markets"]["nyiso"]["base_url"]

    date_key = market_date.strftime("%Y%m%d")
    dataset = product_config["dataset"]
    file_suffix = product_config["file_suffix"]

    return f"{base_url}/{dataset}/{date_key}{file_suffix}.csv"


def fetch_nyiso_daily_csv(product: NyisoProduct, market_date: date) -> pd.DataFrame:
    url = build_nyiso_daily_url(product, market_date)

    response = requests.get(url, timeout=60)
    response.raise_for_status()

    df = pd.read_csv(url)

    load_timestamp_utc = datetime.now(timezone.utc)

    df["source_system"] = "NYISO"
    df["source_product"] = product
    df["source_url"] = url
    df["market_date"] = market_date.isoformat()
    df["ingested_at_utc"] = load_timestamp_utc.isoformat()

    return df


def get_bronze_output_path(product: NyisoProduct, market_date: date) -> Path:
    return (
        BRONZE_PATH
        / "market=nyiso"
        / f"product={product}"
        / f"year={market_date.year}"
        / f"month={market_date.month:02d}"
        / f"{market_date.strftime('%Y%m%d')}.parquet"
    )


def write_bronze_parquet(df: pd.DataFrame, product: NyisoProduct, market_date: date) -> Path:
    output_path = get_bronze_output_path(product, market_date)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df.to_parquet(output_path, index=False)

    return output_path


def run_nyiso_bronze_price_load(
    product: NyisoProduct,
    start_date: date,
    end_date: date,
) -> list[Path]:
    """
    Loads NYISO daily price CSV files into Bronze Parquet.

    end_date is inclusive.
    """

    written_files: list[Path] = []

    current_date = start_date

    while current_date <= end_date:
        print(f"Loading NYISO {product} for {current_date}...")

        try:
            df = fetch_nyiso_daily_csv(product=product, market_date=current_date)
            output_path = write_bronze_parquet(
                df=df,
                product=product,
                market_date=current_date,
            )

            print(f"  Wrote {len(df):,} rows to {output_path}")
            written_files.append(output_path)

        except requests.HTTPError as error:
            print(f"  Skipped {current_date}: HTTP error - {error}")

        except Exception as error:
            print(f"  Failed {current_date}: {error}")
            raise

        current_date += timedelta(days=1)

    return written_files