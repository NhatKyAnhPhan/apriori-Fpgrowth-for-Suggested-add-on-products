import ast
import csv
import os
from config import Config
from algorithms.collaborative_filtering import cf_engine


class RuleEngine:
    """Tổng hợp kết quả từ Apriori, FP-Growth và Sequential Rules (Thuần Python - Không Pandas)."""

    def __init__(self):
        self.reload_rules()

    def reload_rules(self):
        """Đọc lại toàn bộ luật từ file CSV vào bộ nhớ RAM sử dụng thư viện csv mặc định."""
        self.apriori_rules   = self._load_rules(Config.APRIORI_RULES_PATH)
        self.fpgrowth_rules  = self._load_rules(Config.FPGROWTH_RULES_PATH)
        self.sequential_pats = self._load_sequential(Config.SEQUENTIAL_RULES_PATH)
        print("🔄 [RuleEngine] Đã cập nhật và đồng bộ luật mới thành công (Thuần Python)!")

    def _load_rules(self, path: str) -> list:
        """Đọc file CSV chứa các luật và trả về một danh sách các Dictionary."""
        rules_list = []
        if not os.path.exists(path):
            print(f"⚠️ Cảnh báo: Không tìm thấy tệp luật tại {path}")
            return rules_list
        try:
            with open(path, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if "antecedents" in row:
                        row["antecedents"] = self._parse_itemset(row["antecedents"])
                    if "consequents" in row:
                        row["consequents"] = self._parse_itemset(row["consequents"])
                    
                    if "support" in row:
                        row["support"] = float(row["support"])
                    if "confidence" in row:
                        row["confidence"] = float(row["confidence"])
                    if "lift" in row:
                        row["lift"] = float(row["lift"])
                        
                    rules_list.append(row)
        except Exception as e:
            print(f"❌ Lỗi khi tải tệp luật {path}: {str(e)}")
        return rules_list

    def _load_sequential(self, path: str) -> list:
        """Đọc tệp luật chuỗi thời gian (Sequential Patterns)."""
        pats = []
        if not os.path.exists(path):
            return pats
        try:
            with open(path, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if "sequence" in row:
                        try:
                            row["sequence"] = ast.literal_eval(row["sequence"])
                        except Exception:
                            row["sequence"] = [item.strip() for item in row["sequence"].split(",") if item.strip()]
                    if "support" in row:
                        row["support"] = float(row["support"])
                    pats.append(row)
        except Exception as e:
            print(f"❌ Lỗi khi tải tệp chuỗi {path}: {str(e)}")
        return pats

    def _parse_itemset(self, value: str) -> frozenset:
        """SỬA LỖI SO KHỚP: Chuyển đổi chuỗi luật CSV (dấu phẩy hoặc dạng list Python) thành frozenset chữ IN HOA chuẩn chỉnh."""
        if not value:
            return frozenset()
        val_str = str(value).strip()
        # Nếu chuỗi chứa định dạng mảng của Python cũ: "['MILK', 'BREAD']"
        if val_str.startswith('[') and val_str.endswith(']'):
            try:
                parsed = ast.literal_eval(val_str)
                return frozenset(item.strip().upper() for item in parsed)
            except Exception:
                pass
        # Định dạng chuẩn mới phân tách bằng dấu phẩy: "MILK,BREAD"
        return frozenset(item.strip().upper() for item in val_str.split(',') if item.strip())

    def recommend(self, cart_items: list, method: str = "fpgrowth", top_n: int = 5) -> list:
        """
        Nhận diện giỏ hàng của người dùng và đưa ra danh sách sản phẩm gợi ý kèm thông số chi tiết.
        
        Hỗ trợ 3 phương pháp:
        - "apriori": Association Rules từ Apriori
        - "fpgrowth": Association Rules từ FP-Growth
        - "collab": Collaborative Filtering + FP-Growth
        """
        # ĐỒNG BỘ: Chuyển toàn bộ tên sản phẩm trong giỏ hàng thành chữ IN HOA để khớp hoàn toàn với luật
        user_cart = frozenset(str(item).strip().upper() for item in cart_items if str(item).strip())
        
        print(f"🔍 [RuleEngine.recommend] method={method}, cart_items={cart_items}, user_cart={user_cart}")
        
        if not user_cart:
            print(f"⚠️ [RuleEngine] Cart rỗng, trả về []")
            return []

        # Nếu dùng Collaborative Filtering
        if method == "collab":
            print(f"🤖 [RuleEngine] Sử dụng CF")
            return cf_engine.recommend_from_similar_users(cart_items, top_n=top_n)

        # Chọn tập luật dựa trên cấu hình thuật toán của Frontend tuyển lựa
        rules = self.fpgrowth_rules if method == "fpgrowth" else self.apriori_rules
        print(f"📊 [RuleEngine] method={method}, loaded {len(rules)} rules")
        
        candidates = {}
        matched_rules = 0
        for r in rules:
            ant = r.get("antecedents", frozenset())
            con = r.get("consequents", frozenset())
            
            # Nếu giỏ hàng của khách hàng bao trùm lấy vế trái (antecedents) của luật
            if ant and ant.issubset(user_cart):
                matched_rules += 1
                # Các sản phẩm gợi ý thuộc vế phải (consequents) chưa có trong giỏ hàng hiện tại
                remain = con - user_cart
                for item in remain:
                    conf = r.get("confidence", 0.0)
                    lift = r.get("lift", 1.0)
                    sup  = r.get("support", 0.0)
                    
                    # Tính toán trọng số ưu tiên kết hợp thông minh
                    score = conf * lift
                    
                    ant_str = ", ".join(list(ant))
                    con_str = ", ".join(list(con))
                    rule_txt = f"{{{ant_str}}} -> {{{con_str}}}"

                    if item not in candidates or score > candidates[item]["score"]:
                        candidates[item] = {
                            "product_id": item,
                            "confidence": conf,
                            "lift":       lift,
                            "support":    sup,
                            "score":      score,
                            "rule":       rule_txt
                        }

        print(f"✅ [RuleEngine] Matched {matched_rules}/{len(rules)} rules, found {len(candidates)} candidates")
        
        # Sắp xếp danh sách gợi ý theo điểm số ưu tiên giảm dần
        sorted_candidates = sorted(candidates.values(), key=lambda x: x["score"], reverse=True)
        result = sorted_candidates[:top_n]
        print(f"📦 [RuleEngine] Returning {len(result)} recommendations")
        return result

    def get_stats(self) -> dict:
        """Tổng hợp thống kê chất lượng tập luật phục vụ hiển thị báo cáo khoa học."""
        def summarize(rules_list, name):
            total = len(rules_list)
            if total == 0:
                return {"algorithm": name, "total_rules": 0, "avg_support": 0, "avg_confidence": 0, "avg_lift": 0, "max_lift": 0, "top_rules": []}

            sum_support    = sum(r.get("support", 0.0) for r in rules_list)
            sum_confidence = sum(r.get("confidence", 0.0) for r in rules_list)
            sum_lift       = sum(r.get("lift", 0.0) for r in rules_list)
            max_lift       = max(r.get("lift", 0.0) for r in rules_list)

            top_rules_sorted = sorted(rules_list, key=lambda x: x.get("lift", 0.0), reverse=True)[:5]
            top_rules = []
            for r in top_rules_sorted:
                top_rules.append({
                    "antecedents":  list(r.get("antecedents", [])),
                    "consequents":  list(r.get("consequents", [])),
                    "support":      round(r.get("support", 0.0), 4),
                    "confidence":   round(r.get("confidence", 0.0), 4),
                    "lift":         round(r.get("lift", 0.0), 4)
                })

            return {
                "algorithm":      name,
                "total_rules":    total,
                "avg_support":    round(sum_support / total, 4),
                "avg_confidence": round(sum_confidence / total, 4),
                "avg_lift":       round(sum_lift / total, 4),
                "max_lift":       round(max_lift, 4),
                "top_rules":      top_rules,
            }

        cf_stats = {
            "algorithm": "collab",
            "total_users": len(cf_engine.user_items),
            "total_products": len(cf_engine.item_users),
            "description": "Collaborative Filtering + FP-Growth (dựa trên lịch sử mua hàng tương tự)"
        }

        return {
            "apriori":   summarize(self.apriori_rules,  "apriori"),
            "fpgrowth":  summarize(self.fpgrowth_rules, "fpgrowth"),
            "collab":    cf_stats,
        }


rule_engine = RuleEngine()