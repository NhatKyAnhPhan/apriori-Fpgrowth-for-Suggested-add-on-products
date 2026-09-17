import json
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from database import db, User, CartHistory, Favorite, ViewedRecommendation

user_bp = Blueprint("user", __name__)


# ─── API LẤY ĐỊA CHỈ (BỌC TRY-EXCEPT AN TOÀN TUYỆT ĐỐI) ──────────────────────

@user_bp.route("/profile/address", methods=["GET"])
@jwt_required()
def get_user_address():
    """Lấy địa chỉ hiện tại của User - Chống sập hệ thống khi chưa nâng cấp DB"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Không tìm thấy người dùng"}), 404
        
    try:
        # Nếu cột address tồn tại trong bảng users
        address = getattr(user, "address", "") or ""
        return jsonify({"address": address})
    except Exception:
        # Nếu DB chưa có cột address, trả về chuỗi rỗng thay vì làm sập API Đăng nhập
        return jsonify({"address": ""})


@user_bp.route("/profile/address", methods=["PUT"])
@jwt_required()
def update_user_address():
    """Cập nhật địa chỉ giao hàng"""
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    new_address = data.get("address", "").strip()

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Không tìm thấy người dùng"}), 404

    try:
        # Gán và lưu xuống DB
        user.address = new_address
        db.session.commit()
        return jsonify({
            "status": "success",
            "message": "Cập nhật địa chỉ giao hàng mặc định thành công!",
            "address": new_address
        }), 200
    except Exception as e:
        db.session.rollback()
        # Trả về thông báo hướng dẫn cụ thể nếu thiếu cột trong bảng
        return jsonify({
            "error": "Database chưa có cột 'address'. Vui lòng thêm cột address vào bảng users hoặc xóa database cũ để hệ thống tự khởi tạo lại!"
        }), 500


# ─── Cart History (Giữ nguyên logic gốc) ──────────────────────────────────────

@user_bp.route("/history", methods=["GET"])
@jwt_required()
def get_history():
    user_id = int(get_jwt_identity())
    history = (CartHistory.query
               .filter_by(user_id=user_id)\
               .order_by(CartHistory.searched_at.desc())\
               .limit(50)\
               .all())
    return jsonify({"history": [h.to_dict() for h in history]})


@user_bp.route("/history", methods=["POST"])
@jwt_required()
def save_history():
    user_id = int(get_jwt_identity())
    data    = request.get_json()

    cart_items      = data.get("cart_items", [])
    recommendations = data.get("recommendations", [])
    algorithm       = data.get("algorithm", "fpgrowth")

    if not cart_items:
        return jsonify({"error": "Giỏ hàng trống."}), 400

    record = CartHistory(
        user_id         = user_id,
        cart_items      = json.dumps(cart_items, ensure_ascii=False),
        recommendations = json.dumps(recommendations, ensure_ascii=False),
        algorithm       = algorithm,
    )
    db.session.add(record)
    db.session.commit()
    return jsonify({"message": "Đã lưu lịch sử.", "history_id": record.id}), 201


@user_bp.route("/history/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_history(id):
    user_id = int(get_jwt_identity())
    record = CartHistory.query.filter_by(id=id, user_id=user_id).first()
    if not record:
        return jsonify({"error": "Không tìm thấy bản ghi hoặc không có quyền."}), 404

    db.session.delete(record)
    db.session.commit()
    return jsonify({"message": "Đã xóa bản ghi lịch sử."})


# ─── Favorites (Giữ nguyên logic gốc) ─────────────────────────────────────────

@user_bp.route("/favorites", methods=["GET"])
@jwt_required()
def get_favorites():
    user_id   = int(get_jwt_identity())
    favorites = (Favorite.query
                 .filter_by(user_id=user_id)\
                 .order_by(Favorite.added_at.desc())\
                 .all())
    return jsonify({"favorites": [f.to_dict() for f in favorites]})


@user_bp.route("/favorites", methods=["POST"])
@jwt_required()
def toggle_favorite():
    user_id    = int(get_jwt_identity())
    product_id = request.get_json().get("product_id", "").strip()

    if not product_id:
        return jsonify({"error": "Thiếu product_id."}), 400

    existing = Favorite.query.filter_by(user_id=user_id, product_id=product_id).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        return jsonify({"message": "Đã xóa khỏi yêu thích.", "action": "removed"})

    fav = Favorite(user_id=user_id, product_id=product_id)
    db.session.add(fav)
    db.session.commit()
    return jsonify({"message": "Đã thêm vào yêu thích.", "action": "added", "favorite": fav.to_dict()}), 201


# ─── Viewed Recommendations (Giữ nguyên logic gốc) ────────────────────────────

@user_bp.route("/viewed", methods=["POST"])
@jwt_required()
def log_viewed():
    user_id    = int(get_jwt_identity())
    data       = request.get_json()
    product_id = data.get("product_id", "").strip()
    algorithm  = data.get("algorithm", "")

    if not product_id:
        return jsonify({"error": "Thiếu product_id"}), 400

    log = ViewedRecommendation(user_id=user_id, product_id=product_id, algorithm=algorithm)
    db.session.add(log)
    db.session.commit()
    return jsonify({"message": "Đã ghi nhận lượt xem gợi ý."}), 201