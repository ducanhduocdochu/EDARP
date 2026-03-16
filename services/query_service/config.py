import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

WEAVIATE_URL = os.getenv("WEAVIATE_URL", "http://localhost:8080")
VECTORIZE_URL = os.getenv("VECTORIZE_URL", "http://localhost:5003/vectorize")
PROJECT_SERVICE_URL = os.getenv("PROJECT_SERVICE_URL", "http://localhost:5002")
LLM_API_URL = os.getenv("LLM_API_URL", "http://localhost:11434/api/generate")

JWT_SECRET = os.getenv("JWT_SECRET", "change-me-in-production")
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "5005"))

MAX_NEW_TOKENS = int(os.getenv("MAX_NEW_TOKENS", "512"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", "3"))
