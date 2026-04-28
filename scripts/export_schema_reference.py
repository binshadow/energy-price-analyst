from pathlib import Path
import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

import duckdb

from src.utils.config import BRONZE_PATH, SILVER_PATH, GOLD_PATH





OUTPUT_PATH = Path("docs/schema_reference.md")


LAYER_PATHS = {
    "bronze": BRONZE_PATH,
    "silver": SILVER_PATH,
    "gold": GOLD_PATH,
}


def find_parquet_tables(layer_path: Path) -> list[Path]:
    """
    Finds folders that contain parquet files.
    Each folder is treated as a logical table.
    """
    parquet_files = list(layer_path.rglob("*.parquet"))

    table_dirs = sorted({file.parent for file in parquet_files})

    return table_dirs


def get_schema_for_path(path: Path) -> list[tuple[str, str]]:
    parquet_path = str(path / "*.parquet").replace("\\", "/")

    sql = f"""
    DESCRIBE
    SELECT *
    FROM read_parquet('{parquet_path}')
    """

    with duckdb.connect(database=":memory:") as conn:
        rows = conn.execute(sql).fetchall()

    return [(row[0], row[1]) for row in rows]


def relative_table_name(layer_path: Path, table_path: Path) -> str:
    return str(table_path.relative_to(layer_path)).replace("\\", "/")


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    lines = []
    lines.append("# Energy Price Analyst Schema Reference")
    lines.append("")
    lines.append("This document describes the local Parquet warehouse schema used by the Energy Price Analyst project.")
    lines.append("")

    for layer_name, layer_path in LAYER_PATHS.items():
        lines.append(f"## {layer_name.title()} Layer")
        lines.append("")
        lines.append(f"Base path: `{layer_path}`")
        lines.append("")

        table_paths = find_parquet_tables(layer_path)

        if not table_paths:
            lines.append("_No Parquet tables found._")
            lines.append("")
            continue

        for table_path in table_paths:
            table_name = relative_table_name(layer_path, table_path)

            lines.append(f"### `{table_name}`")
            lines.append("")
            lines.append("| Column | Type |")
            lines.append("|---|---|")

            try:
                schema = get_schema_for_path(table_path)

                for column_name, column_type in schema:
                    lines.append(f"| `{column_name}` | `{column_type}` |")

            except Exception as exc:
                lines.append(f"| ERROR | `{exc}` |")

            lines.append("")

    OUTPUT_PATH.write_text("\n".join(lines), encoding="utf-8")

    print(f"Schema reference written to: {OUTPUT_PATH.resolve()}")


if __name__ == "__main__":
    main()