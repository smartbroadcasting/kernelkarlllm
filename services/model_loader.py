import logging
import os
from pathlib import Path
from threading import Lock
from typing import Any

from llama_cpp import Llama

from config.settings import Settings


class ModelNotLoadedError(Exception):
    pass


class LlamaCppModelLoader:
    def __init__(self, settings: Settings, logger: logging.Logger) -> None:
        self.settings = settings
        self.logger = logger
        self._model: Llama | None = None
        self._resolved_model_path: Path | None = None
        self._lock = Lock()

    @property
    def model_name(self) -> str:
        return Path(self.settings.model_path).name

    @property
    def is_loaded(self) -> bool:
        return self._model is not None

    def _thread_count(self) -> int:
        if self.settings.model_threads > 0:
            return self.settings.model_threads

        try:
            return max(1, len(os.sched_getaffinity(0)))
        except AttributeError:
            return max(1, os.cpu_count() or 1)

    def _available_models(self) -> list[Path]:
        model_dir = self.settings.model_path.parent
        if not model_dir.exists():
            return []

        return sorted(model_dir.glob("*.gguf"))

    def _resolve_model_path(self) -> Path:
        configured_path = self.settings.model_path
        if configured_path.exists():
            return configured_path

        available_models = self._available_models()
        if not available_models:
            raise ModelNotLoadedError(f"Model not found: {configured_path}")

        configured_name = configured_path.name.lower()
        for candidate in available_models:
            if candidate.name.lower() == configured_name:
                self.logger.warning(
                    "model_path_fallback",
                    extra={
                        "configured_model_path": str(configured_path),
                        "resolved_model_path": str(candidate),
                    },
                )
                return candidate

        if len(available_models) == 1:
            candidate = available_models[0]
            self.logger.warning(
                "model_path_fallback",
                extra={
                    "configured_model_path": str(configured_path),
                    "resolved_model_path": str(candidate),
                },
            )
            return candidate

        available_names = ", ".join(model.name for model in available_models)
        raise ModelNotLoadedError(
            f"Model not found: {configured_path}. Available models: {available_names}"
        )

    def get_model(self) -> Llama:
        if self._model is None:
            with self._lock:
                if self._model is None:
                    self._model = self._load()

        return self._model

    def _load(self) -> Llama:
        resolved_model_path = self._resolve_model_path()
        self._resolved_model_path = resolved_model_path

        threads = self._thread_count()

        self.logger.info(
            "loading_model",
            extra={
                "model_path": str(resolved_model_path),
                "configured_model_path": str(self.settings.model_path),
                "context": self.settings.model_context,
                "threads": threads,
                "gpu_layers": self.settings.model_gpu_layers,
            },
        )

        return Llama(
            model_path=str(resolved_model_path),
            n_ctx=self.settings.model_context,
            n_threads=threads,
            n_gpu_layers=self.settings.model_gpu_layers,
            embedding=True,
            chat_format="chatml",
            verbose=False,
        )

    def info(self) -> dict[str, Any]:
        model_path = self._resolved_model_path or self.settings.model_path
        return {
            "loaded": self.is_loaded,
            "model_path": str(model_path),
            "configured_model_path": str(self.settings.model_path),
            "loaded_model": (
                self.model_name
                if model_path.exists()
                else None
            ),
            "context": self.settings.model_context,
            "threads": self.settings.model_threads,
            "gpu_layers": self.settings.model_gpu_layers,
        }
