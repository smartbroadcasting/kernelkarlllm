import time

from fastapi import APIRouter, Request

from api.schemas import EmbeddingRequest, EmbeddingResponse

router = APIRouter(tags=["embeddings"])


@router.post("/embed", response_model=EmbeddingResponse)
async def embed(payload: EmbeddingRequest, request: Request) -> EmbeddingResponse:
    start = time.perf_counter()
    embedding = request.app.state.backend.embed(payload.text)
    request.app.state.logger.info(
        "llm_embedding_completed",
        extra={"duration_ms": round((time.perf_counter() - start) * 1000, 2)},
    )
    return EmbeddingResponse(embedding=embedding)
