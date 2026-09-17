import os
import csv
from flask import Blueprint, jsonify
from sqlalchemy import func
from database import db, Order, OrderItem, Product
from datetime import datetime, timedelta
from collections import defaultdict

stats_bp = Blueprint("stats", __name__)

# Đường dẫn tới file CSV data lớn (đặt trong backend/data/)
CSV_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "Assignment-1_Data_Cleaned.csv")

# Ngày mới nhất trong CSV (dùng làm mốc thời gian cho day/week/month)
CSV_MAX_DATE = datetime(2011, 12, 9, 12, 50)


def query_csv_stats(start_date):
    """Đọc CSV và trả về dict {product_name: total_quantity} trong khoảng thời gian."""
    counts = defaultdict(int)
    if not os.path.exists(CSV_PATH):
        return counts
    with open(CSV_PATH, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                dt  = datetime.strptime(row["Date"].strip(), "%Y-%m-%d %H:%M:%S")
                qty = int(float(row["Quantity"]))
                if dt >= start_date and qty > 0:
                    counts[row["Itemname"].strip()] += qty
            except Exception:
                pass
    return counts


def query_db_stats(start_date):
    """Đọc đơn hàng thực từ DB và trả về dict {product_name: total_quantity}."""
    rows = db.session.query(
        Product.name,
        func.sum(OrderItem.quantity).label("total_qty")
    ).join(OrderItem, OrderItem.product_id == Product.id)\
     .join(Order, Order.id == OrderItem.order_id)\
     .filter(Order.status != "cancelled", Order.created_at >= start_date)\
     .group_by(Product.name).all()
    return {name: int(qty) for name, qty in rows}


def merge_and_top5(csv_counts, db_counts):
    """Gộp 2 nguồn data, trả về top 5 dạng list [{"name": ..., "quantity": ...}]."""
    merged = defaultdict(int)
    for name, qty in csv_counts.items():
        merged[name] += qty
    for name, qty in db_counts.items():
        merged[name] += qty
    top5 = sorted(merged.items(), key=lambda x: -x[1])[:5]
    return [{"name": name, "quantity": qty} for name, qty in top5]


@stats_bp.route("/stats", methods=["GET"])
def get_top_selling_stats():
    now = datetime.utcnow()

    # Mốc thời gian cho DB (đơn hàng thực tế — tính từ hiện tại)
    db_day   = now - timedelta(days=1)
    db_week  = now - timedelta(weeks=1)
    db_month = now - timedelta(days=30)

    # Mốc thời gian cho CSV (tính lùi từ ngày cuối cùng trong dataset)
    csv_day   = CSV_MAX_DATE - timedelta(days=1)
    csv_week  = CSV_MAX_DATE - timedelta(weeks=1)
    csv_month = CSV_MAX_DATE - timedelta(days=30)

    try:
        # Lấy data từ CSV theo từng khoảng
        csv_day_data   = query_csv_stats(csv_day)
        csv_week_data  = query_csv_stats(csv_week)
        csv_month_data = query_csv_stats(csv_month)

        # Lấy data từ DB
        db_day_data   = query_db_stats(db_day)
        db_week_data  = query_db_stats(db_week)
        db_month_data = query_db_stats(db_month)

        return jsonify({
            "status": "success",
            "data": {
                "day":   merge_and_top5(csv_day_data,   db_day_data),
                "week":  merge_and_top5(csv_week_data,  db_week_data),
                "month": merge_and_top5(csv_month_data, db_month_data),
            }
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500