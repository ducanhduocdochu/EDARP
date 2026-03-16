from flask import Blueprint, g, jsonify, request

from ..embedding_client import vectorize, vectorize_batch
from ..models import Document, Project, db
from ..utils import login_required

documents_bp = Blueprint("documents", __name__)


@documents_bp.route("/projects/<project_id>/documents", methods=["POST"])
@login_required
def create_document(project_id):
    project = Project.query.filter_by(
        id=project_id, tenant_id=g.current_tenant_id
    ).first()
    if not project:
        return jsonify({"error": "Project not found"}), 404

    data = request.get_json(silent=True) or {}
    file_name = data.get("file_name")
    s3_path = data.get("s3_path")

    if not file_name:
        return jsonify({"error": "file_name is required"}), 400

    doc = Document(
        project_id=project.id,
        file_name=file_name,
        s3_path=s3_path,
        status="uploaded",
    )
    db.session.add(doc)
    db.session.commit()

    return jsonify({
        "id": doc.id,
        "project_id": doc.project_id,
        "file_name": doc.file_name,
        "s3_path": doc.s3_path,
        "status": doc.status,
        "created_at": doc.created_at.isoformat(),
    }), 201


@documents_bp.route("/projects/<project_id>/documents", methods=["GET"])
@login_required
def list_documents(project_id):
    project = Project.query.filter_by(
        id=project_id, tenant_id=g.current_tenant_id
    ).first()
    if not project:
        return jsonify({"error": "Project not found"}), 404

    docs = Document.query.filter_by(project_id=project.id).all()
    return jsonify([
        {
            "id": d.id,
            "file_name": d.file_name,
            "s3_path": d.s3_path,
            "status": d.status,
            "created_at": d.created_at.isoformat(),
        }
        for d in docs
    ])


@documents_bp.route("/documents/<document_id>", methods=["DELETE"])
@login_required
def delete_document(document_id):
    doc = Document.query.get(document_id)
    if not doc:
        return jsonify({"error": "Document not found"}), 404

    project = Project.query.filter_by(
        id=doc.project_id, tenant_id=g.current_tenant_id
    ).first()
    if not project:
        return jsonify({"error": "Document not found"}), 404

    db.session.delete(doc)
    db.session.commit()

    return jsonify({"message": "Document deleted"}), 200


@documents_bp.route("/projects/<project_id>/documents/embed", methods=["POST"])
@login_required
def embed_text(project_id):
    """Embed a single text using the project's configured embedding model."""
    project = Project.query.filter_by(
        id=project_id, tenant_id=g.current_tenant_id
    ).first()
    if not project:
        return jsonify({"error": "Project not found"}), 404

    data = request.get_json(silent=True) or {}
    text = data.get("text")
    if not text:
        return jsonify({"error": "text is required"}), 400

    try:
        result = vectorize(text, model=project.embedding_model)
    except Exception as e:
        return jsonify({"error": f"Embedding service error: {str(e)}"}), 502

    return jsonify(result)


@documents_bp.route("/projects/<project_id>/documents/embed-batch", methods=["POST"])
@login_required
def embed_batch(project_id):
    """Embed multiple texts using the project's configured embedding model."""
    project = Project.query.filter_by(
        id=project_id, tenant_id=g.current_tenant_id
    ).first()
    if not project:
        return jsonify({"error": "Project not found"}), 404

    data = request.get_json(silent=True) or {}
    texts = data.get("texts")
    if not texts or not isinstance(texts, list):
        return jsonify({"error": "texts (list of strings) is required"}), 400

    try:
        result = vectorize_batch(texts, model=project.embedding_model)
    except Exception as e:
        return jsonify({"error": f"Embedding service error: {str(e)}"}), 502

    return jsonify(result)
