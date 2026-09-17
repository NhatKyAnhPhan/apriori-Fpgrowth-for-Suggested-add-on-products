from flask import Blueprint, request, jsonify
from algorithms.rule_engine import rule_engine

compare_bp = Blueprint("compare", __name__)


@compare_bp.route("/compare", methods=["POST"])
def compare():
    """
    So sánh kết quả Apriori vs FP-Growth cho cùng giỏ hàng.
    Body JSON: { "items": ["Milk", "Bread"], "top_n": 5 }
    """
    data  = request.get_json()
    items = data.get("items", [])
    top_n = int(data.get("top_n", 5))

    if not items:
        return jsonify({"error": "Vui lòng chọn ít nhất 1 sản phẩm."}), 400

    comparison = rule_engine.compare(items, top_n=top_n)
    return jsonify({
        "cart_items": items,
        "results":    comparison,
    })
