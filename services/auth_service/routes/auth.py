from datetime import datetime, timedelta, timezone

from flask import Blueprint, current_app, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

from ..models import RefreshToken, Tenant, User, db
from ..utils import (
    create_access_token,
    generate_raw_token,
    hash_token,
    login_required,
)
from flask import g

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    """Create a new tenant + admin user."""
    data = request.get_json(silent=True) or {}
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not all([name, email, password]):
        return jsonify({"error": "name, email and password are required"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 409

    tenant = Tenant(name=name, admin_email=email)
    db.session.add(tenant)
    db.session.flush()

    user = User(
        tenant_id=tenant.id,
        email=email,
        password_hash=generate_password_hash(password),
        role="admin",
    )
    db.session.add(user)
    db.session.commit()

    return jsonify({
        "tenant_id": tenant.id,
        "user_id": user.id,
        "email": user.email,
        "role": user.role,
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    password = data.get("password")

    if not all([email, password]):
        return jsonify({"error": "email and password are required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid credentials"}), 401

    access_token = create_access_token(user.id, user.tenant_id, user.role)

    raw_refresh = generate_raw_token()
    refresh_token = RefreshToken(
        user_id=user.id,
        token_hash=hash_token(raw_refresh),
        expires_at=datetime.now(timezone.utc)
        + timedelta(days=current_app.config["JWT_REFRESH_EXPIRES_DAYS"]),
    )
    db.session.add(refresh_token)
    db.session.commit()

    return jsonify({
        "access_token": access_token,
        "refresh_token": raw_refresh,
        "token_type": "Bearer",
    })


@auth_bp.route("/refresh", methods=["POST"])
def refresh():
    data = request.get_json(silent=True) or {}
    raw_refresh = data.get("refresh_token")
    if not raw_refresh:
        return jsonify({"error": "refresh_token is required"}), 400

    hashed = hash_token(raw_refresh)
    token_row = RefreshToken.query.filter_by(token_hash=hashed).first()

    if not token_row:
        return jsonify({"error": "Invalid refresh token"}), 401
    if token_row.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        db.session.delete(token_row)
        db.session.commit()
        return jsonify({"error": "Refresh token expired"}), 401

    user = User.query.get(token_row.user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    db.session.delete(token_row)

    new_raw = generate_raw_token()
    new_token = RefreshToken(
        user_id=user.id,
        token_hash=hash_token(new_raw),
        expires_at=datetime.now(timezone.utc)
        + timedelta(days=current_app.config["JWT_REFRESH_EXPIRES_DAYS"]),
    )
    db.session.add(new_token)
    db.session.commit()

    access_token = create_access_token(user.id, user.tenant_id, user.role)
    return jsonify({
        "access_token": access_token,
        "refresh_token": new_raw,
        "token_type": "Bearer",
    })


@auth_bp.route("/me", methods=["GET"])
@login_required
def me():
    user = User.query.get(g.current_user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({
        "id": user.id,
        "tenant_id": user.tenant_id,
        "email": user.email,
        "role": user.role,
        "status": user.status,
        "created_at": user.created_at.isoformat(),
    })
