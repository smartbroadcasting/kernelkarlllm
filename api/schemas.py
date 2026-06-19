from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    prompt: str = Field(..., min_length=1)
    temperature: float | None = Field(default=None, ge=0.0, le=2.0)
    max_tokens: int | None = Field(default=None, ge=1)


class GenerateResponse(BaseModel):
    text: str


class ChatMessage(BaseModel):
    role: str = Field(..., pattern="^(system|user|assistant)$")
    content: str = Field(..., min_length=1)


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(..., min_length=1)
    temperature: float | None = Field(default=None, ge=0.0, le=2.0)
    max_tokens: int | None = Field(default=None, ge=1)


class ChatResponse(BaseModel):
    message: ChatMessage


class EmbeddingRequest(BaseModel):
    text: str = Field(..., min_length=1)


class EmbeddingResponse(BaseModel):
    embedding: list[float]
