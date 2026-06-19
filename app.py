import json
import logging
import sys
import time
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from api.chat import router as chat_router
from api.embeddings import router as embeddings_router
from api.generate import router as generate_router
from api.health import router as health_router
from api.models import router as models_router
from config.settings import get_settings
from services.llm_service import create_backend
from services.model_loader import ModelNotLoadedError


class JsonFormatter(logging.Formatter):
    reserved = {
        "args",
        "asctime",
        "created",
        "exc_info",
        "exc_text",
        "filename",
        "funcName",
        "levelname",
        "levelno",
        "lineno",
        "module",
        "msecs",
        "message",
        "msg",
        "name",
        "pathname",
        "process",
        "processName",
        "relativeCreated",
        "stack_info",
        "thread",
        "threadName",
    }

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
        }
        for key, value in record.__dict__.items():
            if key not in self.reserved and not key.startswith("_"):
                payload[key] = value
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def configure_logging(level: str) -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        handlers=[handler],
        force=True,
    )


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    configure_logging(settings.log_level)
    logger = logging.getLogger("kernel_karl_llm")
    app.state.settings = settings
    app.state.logger = logger
    app.state.backend = create_backend(settings, logger)
    logger.info(
        "service_started",
        extra={"backend": settings.backend, "model_path": str(settings.model_path)},
    )
    yield
    logger.info("service_stopped")


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        lifespan=lifespan,
    )

    @app.middleware("http")
    async def request_logging(request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        request.app.state.logger.info(
            "request_completed",
            extra={
                "endpoint": request.url.path,
                "method": request.method,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            },
        )
        return response

    @app.exception_handler(ModelNotLoadedError)
    async def model_not_loaded_handler(
        request: Request, exc: ModelNotLoadedError
    ) -> JSONResponse:
        request.app.state.logger.error(
            "model_not_loaded",
            extra={"endpoint": request.url.path, "message": str(exc)},
        )
        return JSONResponse(
            status_code=503,
            content={"error": True, "message": str(exc)},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={"error": True, "message": "Invalid request payload"},
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_error_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        detail = exc.detail if isinstance(exc.detail, str) else "HTTP error"
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": True, "message": detail},
        )

    @app.exception_handler(Exception)
    async def internal_error_handler(request: Request, exc: Exception) -> JSONResponse:
        request.app.state.logger.exception(
            "internal_error",
            extra={"endpoint": request.url.path},
        )
        return JSONResponse(
            status_code=500,
            content={"error": True, "message": "Internal server error"},
        )

    app.include_router(health_router)
    app.include_router(models_router)
    app.include_router(generate_router)
    app.include_router(chat_router)
    app.include_router(embeddings_router)
    return app


app = create_app()
