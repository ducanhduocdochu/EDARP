import asyncio
import logging

import requests
from pyvi.ViTokenizer import tokenize

from .config import (
    LLM_API_URL,
    MAX_NEW_TOKENS,
    PROJECT_SERVICE_URL,
    TEMPERATURE,
    VECTORIZE_URL,
)
from .weaviate_client import search_vectors

logger = logging.getLogger(__name__)

RAG_PROMPT_TEMPLATE = (
    "We have provided context information below.\n"
    "---------------------\n"
    "{context_str}\n"
    "---------------------\n"
    "Given this information, please answer the question: {query_str}\n"
)


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


def call_llm(
    prompt: str,
    llm_model: str,
    max_new_tokens: int = MAX_NEW_TOKENS,
    temperature: float = TEMPERATURE,
) -> str:
    """Call the LLM API. Supports OpenAI-compatible and Ollama-compatible APIs."""
    try:
        resp = requests.post(
            LLM_API_URL,
            json={
                "model": llm_model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": max_new_tokens,
                    "temperature": temperature,
                },
            },
            timeout=120,
            verify=False,
        )
        resp.raise_for_status()
        data = resp.json()
        if "response" in data:
            return data["response"]
        if "choices" in data:
            return data["choices"][0].get("message", {}).get("content", "")
        return str(data)
    except requests.exceptions.ConnectionError:
        logger.warning("LLM API not reachable, returning prompt-only fallback")
        return f"[LLM unavailable] Context was retrieved but LLM at {LLM_API_URL} is not reachable."
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        return f"[LLM error] {str(e)}"


def build_context_string(chunks: list[dict]) -> str:
    parts = []
    for chunk in chunks:
        title = chunk.get("title", "")
        content = chunk.get("content", "")
        score = chunk.get("score", 0)
        prefix = f"[{title}] (score: {score})" if title else f"(score: {score})"
        parts.append(f"{prefix}\n{content}")
    return "\n\n".join(parts)


async def run_rag_pipeline(
    project_id: str,
    query_str: str,
    token: str,
    top_k: int = 3,
    max_new_tokens: int | None = None,
    temperature: float | None = None,
) -> dict:
    """Full RAG pipeline: tokenize → vectorize → search → prompt → LLM."""

    project_info = await asyncio.to_thread(get_project_info, project_id, token)
    embedding_model = project_info.get("embedding_model")
    llm_model = project_info.get("llm_model", "gpt-4o-mini")

    logger.info(f"RAG query: project={project_id}, emb={embedding_model}, llm={llm_model}")

    tokenized_query = await asyncio.to_thread(tokenize, query_str)
    logger.info(f"Tokenized query: {tokenized_query}")

    query_vector = await asyncio.to_thread(vectorize_text, tokenized_query, embedding_model)
    logger.info(f"Query vectorized, dim={len(query_vector)}")

    chunks = await asyncio.to_thread(search_vectors, project_id, query_vector, top_k)
    logger.info(f"Found {len(chunks)} relevant chunks")

    context_str = build_context_string(chunks)

    prompt = RAG_PROMPT_TEMPLATE.format(
        context_str=context_str,
        query_str=query_str,
    )

    _max_tokens = max_new_tokens or MAX_NEW_TOKENS
    _temp = temperature if temperature is not None else TEMPERATURE

    answer = await asyncio.to_thread(call_llm, prompt, llm_model, _max_tokens, _temp)

    return {
        "answer": answer,
        "query": query_str,
        "context": chunks,
        "llm_model": llm_model,
        "embedding_model": embedding_model or "default",
    }
