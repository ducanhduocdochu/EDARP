from pydantic import BaseModel, Field


class IndexTextRequest(BaseModel):
    text: str
    metadata: dict = Field(default_factory=dict)


class IndexBatchRequest(BaseModel):
    documents: list[dict] = Field(
        ...,
        min_length=1,
        description="List of dicts with 'title' and 'context' fields",
    )


class SearchRequest(BaseModel):
    query: str
    top_k: int = Field(default=5, ge=1, le=100)


class SearchResult(BaseModel):
    content: str
    score: float
    metadata: dict = Field(default_factory=dict)


class SearchResponse(BaseModel):
    results: list[SearchResult]
    query: str
    model: str
    total: int


class IndexStatusResponse(BaseModel):
    project_id: str
    collection: str
    document_count: int
