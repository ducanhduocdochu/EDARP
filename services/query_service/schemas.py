from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    query: str
    top_k: int = Field(default=3, ge=1, le=20)
    max_new_tokens: int | None = None
    temperature: float | None = None


class ContextChunk(BaseModel):
    content: str
    title: str
    score: float


class QueryResponse(BaseModel):
    answer: str
    query: str
    context: list[ContextChunk]
    llm_model: str
    embedding_model: str
