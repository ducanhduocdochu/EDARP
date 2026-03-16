import hashlib
import secrets
from functools import wraps

import jwt
from flask import current_app, g, jsonify, request


def hash_key(raw: str) -> str:
    return hashlib.sha256(raw.encode()).hexdigest()


def generate_raw_key() -> str:
    return secrets.token_urlsafe(32)


def decode_access_token(token: str) -> dict:
    return jwt.decode(
        token, current_app.config["JWT_SECRET"], algorithms=["HS256"]
    )


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401
        token = auth_header.split(" ", 1)[1]
        try:
            payload = decode_access_token(token)
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        g.current_user_id = payload["sub"]
        g.current_tenant_id = payload["tenant_id"]
        g.current_role = payload["role"]
        return f(*args, **kwargs)

    return wrapper
