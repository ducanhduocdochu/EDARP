from flask import Blueprint, g, jsonify, request
from werkzeug.security import generate_password_hash

from ..models import User, db
from ..utils import admin_required, login_required

users_bp = Blueprint("users", __name__, url_prefix="/users")


@users_bp.route("", methods=["POST"])
@admin_required
def create_user():
    """Admin creates a member user under the same tenant."""
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    password = data.get("password")
    role = data.get("role", "member")

    if not all([email, password]):
        return jsonify({"error": "email and password are required"}), 400

    if role not in ("admin", "member"):
        return jsonify({"error": "role must be 'admin' or 'member'"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 409

    user = User(
        tenant_id=g.current_tenant_id,
        email=email,
        password_hash=generate_password_hash(password),
        role=role,
    )
    db.session.add(user)
    db.session.commit()

    return jsonify({
        "id": user.id,
        "tenant_id": user.tenant_id,
        "email": user.email,
        "role": user.role,
        "status": user.status,
    }), 201


@users_bp.route("", methods=["GET"])
@login_required
def list_users():
    """List all users in the current tenant."""
    users = User.query.filter_by(tenant_id=g.current_tenant_id).all()
    return jsonify([
        {
            "id": u.id,
            "email": u.email,
            "role": u.role,
            "status": u.status,
            "created_at": u.created_at.isoformat(),
        }
        for u in users
    ])
