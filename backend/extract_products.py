"""
Chạy script này để lấy danh sách sản phẩm thật từ dataset.
Output: products.json — dùng trong CartPanel.jsx
Không cần cài pandas - dùng csv module built-in
"""
import csv
import json
import ast
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Đọc rules CSV để lấy tất cả sản phẩm đã xuất hiện
rules_path = os.path.join(BASE_DIR, "precomputed", "apriori_rules.csv")

products = set()
with open(rules_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        for col in ["antecedents", "consequents"]:
            if col in row:
                val = row[col]
                try:
                    items = ast.literal_eval(str(val))
                    for item in items:
                        if isinstance(item, str):
                            products.add(item.strip())
                except Exception:
                    if str(val).strip():
                        products.add(str(val).strip())

product_list = sorted(list(products))
print(f"✅ Tìm thấy {len(product_list)} sản phẩm")

# Lưu ra file JSON
out_path = os.path.join(BASE_DIR, "..", "frontend", "src", "products.json")
os.makedirs(os.path.dirname(out_path), exist_ok=True)
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(product_list, f, ensure_ascii=False, indent=2)

print(f"✅ Đã lưu: {out_path}")
print("\n5 sản phẩm đầu tiên:")
for p in product_list[:5]:
    print(f"  - {p}")
