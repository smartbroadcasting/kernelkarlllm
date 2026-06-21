import logging
from threading import Lock
from typing import Any

from config.settings import Settings
from services.backend_adapter import BackendAdapter
from services.model_loader import LlamaCppModelLoader


class LlamaCppAdapter(BackendAdapter):
    name = "llama.cpp"

    def __init__(self, settings: Settings, logger: logging.Logger) -> None:
        self.settings = settings
        self.logger = logger
        self.loader = LlamaCppModelLoader(settings, logger)
        self._inference_lock = Lock()

    def load_model(self) -> None:
        self.loader.get_model()

    def model_info(self) -> dict[str, Any]:
        return {
            "backend": self.name,
            **self.loader.info(),
        }

    def generate(self, prompt: str, temperature: float, max_tokens: int,
                 min_p: float | None = None, top_p: float | None = None, top_k: int | None = None) -> str:
        model = self.loader.get_model()
        kwargs: dict = dict(temperature=temperature, max_tokens=max_tokens)
        if min_p is not None:
            kwargs["min_p"] = min_p
        if top_p is not None:
            kwargs["top_p"] = top_p
        if top_k is not None:
            kwargs["top_k"] = top_k

        with self._inference_lock:
            result = model.create_chat_completion(
                messages=[{"role": "user", "content": prompt}],
                **kwargs,
            )

        return result["choices"][0]["message"]["content"].strip()

    def chat(
        self, messages: list[dict[str, str]], temperature: float, max_tokens: int,
        min_p: float | None = None, top_p: float | None = None, top_k: int | None = None,
    ) -> dict[str, str]:
        model = self.loader.get_model()
        kwargs: dict = dict(temperature=temperature, max_tokens=max_tokens)
        if min_p is not None:
            kwargs["min_p"] = min_p
        if top_p is not None:
            kwargs["top_p"] = top_p
        if top_k is not None:
            kwargs["top_k"] = top_k

        with self._inference_lock:
            result = model.create_chat_completion(
                messages=messages,
                **kwargs,
            )

        content = result["choices"][0]["message"]["content"].strip()

        return {
            "role": "assistant",
            "content": content,
        }

    def embed(self, text: str) -> list[float]:
        model = self.loader.get_model()

        with self._inference_lock:
            result = model.create_embedding(text)

        return result["data"][0]["embedding"]


def create_backend(settings: Settings, logger: logging.Logger) -> BackendAdapter:
    if settings.backend != "llama_cpp":
        raise ValueError(f"Unsupported backend: {settings.backend}")

    return LlamaCppAdapter(settings, logger)
