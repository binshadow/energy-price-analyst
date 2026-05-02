from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict

import yaml


class AIProvider(ABC):
    def __init__(self) -> None:
        self.settings = self._load_settings()

    def _load_settings(self) -> Dict[str, Any]:
        settings_path = Path("config/settings.yaml")

        if not settings_path.exists():
            raise FileNotFoundError("settings.yaml not found")

        with open(settings_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def get_llm_config(self, provider_name: str) -> Dict[str, Any]:
        try:
            return self.settings["llm"][provider_name]
        except KeyError:
            raise ValueError(f"Missing config for provider: {provider_name}")

    @abstractmethod
    def init(self) -> None:
        pass

    @abstractmethod
    def generate_sql(self, question: str, schema_context: str) -> str:
        pass