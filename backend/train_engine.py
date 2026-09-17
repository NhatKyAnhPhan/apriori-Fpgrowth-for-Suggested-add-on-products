import csv
import os
from itertools import combinations
from database import db, Order

# ─── 1. HÀM TRÍCH XUẤT ĐƠN HÀNG CỦA BẠN (GIỮ NGUYÊN) ───────────────────────────
def export_transactions_from_db(output_path="data/transactions.csv"):
    """
    Quét qua bảng orders và order_items trong Database để tạo file transactions dạng:
    item1,item2,item3
    (Thuần Python - Không dùng Pandas)
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Lấy tất cả các đơn hàng trừ các đơn đã bị hủy
    orders = Order.query.filter(Order.status != "cancelled").all()
    
    count = 0
    with open(output_path, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        for order in orders:
            items = [item.product.name for item in order.items if item.product]
            if items:
                writer.writerow(items)
                count += 1
                
    print(f"📊 [TrainEngine] Đã trích xuất thành công {count} giao dịch thực tế từ Database ra {output_path}!")
    return output_path


# ─── 2. THUẬT TOÁN APRIORI THUẦN PYTHON — TỰ ĐỘNG XUẤT LUẬT MỚI ──────────────────
def run_apriori_mining(min_support=0.01, min_confidence=0.1):
    """
    Đọc dữ liệu giao dịch từ data/transactions.csv, chạy thuật toán Apriori
    và xuất kết quả trực tiếp ra file precomputed/apriori_rules.csv (Không dùng Pandas)
    """
    # Đường dẫn đọc file transaction vừa xuất và đường dẫn ghi file luật
    base_dir = os.path.dirname(os.path.abspath(__file__))
    tx_path = os.path.join(base_dir, "data", "transactions.csv")
    rules_output_path = os.path.join(base_dir, "precomputed", "apriori_rules.csv")
    
    if not os.path.exists(tx_path):
        print("⚠️ Không tìm thấy file transactions.csv để khai phá.")
        return

    # Đọc các giao dịch vào bộ nhớ RAM
    transactions = []
    with open(tx_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if row:
                transactions.append(set(row))
                
    total_tx = len(transactions)
    if total_tx == 0:
        print("⚠️ File transactions trống, không thể khai phá.")
        return

    # Bước A: Tìm tập mục phổ biến kích thước 1 (C1 -> L1)
    item_counts = {}
    for tx in transactions:
        for item in tx:
            item_counts[frozenset([item])] = item_counts.get(frozenset([item]), 0) + 1

    frequent_itemsets = {}
    for itemset, count in item_counts.items():
        support = count / total_tx
        if support >= min_support:
            frequent_itemsets[itemset] = support

    # Bước B: Tìm tập mục phổ biến kích thước lớn hơn (k >= 2)
    current_l = list(frequent_itemsets.keys())
    k = 2
    while len(current_l) > 0:
        candidates = set()
        for i in range(len(current_l)):
            for j in range(i + 1, len(current_l)):
                candidate = current_l[i] | current_l[j]
                if len(candidate) == k:
                    candidates.add(candidate)
        
        candidate_counts = {c: 0 for c in candidates}
        for tx in transactions:
            for c in candidates:
                if c.issubset(tx):
                    candidate_counts[c] += 1
                    
        current_l = []
        for c, count in candidate_counts.items():
            support = count / total_tx
            if support >= min_support:
                frequent_itemsets[c] = support
                current_l.append(c)
        k += 1

    # Bước C: Sinh luật kết hợp từ các tập mục phổ biến (Rules Generation)
    rules = []
    for itemset, support in frequent_itemsets.items():
        if len(itemset) < 2:
            continue
            
        items = list(itemset)
        for r_len in range(1, len(items)):
            for antecedent in combinations(items, r_len):
                antecedent = frozenset(antecedent)
                consequent = itemset - antecedent
                
                if antecedent in frequent_itemsets:
                    support_a = frequent_itemsets[antecedent]
                    confidence = support / support_a
                    
                    if confidence >= min_confidence and consequent in frequent_itemsets:
                        support_b = frequent_itemsets[consequent]
                        lift = confidence / support_b
                        
                        rules.append({
                            "antecedents": antecedent,
                            "consequents": consequent,
                            "support": round(support, 4),
                            "confidence": round(confidence, 4),
                            "lift": round(lift, 4)
                        })

    # ─── Bước D: Ghi trực tiếp danh sách luật tìm được ra file CSV bằng csv.DictWriter ───
    os.makedirs(os.path.dirname(rules_output_path), exist_ok=True)
    with open(rules_output_path, mode="w", encoding="utf-8", newline="") as f:
        fieldnames = ["antecedents", "consequents", "support", "confidence", "lift"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rules:
            # Chuẩn hóa: Biến đổi frozenset thành chuỗi, các item cách nhau bằng dấu phẩy
            # Ví dụ: "MILK,BREAD" thay vì "['MILK', 'BREAD']"
            antecedents_str = ",".join(sorted(list(r["antecedents"])))
            consequents_str = ",".join(sorted(list(r["consequents"])))
            
            writer.writerow({
                "antecedents": antecedents_str,
                "consequents": consequents_str,
                "support": r["support"],
                "confidence": r["confidence"],
                "lift": r["lift"]
            })
            
    print(f"🚀 [TrainEngine] Đã lưu {len(rules)} luật Apriori mới vào {rules_output_path}")