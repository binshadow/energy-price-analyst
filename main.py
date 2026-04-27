from datetime import date, timedelta

from src.ingestion.nyiso.bronze_prices import run_nyiso_bronze_price_load
from src.ingestion.nyiso.silver_prices import run_nyiso_silver_price_load
from src.transformation.gold.gold_prices import run_gold_price_load

from src.utils.config import ensure_data_directories


NYISO_PRODUCTS = [
    "day_ahead_lbmp",
    "real_time_lbmp",
]


def main() -> None:
    ensure_data_directories()

    end_date = date.today() - timedelta(days=1)
    start_date = end_date - timedelta(days=7)

    for product in NYISO_PRODUCTS:
        print("=" * 80)
        print(f"Starting NYISO Bronze load for {product}")
        print("=" * 80)

        run_nyiso_bronze_price_load(
            product=product,
            start_date=start_date,
            end_date=end_date,
            overwrite_existing=False,
        )

        print("=" * 80)
        print(f"Starting NYISO Silver load for {product}")
        print("=" * 80)

        run_nyiso_silver_price_load(product=product)

    run_gold_price_load()


if __name__ == "__main__":
    main()