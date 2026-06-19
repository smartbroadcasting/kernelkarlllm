import time

from fastapi import APIRouter, Request

from api.schemas import GenerateRequest, GenerateResponse

router = APIRouter(tags=["generate"])


@router.post("/generate", response_model=GenerateResponse)
async def generate(payload: GenerateRequest, request: Request) -> GenerateResponse:
    settings = request.app.state.settings
    temperature = payload.temperature
    if temperature is None:
        temperature = settings.default_temperature
    max_tokens = payload.max_tokens
    if max_tokens is None:
        max_tokens = settings.default_max_tokens

    start = time.perf_counter()
    text = request.app.state.backend.generate(
        payload.prompt,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    request.app.state.logger.info(
        "llm_generate_completed",
        extra={"duration_ms": round((time.perf_counter() - start) * 1000, 2)},
    )
    return GenerateResponse(text=text)
