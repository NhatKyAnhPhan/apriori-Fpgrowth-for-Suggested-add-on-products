from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity
)
import bcrypt

from database import db, User

auth_bp = Blueprint("auth", __name__)


# ─── Register ─────────────────────────────────────────────────────────────────

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username", "").strip()
    email    = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not username or not email or not password:
        return jsonify({"error": "Vui lòng điền đầy đủ thông tin."}), 400

    if len(password) < 6:
        return jsonify({"error": "Mật khẩu ít nhất 6 ký tự."}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email đã được sử dụng."}), 409

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username đã tồn tại."}), 409

    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    user = User(username=username, email=email, password_hash=password_hash)
    db.session.add(user)
    db.session.commit()

    access_token  = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    return jsonify({
        "message":       "Đăng ký thành công!",
        "user":          user.to_dict(),
        "access_token":  access_token,
        "refresh_token": refresh_token,
    }), 201


# ─── Login ────────────────────────────────────────────────────────────────────

@auth_bp.route("/login", methods=["POST"])
def login():
    data     = request.get_json()
    email    = data.get("email", "").strip().lower()
    password = data.get("password", "")

    user = User.query.filter_by(email=email).first()
    if not user or not bcrypt.checkpw(password.encode(), user.password_hash.encode()):
        return jsonify({"error": "Email hoặc mật khẩu không đúng."}), 401

    access_token  = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    return jsonify({
        "message":       "Đăng nhập thành công!",
        "user":          user.to_dict(),
        "access_token":  access_token,
        "refresh_token": refresh_token,
    })


# ─── Refresh token ────────────────────────────────────────────────────────────

@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    user_id      = get_jwt_identity()
    access_token = create_access_token(identity=user_id)
    return jsonify({"access_token": access_token})


# ─── Get current user ─────────────────────────────────────────────────────────

@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = int(get_jwt_identity())
    user    = User.query.get_or_404(user_id)
    return jsonify({"user": user.to_dict()})
