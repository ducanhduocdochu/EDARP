from flask import Blueprint, g, jsonify

from ..models import ApiKey, Project, db
from ..utils import generate_raw_key, hash_key, login_required

api_keys_bp = Blueprint("api_keys", __name__, url_prefix="/projects")


@api_keys_bp.route("/<project_id>/api-keys", methods=["POST"])
@login_required
def create_api_key(project_id):
    project = Project.query.filter_by(
        id=project_id, tenant_id=g.current_tenant_id
    ).first()
    if not project:
        return jsonify({"error": "Project not found"}), 404

    raw_key = generate_raw_key()
    api_key = ApiKey(
        project_id=project.id,
        key_hash=hash_key(raw_key),
    )
    db.session.add(api_key)
    db.session.commit()

    return jsonify({
        "id": api_key.id,
        "project_id": api_key.project_id,
        "key": raw_key,
        "status": api_key.status,
        "created_at": api_key.created_at.isoformat(),
    }), 201


@api_keys_bp.route("/<project_id>/api-keys", methods=["GET"])
@login_required
def list_api_keys(project_id):
    project = Project.query.filter_by(
        id=project_id, tenant_id=g.current_tenant_id
    ).first()
    if not project:
        return jsonify({"error": "Project not found"}), 404

    keys = ApiKey.query.filter_by(project_id=project.id).all()
    return jsonify([
        {
            "id": k.id,
            "project_id": k.project_id,
            "status": k.status,
            "created_at": k.created_at.isoformat(),
        }
        for k in keys
    ])
