from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str = Field(..., pattern="^(system|user|assistant)$")
    content: str = Field(..., min_length=1)


class SamplingParams(BaseModel):
    temperature: float | None = Field(default=None, ge=0.0, le=2.0)
    max_tokens: int | None = Field(default=None, ge=1)
    min_p: float | None = Field(default=None, ge=0.0, le=1.0)
    top_p: float | None = Field(default=None, ge=0.0, le=1.0)
    top_k: int | None = Field(default=None, ge=1)


class ChatRequest(SamplingParams):
    messages: list[ChatMessage] = Field(..., min_length=1)


class GenerateRequest(SamplingParams):
    prompt: str = Field(..., min_length=1)


class GenerateResponse(BaseModel):
    text: str


class ChatResponse(BaseModel):
    message: ChatMessage


class EmbeddingRequest(BaseModel):
    text: str = Field(..., min_length=1)


class EmbeddingResponse(BaseModel):
    embedding: list[float]
