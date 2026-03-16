import logging

import requests
from fastapi import Depends, FastAPI, HTTPException, Request

from .auth import get_current_user, get_token
from .config import LLM_API_URL, VECTORIZE_URL
from .rag_pipeline import run_rag_pipeline
from .schemas import ContextChunk, QueryRequest, QueryResponse
from .weaviate_client import get_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Query Service (RAG)",
    version="1.0.0",
)


@app.get("/healthz")
async def health_check():
    return {"status": "ok"}


@app.get("/readyz")
async def readiness_check():
    errors = []
    try:
        get_client().schema.get()
    except Exception:
        errors.append("weaviate")
    try:
        requests.get(VECTORIZE_URL.replace("/vectorize", "/health"), timeout=5)
    except Exception:
        errors.append("embedding_service")
    try:
        requests.get(LLM_API_URL.replace("/api/generate", "/"), timeout=5)
    except Exception:
        errors.append("llm_api (optional)")

    if "weaviate" in errors or "embedding_service" in errors:
        raise HTTPException(status_code=503, detail=f"Not ready: {errors}")
    return {"status": "ready", "warnings": errors}


@app.post("/query/{project_id}", response_model=QueryResponse)
async def query(
    project_id: str,
    body: QueryRequest,
    request: Request,
    user: dict = Depends(get_current_user),
):
    token = get_token(request)

    try:
        result = await run_rag_pipeline(
            project_id=project_id,
            query_str=body.query,
            token=token,
            top_k=body.top_k,
            max_new_tokens=body.max_new_tokens,
            temperature=body.temperature,
        )
    except Exception as e:
        logger.error(f"RAG pipeline error: {e}")
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

    return QueryResponse(
        answer=result["answer"],
        query=result["query"],
        context=[
            ContextChunk(
                content=c["content"],
                title=c.get("title", ""),
                score=c["score"],
            )
            for c in result["context"]
        ],
        llm_model=result["llm_model"],
        embedding_model=result["embedding_model"],
    )
