from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from .config import DEFAULT_MODEL, MODEL_REGISTRY
from .model_manager import manager
from .schemas import (
    BatchEmbeddingResponse,
    BatchTextRequest,
    EmbeddingResponse,
    ModelsResponse,
    TextRequest,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    manager.get(DEFAULT_MODEL)
    yield


app = FastAPI(
    title="Embedding Service",
    description="Text embedding service with multiple HuggingFace models",
    version="1.0.0",
    lifespan=lifespan,
)


def _resolve_model(requested: str | None) -> str:
    model_key = requested or DEFAULT_MODEL
    if model_key not in MODEL_REGISTRY and requested is not None:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown model '{model_key}'. Available: {list(MODEL_REGISTRY.keys())}",
        )
    return model_key


@app.get("/health")
async def health():
    return {"status": "ok", "loaded_models": manager.loaded_models}


@app.get("/models", response_model=ModelsResponse)
async def list_models():
    return ModelsResponse(
        available=MODEL_REGISTRY,
        default=DEFAULT_MODEL,
        loaded=manager.loaded_models,
    )


@app.post("/vectorize", response_model=EmbeddingResponse)
async def vectorize(request: TextRequest):
    model_key = _resolve_model(request.model)
    try:
        vector = manager.encode(request.text, model_key)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embedding failed: {str(e)}")
    return EmbeddingResponse(
        vector=vector,
        model=model_key,
        dimension=len(vector),
    )


@app.post("/vectorize/batch", response_model=BatchEmbeddingResponse)
async def vectorize_batch(request: BatchTextRequest):
    model_key = _resolve_model(request.model)
    try:
        vectors = manager.encode_batch(request.texts, model_key)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch embedding failed: {str(e)}")
    return BatchEmbeddingResponse(
        vectors=vectors,
        model=model_key,
        dimension=len(vectors[0]) if vectors else 0,
        count=len(vectors),
    )
