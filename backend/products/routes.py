import os
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename

from database import db, Product

products_bp = Blueprint("products", __name__)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ─── GET tất cả sản phẩm ─────────────────────────────────────────────────────

@products_bp.route("/products", methods=["GET"])
def get_products():
    category = request.args.get("category", "")
    search   = request.args.get("search", "")

    query = Product.query.filter_by(is_active=True)
    if category:
        query = query.filter_by(category=category)
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))

    products = query.order_by(Product.created_at.desc()).all()
    return jsonify({"products": [p.to_dict() for p in products]})


# ─── GET 1 sản phẩm ──────────────────────────────────────────────────────────

@products_bp.route("/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify({"product": product.to_dict()})


# ─── GET danh sách category ───────────────────────────────────────────────────

@products_bp.route("/products/categories", methods=["GET"])
def get_categories():
    rows = db.session.query(Product.category).distinct().filter(Product.is_active == True).all()
    categories = [r[0] for r in rows if r[0]]
    return jsonify({"categories": categories})


# ─── POST thêm sản phẩm (admin) ───────────────────────────────────────────────

@products_bp.route("/products", methods=["POST"])
@jwt_required()
def create_product():
    data = request.get_json()
    name = data.get("name", "").strip()
    if not name:
        return jsonify({"error": "Tên sản phẩm không được để trống."}), 400

    if Product.query.filter_by(name=name).first():
        return jsonify({"error": "Sản phẩm đã tồn tại."}), 409

    product = Product(
        name        = name,
        description = data.get("description", ""),
        price       = float(data.get("price", 0)),
        image_url   = data.get("image_url", ""),
        category    = data.get("category", ""),
        stock       = int(data.get("stock", 100)),
    )
    db.session.add(product)
    db.session.commit()
    return jsonify({"message": "Đã thêm sản phẩm.", "product": product.to_dict()}), 201


# ─── PUT cập nhật sản phẩm ────────────────────────────────────────────────────

@products_bp.route("/products/<int:product_id>", methods=["PUT"])
@jwt_required()
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    data    = request.get_json()

    product.name        = data.get("name",        product.name)
    product.description = data.get("description", product.description)
    product.price       = float(data.get("price", product.price))
    product.image_url   = data.get("image_url",   product.image_url)
    product.category    = data.get("category",    product.category)
    product.stock       = int(data.get("stock",   product.stock))
    product.is_active   = data.get("is_active",   product.is_active)

    db.session.commit()
    return jsonify({"message": "Đã cập nhật.", "product": product.to_dict()})


# ─── POST upload hình ảnh ─────────────────────────────────────────────────────

@products_bp.route("/products/<int:product_id>/upload-image", methods=["POST"])
@jwt_required()
def upload_image(product_id):
    product = Product.query.get_or_404(product_id)

    if "image" not in request.files:
        return jsonify({"error": "Không có file ảnh."}), 400

    file = request.files["image"]
    if not file or not allowed_file(file.filename):
        return jsonify({"error": "Định dạng ảnh không hợp lệ. Dùng PNG, JPG, JPEG hoặc WEBP."}), 400

    filename  = f"product_{product_id}_{secure_filename(file.filename)}"
    upload_dir = os.path.join(current_app.root_path, "uploads")
    os.makedirs(upload_dir, exist_ok=True)

    filepath = os.path.join(upload_dir, filename)
    file.save(filepath)

    product.image_url = f"/uploads/{filename}"
    db.session.commit()

    return jsonify({"message": "Upload thành công.", "image_url": product.image_url})


# ─── DELETE sản phẩm (soft delete) ───────────────────────────────────────────

@products_bp.route("/products/<int:product_id>", methods=["DELETE"])
@jwt_required()
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    product.is_active = False
    db.session.commit()
    return jsonify({"message": "Đã xóa sản phẩm."})
