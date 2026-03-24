import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/project_db",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET = os.getenv("JWT_SECRET", "change-me-in-production")
    EMBEDDING_SERVICE_URL = os.getenv("EMBEDDING_SERVICE_URL", "http://localhost:5003")

    S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL", "http://localhost:9000")
    S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY", "minioadmin")
    S3_SECRET_KEY = os.getenv("S3_SECRET_KEY", "minioadmin")
    S3_BUCKET = os.getenv("S3_BUCKET", "platform-rag")
    S3_REGION = os.getenv("S3_REGION", "us-east-1")
