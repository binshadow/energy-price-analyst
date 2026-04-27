import os
from pathlib import Path

import yaml
from dotenv import load_dotenv


load_dotenv()


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SETTINGS_PATH = PROJECT_ROOT / "config" / "settings.yaml"


def load_settings() -> dict:
    with open(SETTINGS_PATH, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


settings = load_settings()

DATA_ROOT = Path(os.getenv("DATA_ROOT") or (PROJECT_ROOT / "data"))

BRONZE_PATH = DATA_ROOT / settings["paths"]["bronze"]
SILVER_PATH = DATA_ROOT / settings["paths"]["silver"]
GOLD_PATH = DATA_ROOT / settings["paths"]["gold"]


def ensure_data_directories() -> None:
    for path in [BRONZE_PATH, SILVER_PATH, GOLD_PATH]:
        path.mkdir(parents=True, exist_ok=True)