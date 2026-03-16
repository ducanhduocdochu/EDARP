import uuid
from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def _utcnow():
    return datetime.now(timezone.utc)


class Project(db.Model):
    __tablename__ = "projects"

    EMBEDDING_MODELS = [
        "vietnamese-embedding",
        "bge-large-en-v1.5",
        "bge-base-en-v1.5",
        "bge-small-en-v1.5",
        "multilingual-e5-large",
        "multilingual-e5-base",
    ]

    LLM_MODELS = [
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4-turbo",
        "gpt-3.5-turbo",
        "claude-3.5-sonnet",
        "claude-3-haiku",
        "gemini-1.5-pro",
        "gemini-1.5-flash",
    ]

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = db.Column(db.String(36), nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    embedding_model = db.Column(db.String(100), nullable=False, default="vietnamese-embedding")
    llm_model = db.Column(db.String(100), nullable=False, default="gpt-4o-mini")
    created_by = db.Column(db.String(36), nullable=False)
    created_at = db.Column(db.DateTime, default=_utcnow)
    status = db.Column(db.String(50), default="active")

    api_keys = db.relationship("ApiKey", back_populates="project", lazy="dynamic")
    documents = db.relationship("Document", back_populates="project", lazy="dynamic")


class ApiKey(db.Model):
    __tablename__ = "api_keys"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = db.Column(db.String(36), db.ForeignKey("projects.id"), nullable=False)
    key_hash = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=_utcnow)
    status = db.Column(db.String(50), default="active")

    project = db.relationship("Project", back_populates="api_keys")


class Document(db.Model):
    __tablename__ = "documents"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = db.Column(db.String(36), db.ForeignKey("projects.id"), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    s3_path = db.Column(db.Text, nullable=True)
    status = db.Column(
        db.String(50),
        default="uploaded",
    )
    created_at = db.Column(db.DateTime, default=_utcnow)

    project = db.relationship("Project", back_populates="documents")

    __table_args__ = (
        db.CheckConstraint(
            "status IN ('uploaded', 'processing', 'indexed', 'failed')",
            name="ck_document_status",
        ),
    )
