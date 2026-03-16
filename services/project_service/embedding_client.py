import requests
from flask import current_app


def get_embedding_url():
    return current_app.config.get("EMBEDDING_SERVICE_URL", "http://localhost:5003")


def vectorize(text: str, model: str | None = None) -> dict:
    url = f"{get_embedding_url()}/vectorize"
    payload = {"text": text}
    if model:
        payload["model"] = model
    resp = requests.post(url, json=payload, timeout=120)
    resp.raise_for_status()
    return resp.json()


def vectorize_batch(texts: list[str], model: str | None = None) -> dict:
    url = f"{get_embedding_url()}/vectorize/batch"
    payload = {"texts": texts}
    if model:
        payload["model"] = model
    resp = requests.post(url, json=payload, timeout=300)
    resp.raise_for_status()
    return resp.json()


def list_models() -> dict:
    url = f"{get_embedding_url()}/models"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp.json()
