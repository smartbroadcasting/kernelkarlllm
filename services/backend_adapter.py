from abc import ABC, abstractmethod
from typing import Any


class BackendAdapter(ABC):
    name: str

    @abstractmethod
    def load_model(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def model_info(self) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def generate(
        self, prompt: str, temperature: float, max_tokens: int
    ) -> str:
        raise NotImplementedError

    @abstractmethod
    def chat(
        self, messages: list[dict[str, str]], temperature: float, max_tokens: int
    ) -> dict[str, str]:
        raise NotImplementedError

    @abstractmethod
    def embed(self, text: str) -> list[float]:
        raise NotImplementedError
