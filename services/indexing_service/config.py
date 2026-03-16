import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

WEAVIATE_URL = os.getenv("WEAVIATE_URL", "http://localhost:8080")
VECTORIZE_URL = os.getenv("VECTORIZE_URL", "http://localhost:5003/vectorize")
PROJECT_SERVICE_URL = os.getenv("PROJECT_SERVICE_URL", "http://localhost:5002")
JWT_SECRET = os.getenv("JWT_SECRET", "change-me-in-production")
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "5004"))
