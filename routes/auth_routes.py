from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db,limiter
from models.user import User
import jwt
from datetime import datetime, timedelta

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "JSON data is required"
        }), 400

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not name or not email or not password:
        return jsonify({
            "success": False,
            "message": "Name, email and password are required"
        }), 400

    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        return jsonify({
            "success": False,
            "message": "Email already registered"
        }), 409

    hashed_password = generate_password_hash(password)

    new_user = User(
        name=name,
        email=email,
        password=hashed_password
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "User registered successfully"
    }), 201

@auth_bp.route("/login", methods=["POST"])
@limiter.limit("5 per minute")
def login():
    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "JSON data is required"
        }), 400

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({
            "success": False,
            "message": "Email and password are required"
        }), 400

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({
            "success": False,
            "message": "Invalid email or password"
        }), 401

    if not check_password_hash(user.password, password):
        return jsonify({
            "success": False,
            "message": "Invalid email or password"
        }), 401

    token = jwt.encode(
        {
            "user_id": user.id,
            "email": user.email,
            "exp": datetime.utcnow() + timedelta(hours=2)
        },
        current_app.config["SECRET_KEY"],
        algorithm="HS256"
    )

    return jsonify({
        "success": True,
        "message": "Login successful",
        "token": token
    }), 200