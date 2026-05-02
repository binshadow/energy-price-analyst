from src.ai.base import AIProvider
import requests
import subprocess
import time


class OllamaProvider(AIProvider):
    def __init__(self) -> None:
        super().__init__()

        config = self.get_llm_config("ollama")

        self.host = config["base_url"].rstrip("/")
        self.model = config["model"]
        self.keep_alive = config.get("keep_alive", "30m")

    def init(self) -> None:
        if not self._is_running():
            self._start_ollama()

        self._wait_until_ready()
        self._ensure_model()
        self._preload_model()

    def _is_running(self) -> bool:
        try:
            return requests.get(f"{self.host}/api/tags", timeout=2).status_code == 200
        except:
            return False

    def _start_ollama(self) -> None:
        subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    def _wait_until_ready(self, timeout: int = 30) -> None:
        start = time.time()
        while time.time() - start < timeout:
            if self._is_running():
                return
            time.sleep(1)
        raise RuntimeError("Ollama failed to start")

    def _ensure_model(self) -> None:
        response = requests.get(f"{self.host}/api/tags")
        models = [m["name"] for m in response.json().get("models", [])]

        if self.model not in models:
            subprocess.run(["ollama", "pull", self.model], check=True)

    def _preload_model(self) -> None:
        requests.post(
            f"{self.host}/api/generate",
            json={
                "model": self.model,
                "prompt": "",
                "keep_alive": self.keep_alive,
                "stream": False,
            },
        )

    def generate_sql(self, question: str, schema_context: str) -> str:
        prompt = f"""
        You are a SQL assistant for a local energy price analytics warehouse.
    
        Use this schema context:
    
        {schema_context}
    
        Rules:
        - Return only SQL.
        - Use DuckDB-compatible SQL.
        - Prefer the gold layer for analytics.
        - Start from fact_market_price when answering price questions.
        - Join dimensions using key columns.
        - Do not invent columns.
        - Do not explain the SQL.
    
        Question:
        {question}
        """.strip()

        response = requests.post(
            f"{self.host}/api/chat",
            json={
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                "stream": False,
                "keep_alive": self.keep_alive,
            },
            timeout=120,
        )

        if response.status_code != 200:
            raise RuntimeError(
                f"Ollama SQL generation failed: {response.text}"
            )

        data = response.json()
        return data["message"]["content"].strip()