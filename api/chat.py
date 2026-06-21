import time

from fastapi import APIRouter, Request

from api.schemas import ChatMessage, ChatRequest, ChatResponse

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest, request: Request) -> ChatResponse:
    settings = request.app.state.settings
    temperature = payload.temperature
    if temperature is None:
        temperature = settings.default_temperature
    max_tokens = payload.max_tokens
    if max_tokens is None:
        max_tokens = settings.default_max_tokens

    start = time.perf_counter()
    message = request.app.state.backend.chat(
        [item.model_dump() for item in payload.messages],
        temperature=temperature,
        max_tokens=max_tokens,
        min_p=payload.min_p,
        top_p=payload.top_p,
        top_k=payload.top_k,
    )
    request.app.state.logger.info(
        "llm_chat_completed",
        extra={"duration_ms": round((time.perf_counter() - start) * 1000, 2)},
    )
    return ChatResponse(message=ChatMessage(**message))
