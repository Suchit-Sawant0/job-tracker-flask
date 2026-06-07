from functools import wraps
from flask import request, jsonify, current_app
import jwt
from models.user import User


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return jsonify({
                "success": False,
                "message": "Token is missing"
            }), 401

        try:
            parts = auth_header.split(" ")

            if len(parts) != 2 or parts[0] != "Bearer":
                return jsonify({
                    "success": False,
                    "message": "Invalid token format. Use: Bearer your_token"
                }), 401

            token = parts[1]

            decoded = jwt.decode(
                token,
                current_app.config["SECRET_KEY"],
                algorithms=["HS256"]
            )

            current_user = User.query.get(decoded["user_id"])

            if not current_user:
                return jsonify({
                    "success": False,
                    "message": "User not found"
                }), 401

        except jwt.ExpiredSignatureError:
            return jsonify({
                "success": False,
                "message": "Token expired"
            }), 401

        except jwt.InvalidTokenError:
            return jsonify({
                "success": False,
                "message": "Invalid token"
            }), 401

        return f(current_user, *args, **kwargs)

    return decorated


def api_key_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get("x-api-key")

        if not api_key:
            return jsonify({
                "success": False,
                "message": "API key is missing"
            }), 401

        if api_key != current_app.config["API_KEY"]:
            return jsonify({
                "success": False,
                "message": "Invalid API key"
            }), 403

        return f(*args, **kwargs)

    return decorated