from src.ai.ollama_provider import OllamaProvider
from src.ai.base import AIProvider


def get_ai_provider() -> AIProvider:
    return OllamaProvider()