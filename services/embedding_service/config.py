import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

MODEL_REGISTRY: dict[str, str] = {
    "vietnamese-embedding": "dangvantuan/vietnamese-embedding",
    "bge-large-en-v1.5": "BAAI/bge-large-en-v1.5",
    "bge-base-en-v1.5": "BAAI/bge-base-en-v1.5",
    "bge-small-en-v1.5": "BAAI/bge-small-en-v1.5",
    "multilingual-e5-large": "intfloat/multilingual-e5-large",
    "multilingual-e5-base": "intfloat/multilingual-e5-base",
}

DEFAULT_MODEL = os.getenv("DEFAULT_EMBEDDING_MODEL", "vietnamese-embedding")
MAX_LENGTH = int(os.getenv("MAX_TOKEN_LENGTH", "512"))
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "5003"))
DEVICE = os.getenv("DEVICE", "cpu")
