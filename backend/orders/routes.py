from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from database import db, Order, OrderItem, Product

orders_bp = Blueprint("orders", __name__)


# ─── Tạo đơn hàng (checkout) ─────────────────────────────────────────────────

@orders_bp.route("/orders", methods=["POST"])
@jwt_required()
def create_order():
    """
    Body JSON nhận từ Frontend:
    {
        "items":   [{"product_id": "BÚN BÒ HUẾ", "quantity": 2}, ...],
        "address": "Tây Thạnh, Tân Phú...",
        "note":    "Giao buổi chiều"
    }
    """
    user_id = int(get_jwt_identity())
    data    = request.get_json() or {}
    items   = data.get("items", [])

    if not items:
        return jsonify({"error": "Giỏ hàng trống."}), 400

    # 1. TÌM ĐỊA CHỈ: Ưu tiên địa chỉ từ Frontend gửi lên trong body đơn hàng
    address = data.get("address", "").strip()

    # 2. ĐỒNG BỘ TỰ ĐỘNG: Nếu Front không gửi, lấy địa chỉ mặc định lưu trong bảng User
    if not address:
        from database import User
        current_user = User.query.get(user_id)
        if current_user and getattr(current_user, "address", ""):
            address = current_user.address.strip()

    # 3. KIỂM TRA CUỐI CÙNG: Nếu cả 2 nguồn đều hoàn toàn trống rỗng thì mới báo lỗi
    if not address:
        return jsonify({
            "error": "Lỗi thanh toán: Vui lòng nhập địa chỉ giao hàng hoặc cập nhật trong thông tin cá nhân."
        }), 400

    # Kiểm tra sản phẩm + tính tổng tiền đơn hàng
    order_items = []
    total       = 0.0

    for item in items:
        product_id = item.get("product_id")
        quantity   = int(item.get("quantity", 1))

        # Khởi tạo biến tìm kiếm sản phẩm ban đầu
        product = None

        # XỬ LÝ NHẬN DIỆN ID SỐ HOẶC TÊN CHỮ IN HOA/THƯỜNG
        if isinstance(product_id, str):
            product_id_clean = product_id.strip()
            if not product_id_clean.isdigit():
                # Nếu là Chuỗi chữ (ví dụ: "BÚN BÒ HUẾ"), tìm kiếm không phân biệt hoa thường bằng .ilike()
                product = Product.query.filter(Product.name.ilike(product_id_clean)).first()
            else:
                # Nếu là Chuỗi nhưng chứa số (ví dụ: "1"), chuyển đổi sang kiểu số nguyên để tìm kiếm
                product = Product.query.get(int(product_id_clean))
        else:
            # Nếu bản thân product_id truyền lên là kiểu Số nguyên (int) nguyên bản
            product = Product.query.get(int(product_id))

        # Kiểm tra sự tồn tại và trạng thái hoạt động của sản phẩm
        if not product or not product.is_active:
            return jsonify({"error": f"Sản phẩm '{product_id}' không tồn tại trong hệ thống."}), 404
            
        # Kiểm tra số lượng tồn kho của sản phẩm
        if product.stock < quantity:
            return jsonify({"error": f"Sản phẩm '{product.name}' không đủ số lượng cung ứng (Tồn kho còn: {product.stock})."}), 400

        # Cộng dồn tổng giá trị và đưa vào danh sách chờ xử lý
        subtotal = product.price * quantity
        total   += subtotal
        order_items.append({"product": product, "quantity": quantity, "price": product.price})

    # Khởi tạo bản ghi Đơn hàng mới
    order = Order(
        user_id = user_id,
        total   = round(total, 2),
        status  = "confirmed",
        address = address, 
        note    = data.get("note", ""),
    )
    db.session.add(order)
    db.session.flush()  # Ép sinh nhanh order.id tạm thời mà chưa hoàn tất commit

    # Lưu chi tiết từng sản phẩm của đơn hàng (OrderItem) và cập nhật số lượng tồn kho
    for item_data in order_items:
        order_item = OrderItem(
            order_id   = order.id,
            product_id = item_data["product"].id,
            quantity   = item_data["quantity"],
            price      = item_data["price"],
        )
        db.session.add(order_item)
        item_data["product"].stock -= item_data["quantity"]  # Trừ số lượng tồn kho tương ứng

    # Hoàn tất lưu trữ mọi biến động vào file dữ liệu .db
    db.session.commit()

    return jsonify({
        "message": "Đặt hàng thành công! 🎉",
        "order":   order.to_dict(),
    }), 201


# ─── Lấy lịch sử đơn hàng của user ──────────────────────────────────────────

@orders_bp.route("/orders/my", methods=["GET"])
@jwt_required()
def get_my_orders():
    user_id = int(get_jwt_identity())
    orders  = (Order.query
               .filter_by(user_id=user_id)
               .order_by(Order.created_at.desc())
               .all())
    return jsonify({"orders": [o.to_dict() for o in orders]})


# ─── Lấy chi tiết 1 đơn hàng ─────────────────────────────────────────────────

@orders_bp.route("/orders/<int:order_id>", methods=["GET"])
@jwt_required()
def get_order(order_id):
    user_id = int(get_jwt_identity())
    order   = Order.query.filter_by(id=order_id, user_id=user_id).first_or_404()
    return jsonify({"order": order.to_dict()})


# ─── Huỷ đơn hàng ────────────────────────────────────────────────────────────

@orders_bp.route("/orders/<int:order_id>/cancel", methods=["POST"])
@jwt_required()
def cancel_order(order_id):
    user_id = int(get_jwt_identity())
    order   = Order.query.filter_by(id=order_id, user_id=user_id).first_or_404()

    if order.status in ("shipping", "delivered"):
        return jsonify({"error": "Không thể huỷ đơn hàng đang giao hoặc đã giao."}), 400

    # Hoàn trả lại số lượng tồn kho của sản phẩm khi hủy đơn
    for item in order.items:
        if item.product:
            item.product.stock += item.quantity

    order.status = "cancelled"
    db.session.commit()
    return jsonify({"message": "Đã huỷ đơn hàng thành công.", "order": order.to_dict()})