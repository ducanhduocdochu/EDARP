from flask import Blueprint, g, jsonify, request

from ..embedding_client import list_models as list_embedding_models
from ..models import Project, db
from ..utils import login_required

projects_bp = Blueprint("projects", __name__, url_prefix="/projects")


def _project_to_dict(p):
    return {
        "id": p.id,
        "tenant_id": p.tenant_id,
        "name": p.name,
        "embedding_model": p.embedding_model,
        "llm_model": p.llm_model,
        "created_by": p.created_by,
        "status": p.status,
        "created_at": p.created_at.isoformat(),
    }


@projects_bp.route("/models", methods=["GET"])
@login_required
def list_models():
    """Return available embedding and LLM models for the UI."""
    try:
        emb_data = list_embedding_models()
        embedding_models = list(emb_data.get("available", {}).keys())
    except Exception:
        embedding_models = Project.EMBEDDING_MODELS

    return jsonify({
        "embedding_models": embedding_models,
        "llm_models": Project.LLM_MODELS,
    })


@projects_bp.route("", methods=["POST"])
@login_required
def create_project():
    data = request.get_json(silent=True) or {}
    name = data.get("name")
    embedding_model = data.get("embedding_model", "vietnamese-embedding")
    llm_model = data.get("llm_model", "gpt-4o-mini")

    if not name:
        return jsonify({"error": "name is required"}), 400

    if embedding_model not in Project.EMBEDDING_MODELS:
        return jsonify({"error": f"Invalid embedding_model. Choose from: {Project.EMBEDDING_MODELS}"}), 400

    if llm_model not in Project.LLM_MODELS:
        return jsonify({"error": f"Invalid llm_model. Choose from: {Project.LLM_MODELS}"}), 400

    project = Project(
        tenant_id=g.current_tenant_id,
        name=name,
        embedding_model=embedding_model,
        llm_model=llm_model,
        created_by=g.current_user_id,
    )
    db.session.add(project)
    db.session.commit()

    return jsonify(_project_to_dict(project)), 201


@projects_bp.route("", methods=["GET"])
@login_required
def list_projects():
    projects = Project.query.filter_by(tenant_id=g.current_tenant_id).all()
    return jsonify([_project_to_dict(p) for p in projects])


@projects_bp.route("/<project_id>", methods=["GET"])
@login_required
def get_project(project_id):
    project = Project.query.filter_by(
        id=project_id, tenant_id=g.current_tenant_id
    ).first()
    if not project:
        return jsonify({"error": "Project not found"}), 404

    return jsonify(_project_to_dict(project))


@projects_bp.route("/<project_id>", methods=["PUT"])
@login_required
def update_project(project_id):
    project = Project.query.filter_by(
        id=project_id, tenant_id=g.current_tenant_id
    ).first()
    if not project:
        return jsonify({"error": "Project not found"}), 404

    data = request.get_json(silent=True) or {}

    if "name" in data:
        project.name = data["name"]
    if "embedding_model" in data:
        if data["embedding_model"] not in Project.EMBEDDING_MODELS:
            return jsonify({"error": f"Invalid embedding_model. Choose from: {Project.EMBEDDING_MODELS}"}), 400
        project.embedding_model = data["embedding_model"]
    if "llm_model" in data:
        if data["llm_model"] not in Project.LLM_MODELS:
            return jsonify({"error": f"Invalid llm_model. Choose from: {Project.LLM_MODELS}"}), 400
        project.llm_model = data["llm_model"]

    db.session.commit()
    return jsonify(_project_to_dict(project))
