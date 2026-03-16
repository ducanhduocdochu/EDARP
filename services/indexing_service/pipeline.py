import logging

import requests
from pyvi.ViTokenizer import tokenize

from .config import PROJECT_SERVICE_URL, VECTORIZE_URL

logger = logging.getLogger(__name__)


def get_project_info(project_id: str, token: str) -> dict:
    resp = requests.get(
        f"{PROJECT_SERVICE_URL}/projects/{project_id}",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()


def vectorize_text(text: str, model: str | None = None) -> list[float]:
    payload: dict = {"text": text}
    if model:
        payload["model"] = model
    resp = requests.post(VECTORIZE_URL, json=payload, timeout=120)
    resp.raise_for_status()
    return resp.json()["vector"]


def vectorize_batch(texts: list[str], model: str | None = None) -> list[list[float]]:
    payload: dict = {"texts": texts}
    if model:
        payload["model"] = model
    url = VECTORIZE_URL.replace("/vectorize", "/vectorize/batch")
    resp = requests.post(url, json=payload, timeout=300)
    resp.raise_for_status()
    return resp.json()["vectors"]


def tokenize_vi(text: str) -> str:
    return tokenize(text)


def process_json_documents(json_data: list[dict]) -> list[dict]:
    """Convert raw JSON items into structured documents with tokenized content."""
    documents = []
    for item in json_data:
        title = item.get("title", "")
        context = item.get("context", "")
        combined = f"Trích dẫn ở: {title} \n Nội dung như sau: {context}"
        tokenized = tokenize_vi(combined)
        documents.append({
            "title": title,
            "content": combined,
            "tokenized": tokenized,
            "metadata": {k: v for k, v in item.items() if k not in ("title", "context")},
        })
    return documents
