import json
import logging

from fastapi import Depends, FastAPI, File, HTTPException, Request, UploadFile

from .auth import get_current_user
from .config import VECTORIZE_URL
from .pipeline import (
    get_project_info,
    process_json_documents,
    vectorize_batch,
    vectorize_text,
)
from .schemas import (
    IndexBatchRequest,
    IndexStatusResponse,
    IndexTextRequest,
    SearchRequest,
    SearchResponse,
    SearchResult,
)
from .weaviate_manager import (
    count_objects,
    delete_collection,
    ensure_collection,
    get_client,
    import_objects,
    search,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Indexing Pipeline Service",
    version="1.0.0",
)


def _get_token(request: Request) -> str:
    auth = request.headers.get("Authorization", "")
    return auth.split(" ", 1)[1] if auth.startswith("Bearer ") else ""


def _get_embedding_model(project_id: str, token: str) -> str | None:
    """Fetch the embedding model configured for the project."""
    try:
        info = get_project_info(project_id, token)
        return info.get("embedding_model")
    except Exception:
        return None


# ---------- Health ----------

@app.get("/healthz")
async def health_check():
    return {"status": "ok"}


@app.get("/readyz")
async def readiness_check():
    try:
        get_client().schema.get()
        import requests as _req
        _req.get(VECTORIZE_URL.replace("/vectorize", "/health"), timeout=5)
        return {"status": "ready"}
    except Exception:
        raise HTTPException(status_code=503, detail="Service not ready")


# ---------- Index single text ----------

@app.post("/index/{project_id}/text")
async def index_text(
    project_id: str,
    body: IndexTextRequest,
    request: Request,
    user: dict = Depends(get_current_user),
):
    token = _get_token(request)
    model = _get_embedding_model(project_id, token)

    vector = vectorize_text(body.text, model=model)

    doc = {
        "title": body.metadata.get("title", ""),
        "content": body.text,
        "metadata": body.metadata,
    }
    imported = import_objects(project_id, [doc], [vector])

    return {
        "message": f"Indexed {imported} document(s)",
        "project_id": project_id,
        "model": model,
        "dimension": len(vector),
    }


# ---------- Index JSON file ----------

@app.post("/index/{project_id}/json")
async def index_json_file(
    project_id: str,
    request: Request,
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user),
):
    try:
        raw = await file.read()
        json_data = json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise HTTPException(status_code=400, detail="Invalid JSON file")

    if not isinstance(json_data, list) or len(json_data) == 0:
        raise HTTPException(
            status_code=400,
            detail="JSON must be a non-empty array of objects with 'title' and 'context'",
        )

    token = _get_token(request)
    model = _get_embedding_model(project_id, token)

    logger.info(f"Processing {len(json_data)} documents for project {project_id}")
    documents = process_json_documents(json_data)

    tokenized_texts = [d["tokenized"] for d in documents]

    logger.info(f"Vectorizing {len(tokenized_texts)} documents with model={model}")
    vectors = vectorize_batch(tokenized_texts, model=model)

    logger.info("Importing documents into Weaviate")
    imported = import_objects(project_id, documents, vectors)

    return {
        "message": f"Successfully indexed {imported}/{len(documents)} documents",
        "project_id": project_id,
        "model": model,
        "total_processed": len(documents),
        "total_imported": imported,
    }


# ---------- Index batch (JSON body) ----------

@app.post("/index/{project_id}/batch")
async def index_batch(
    project_id: str,
    body: IndexBatchRequest,
    request: Request,
    user: dict = Depends(get_current_user),
):
    token = _get_token(request)
    model = _get_embedding_model(project_id, token)

    documents = process_json_documents(body.documents)
    tokenized_texts = [d["tokenized"] for d in documents]
    vectors = vectorize_batch(tokenized_texts, model=model)
    imported = import_objects(project_id, documents, vectors)

    return {
        "message": f"Successfully indexed {imported}/{len(documents)} documents",
        "project_id": project_id,
        "model": model,
        "total_processed": len(documents),
        "total_imported": imported,
    }


# ---------- Search ----------

@app.post("/index/{project_id}/search", response_model=SearchResponse)
async def search_documents(
    project_id: str,
    body: SearchRequest,
    request: Request,
    user: dict = Depends(get_current_user),
):
    token = _get_token(request)
    model = _get_embedding_model(project_id, token)

    query_vector = vectorize_text(body.query, model=model)
    hits = search(project_id, query_vector, top_k=body.top_k)

    results = [
        SearchResult(
            content=h["content"],
            score=h["score"],
            metadata={"title": h.get("title", "")},
        )
        for h in hits
    ]

    return SearchResponse(
        results=results,
        query=body.query,
        model=model or "default",
        total=len(results),
    )


# ---------- Status / Management ----------

@app.get("/index/{project_id}/status", response_model=IndexStatusResponse)
async def index_status(
    project_id: str,
    user: dict = Depends(get_current_user),
):
    from .weaviate_manager import collection_name

    name = collection_name(project_id)
    count = count_objects(project_id)
    return IndexStatusResponse(
        project_id=project_id,
        collection=name,
        document_count=count,
    )


@app.delete("/index/{project_id}")
async def clear_index(
    project_id: str,
    user: dict = Depends(get_current_user),
):
    delete_collection(project_id)
    ensure_collection(project_id)
    return {
        "message": f"Index cleared for project {project_id}",
        "project_id": project_id,
    }
