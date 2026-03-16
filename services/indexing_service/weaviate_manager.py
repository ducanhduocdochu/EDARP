import logging
import re

import weaviate

from .config import WEAVIATE_URL

logger = logging.getLogger(__name__)

_client: weaviate.Client | None = None


def get_client() -> weaviate.Client:
    global _client
    if _client is None:
        _client = weaviate.Client(WEAVIATE_URL, startup_period=40)
    return _client


def collection_name(project_id: str) -> str:
    """Each project gets an isolated Weaviate class: Project_<hex>."""
    safe = re.sub(r"[^a-zA-Z0-9]", "", project_id)
    return f"Project_{safe}"


def ensure_collection(project_id: str):
    client = get_client()
    name = collection_name(project_id)

    existing = client.schema.get()
    existing_names = [c["class"] for c in existing.get("classes", [])]
    if name in existing_names:
        return name

    schema = {
        "class": name,
        "vectorizer": "none",
        "properties": [
            {"name": "content", "dataType": ["text"]},
            {"name": "title", "dataType": ["text"]},
            {"name": "doc_metadata", "dataType": ["text"]},
        ],
    }
    client.schema.create_class(schema)
    logger.info(f"Created Weaviate collection: {name}")
    return name


def delete_collection(project_id: str):
    client = get_client()
    name = collection_name(project_id)
    try:
        client.schema.delete_class(name)
        logger.info(f"Deleted Weaviate collection: {name}")
    except Exception:
        pass


def import_objects(project_id: str, documents: list[dict], vectors: list[list[float]]):
    """Import documents with pre-computed vectors into Weaviate."""
    client = get_client()
    name = ensure_collection(project_id)

    if len(documents) != len(vectors):
        raise ValueError(
            f"Document count ({len(documents)}) != vector count ({len(vectors)})"
        )

    imported = 0
    for i, doc in enumerate(documents):
        try:
            client.data_object.create(
                data_object={
                    "content": doc.get("content", ""),
                    "title": doc.get("title", ""),
                    "doc_metadata": str(doc.get("metadata", {})),
                },
                class_name=name,
                vector=vectors[i],
            )
            imported += 1
        except Exception as e:
            logger.error(f"Error importing document {i}: {e}")

    return imported


def search(project_id: str, vector: list[float], top_k: int = 5) -> list[dict]:
    client = get_client()
    name = collection_name(project_id)

    result = (
        client.query
        .get(name, ["content", "title", "doc_metadata"])
        .with_near_vector({"vector": vector})
        .with_limit(top_k)
        .with_additional(["distance"])
        .do()
    )

    hits = result.get("data", {}).get("Get", {}).get(name, [])
    results = []
    for hit in hits:
        distance = hit.get("_additional", {}).get("distance", 1.0)
        results.append({
            "content": hit.get("content", ""),
            "title": hit.get("title", ""),
            "score": round(1.0 - float(distance), 4),
            "metadata": hit.get("doc_metadata", "{}"),
        })
    return results


def count_objects(project_id: str) -> int:
    client = get_client()
    name = collection_name(project_id)
    try:
        result = client.query.aggregate(name).with_meta_count().do()
        return (
            result.get("data", {})
            .get("Aggregate", {})
            .get(name, [{}])[0]
            .get("meta", {})
            .get("count", 0)
        )
    except Exception:
        return 0
