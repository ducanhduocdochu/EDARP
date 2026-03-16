from typing import Optional

from pydantic import BaseModel, Field


class TextRequest(BaseModel):
    text: str
    model: Optional[str] = None


class BatchTextRequest(BaseModel):
    texts: list[str] = Field(..., min_length=1)
    model: Optional[str] = None


class EmbeddingResponse(BaseModel):
    vector: list[float]
    model: str
    dimension: int


class BatchEmbeddingResponse(BaseModel):
    vectors: list[list[float]]
    model: str
    dimension: int
    count: int


class ModelsResponse(BaseModel):
    available: dict[str, str]
    default: str
    loaded: list[str]
