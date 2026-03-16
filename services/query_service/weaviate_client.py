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
    safe = re.sub(r"[^a-zA-Z0-9]", "", project_id)
    return f"Project_{safe}"


def search_vectors(
    project_id: str, vector: list[float], top_k: int = 3
) -> list[dict]:
    client = get_client()
    name = collection_name(project_id)

    result = (
        client.query
        .get(name, ["content", "title", "doc_metadata"])
        .with_near_vector({"vector": vector})
        .with_limit(top_k)
        .with_additional(["distance", "certainty"])
        .do()
    )

    hits = result.get("data", {}).get("Get", {}).get(name, [])
    results = []
    for hit in hits:
        distance = hit.get("_additional", {}).get("distance", 1.0)
        certainty = hit.get("_additional", {}).get("certainty", 0.0)
        results.append({
            "content": hit.get("content", ""),
            "title": hit.get("title", ""),
            "score": round(float(certainty) if certainty else 1.0 - float(distance), 4),
        })
    return results
