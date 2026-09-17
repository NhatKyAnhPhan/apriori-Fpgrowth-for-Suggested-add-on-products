import json
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request

from algorithms.rule_engine import rule_engine
from database import db, CartHistory
from train_engine import export_transactions_from_db, run_apriori_mining

recommend_bp = Blueprint("recommend", __name__)


# ─── DEBUG: Test endpoint ────────
@recommend_bp.route("/debug/rules", methods=["GET"])
def debug_rules():
    """Kiểm tra xem rules đã load đúng chưa"""
    return jsonify({
        "apriori_count": len(rule_engine.apriori_rules),
        "fpgrowth_count": len(rule_engine.fpgrowth_rules),
        "apriori_sample": rule_engine.apriori_rules[:2] if rule_engine.apriori_rules else [],
        "fpgrowth_sample": rule_engine.fpgrowth_rules[:2] if rule_engine.fpgrowth_rules else [],
    })


# ─── API 1: HÀM GỢI Ý ĐỒNG BỘ CHỮ SẢN PHẨM THEO TÊN (ITEMS) TỪ FRONTEND ────────
@recommend_bp.route("/recommend", methods=["POST"])
def recommend():
    data    = request.get_json() or {}
    # SỬA LỖI: Hỗ trợ linh hoạt cả cấu trúc "items" truyền chuỗi tên sản phẩm trực tiếp từ Frontend
    cart_items = data.get("items", []) or data.get("product_ids", [])
    method     = data.get("method", "fpgrowth")
    top_n      = int(data.get("top_n", 5))

    print(f"\n🔔 [API /recommend] REQUEST RECEIVED:")
    print(f"   method={method}, top_n={top_n}")
    print(f"   cart_items={cart_items}")

    if not cart_items:
        print(f"⚠️ [API] Cart empty!")
        return jsonify({"error": "Vui lòng cung cấp danh sách sản phẩm trong giỏ hàng."}), 400

    # Kiểm tra method hợp lệ
    valid_methods = ["apriori", "fpgrowth", "collab"]
    if method not in valid_methods:
        err_msg = f"Method '{method}' không hợp lệ. Chỉ hỗ trợ: {', '.join(valid_methods)}"
        print(f"❌ [API] {err_msg}")
        return jsonify({"error": err_msg}), 400

    # Gọi bộ công cụ quy tắc kết hợp để khai phá các ứng viên tiềm năng
    print(f"📍 [API] Calling rule_engine.recommend()...")
    recommended_candidates = rule_engine.recommend(cart_items, method=method, top_n=top_n)
    print(f"📍 [API] Got {len(recommended_candidates)} recommendations back")

    # Ghi nhận lịch sử giỏ hàng của người dùng nếu đã thực hiện đăng nhập vào hệ thống
    try:
        verify_jwt_in_request(optional=True)
        user_id = get_jwt_identity()
        if user_id:
            history = CartHistory(
                user_id=int(user_id),
                cart_items=json.dumps(cart_items),
                recommendations=json.dumps([c["product_id"] for c in recommended_candidates]),
                algorithm=method
            )
            db.session.add(history)
            db.session.commit()
    except Exception:
        pass

    # Trả về kết quả mảng cấu trúc đối tượng hoàn chỉnh bao gồm các chỉ số khoa học
    return jsonify({
        "cart_items":      cart_items,
        "algorithm":       method,
        "recommendations": recommended_candidates,
        "count":           len(recommended_candidates),
    })


# ─── API 2: ADMIN KÍCH HOẠT QUY TRÌNH RE-TRAIN MÔ HÌNH KHÉP KÍN ─────────────────
@recommend_bp.route("/admin/re-train", methods=["POST"])
@jwt_required()  
def retrain_recommendations():
    """
    API điều khiển luồng chạy thuật toán trích xuất hóa đơn và khai phá luật kết hợp tự động.
    """
    try:
        # Bước 1: Trích xuất lịch sử đơn hàng thực tế lưu ra file data/transactions.csv
        export_transactions_from_db()
        
        # Bước 2: Chạy thuật toán Apriori thuần Python tự code đọc file transaction và sinh lại luật mới vào file CSV
        run_apriori_mining(min_support=0.01, min_confidence=0.1)
        
        # Bước 3: Nạp nóng tập luật mới vào bộ nhớ đệm RAM của hệ thống Flask ngay lập tức
        rule_engine.reload_rules()
        
        return jsonify({
            "status": "success",
            "message": "Hệ thống đã trích xuất hóa đơn, tự động chạy thuật toán sinh luật và cập nhật bộ nhớ gợi ý thành công! 🚀"
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": f"Lỗi trong quá trình tái huấn luyện dữ liệu: {str(e)}"
        }), 500