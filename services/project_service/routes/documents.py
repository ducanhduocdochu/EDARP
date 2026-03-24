from flask import Blueprint, g, jsonify, request

from ..embedding_client import vectorize, vectorize_batch
from ..models import Document, Project, db
from ..s3_client import delete_file, generate_presigned_url, upload_file
from ..utils import login_required

documents_bp = Blueprint("documents", __name__)


def _doc_to_dict(d, include_download=False):
    result = {
        "id": d.id,
        "project_id": d.project_id,
        "file_name": d.file_name,
        "s3_path": d.s3_path,
        "status": d.status,
        "created_at": d.created_at.isoformat(),
    }
    if include_download and d.s3_path:
        result["download_url"] = generate_presigned_url(d.s3_path)
    return result


@documents_bp.route("/projects/<project_id>/documents", methods=["POST"])
@login_required
def upload_document(project_id):
    """Upload a file to S3 under /{tenant_id}/{project_id}/ and create document record."""
    project = Project.query.filter_by(
        id=project_id, tenant_id=g.current_tenant_id
    ).first()
    if not project:
        return jsonify({"error": "Project not found"}), 404

    if "file" not in request.files:
        return jsonify({"error": "file is required (multipart/form-data)"}), 400

    file = request.files["file"]
    if not file.filename:
        return jsonify({"error": "file is empty"}), 400

    try:
        s3_path = upload_file(
            file_obj=file,
            tenant_id=g.current_tenant_id,
            project_id=project.id,
            file_name=file.filename,
        )
    except Exception as e:
        return jsonify({"error": f"S3 upload failed: {str(e)}"}), 502

    doc = Document(
        project_id=project.id,
        file_name=file.filename,
        s3_path=s3_path,
        status="uploaded",
    )
    db.session.add(doc)
    db.session.commit()

    return jsonify(_doc_to_dict(doc, include_download=True)), 201


@documents_bp.route("/projects/<project_id>/documents", methods=["GET"])
@login_required
def list_documents(project_id):
    project = Project.query.filter_by(
        id=project_id, tenant_id=g.current_tenant_id
    ).first()
    if not project:
        return jsonify({"error": "Project not found"}), 404

    docs = Document.query.filter_by(project_id=project.id).all()
    return jsonify([_doc_to_dict(d, include_download=True) for d in docs])


@documents_bp.route("/documents/<document_id>", methods=["GET"])
@login_required
def get_document(document_id):
    doc = Document.query.get(document_id)
    if not doc:
        return jsonify({"error": "Document not found"}), 404

    project = Project.query.filter_by(
        id=doc.project_id, tenant_id=g.current_tenant_id
    ).first()
    if not project:
        return jsonify({"error": "Document not found"}), 404

    return jsonify(_doc_to_dict(doc, include_download=True))


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

    try:
        delete_file(doc.s3_path)
    except Exception:
        pass

    db.session.delete(doc)
    db.session.commit()

    return jsonify({"message": "Document deleted"}), 200


@documents_bp.route("/projects/<project_id>/documents/embed", methods=["POST"])
@login_required
def embed_text(project_id):
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
