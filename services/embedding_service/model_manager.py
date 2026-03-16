import threading
from typing import Optional

import torch
from transformers import AutoModel, AutoTokenizer

from .config import DEVICE, MAX_LENGTH, MODEL_REGISTRY


class ModelManager:
    """Lazy-loads and caches HuggingFace embedding models."""

    def __init__(self):
        self._models: dict[str, tuple] = {}
        self._lock = threading.Lock()

    def _resolve_hf_name(self, model_key: str) -> str:
        return MODEL_REGISTRY.get(model_key, model_key)

    def _load(self, model_key: str):
        hf_name = self._resolve_hf_name(model_key)
        tokenizer = AutoTokenizer.from_pretrained(hf_name)
        model = AutoModel.from_pretrained(hf_name)
        model.to(DEVICE)
        model.eval()
        return tokenizer, model

    def get(self, model_key: str) -> tuple:
        if model_key not in self._models:
            with self._lock:
                if model_key not in self._models:
                    self._models[model_key] = self._load(model_key)
        return self._models[model_key]

    def encode(self, text: str, model_key: str) -> list[float]:
        tokenizer, model = self.get(model_key)
        inputs = tokenizer(
            text,
            padding=True,
            truncation=True,
            max_length=MAX_LENGTH,
            add_special_tokens=True,
            return_tensors="pt",
        )
        inputs = {k: v.to(DEVICE) for k, v in inputs.items()}
        with torch.no_grad():
            outputs = model(**inputs)
        embedding = outputs.last_hidden_state.mean(dim=1).squeeze(0)
        return embedding.cpu().numpy().tolist()

    def encode_batch(self, texts: list[str], model_key: str) -> list[list[float]]:
        tokenizer, model = self.get(model_key)
        inputs = tokenizer(
            texts,
            padding=True,
            truncation=True,
            max_length=MAX_LENGTH,
            add_special_tokens=True,
            return_tensors="pt",
        )
        inputs = {k: v.to(DEVICE) for k, v in inputs.items()}
        with torch.no_grad():
            outputs = model(**inputs)
        embeddings = outputs.last_hidden_state.mean(dim=1)
        return embeddings.cpu().numpy().tolist()

    @property
    def loaded_models(self) -> list[str]:
        return list(self._models.keys())


manager = ModelManager()
