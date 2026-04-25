from datetime import date, timedelta

from src.ingestion.nyiso.bronze_prices import run_nyiso_bronze_price_load
from src.utils.config import ensure_data_directories


def main() -> None:
    ensure_data_directories()

    end_date = date.today() - timedelta(days=1)
    start_date = end_date - timedelta(days=7)

    run_nyiso_bronze_price_load(
        product="day_ahead_lbmp",
        start_date=start_date,
        end_date=end_date,
    )

    run_nyiso_bronze_price_load(
        product="real_time_lbmp",
        start_date=start_date,
        end_date=end_date,
    )


if __name__ == "__main__":
    main()