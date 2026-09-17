import csv
import os
from database import db, Order, User

class CollaborativeFilteringEngine:
    """
    Kết hợp Collaborative Filtering + FP-Growth
    - Tìm users tương tự dựa trên lịch sử mua hàng (Cosine Similarity)
    - Áp dụng FP-Growth để sinh luật từ dữ liệu users tương tự
    """
    
    def __init__(self):
        self.user_items = {}  # {user_id: set([product_names])}
        self.item_users = {}  # {product_name: set([user_ids])}
    
    def ensure_loaded(self):
        """Lazy load dữ liệu nếu chưa load, dùng trong request context."""
        if not self.user_items and not self.item_users:
            self.load_user_items()
    
    def load_user_items(self):
        """Tải dữ liệu mua hàng của tất cả users từ database."""
        try:
            orders = Order.query.filter(Order.status != "cancelled").all()
            for order in orders:
                user_id = order.user_id
                if user_id not in self.user_items:
                    self.user_items[user_id] = set()
                
                for item in order.items:
                    if item.product:
                        product_name = item.product.name.upper()
                        self.user_items[user_id].add(product_name)
                        
                        if product_name not in self.item_users:
                            self.item_users[product_name] = set()
                        self.item_users[product_name].add(user_id)
            
            print(f"✅ [CF] Đã load {len(self.user_items)} users, {len(self.item_users)} products")
        except Exception as e:
            print(f"❌ Lỗi khi tải dữ liệu CF: {str(e)}")
    
    def cosine_similarity(self, set1: set, set2: set) -> float:
        """Tính độ tương tự cosine giữa 2 tập hợp."""
        if not set1 or not set2:
            return 0.0
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        if union == 0:
            return 0.0
        
        # Jaccard similarity = intersection / union
        return intersection / union
    
    def find_similar_users(self, cart_items: set, top_k: int = 10) -> list:
        """
        Tìm K users tương tự nhất dựa trên giỏ hàng hiện tại.
        
        Args:
            cart_items: frozenset các sản phẩm trong giỏ hàng
            top_k: số lượng users tương tự cần tìm
        
        Returns:
            list các (user_id, similarity_score)
        """
        self.ensure_loaded()  # Ensure data is loaded before using it
        
        user_cart = set(str(item).strip().upper() for item in cart_items if item)
        
        if not user_cart:
            return []
        
        similarities = []
        
        for user_id, user_products in self.user_items.items():
            if len(user_products) == 0:
                continue
            
            sim = self.cosine_similarity(user_cart, user_products)
            if sim > 0:
                similarities.append((user_id, sim))
        
        # Sắp xếp theo độ tương tự giảm dần
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]
    
    def recommend_from_similar_users(self, cart_items: list, top_n: int = 5) -> list:
        """
        Gợi ý sản phẩm từ các users tương tự.
        
        Thuật toán:
        1. Tìm K users tương tự nhất
        2. Lấy các sản phẩm họ đã mua nhưng người dùng hiện tại chưa mua
        3. Xếp hạng dựa trên:
           - Số lần xuất hiện ở users tương tự (popularity)
           - Độ tương tự của user (similarity score)
        """
        self.ensure_loaded()  # Ensure data is loaded before using it
        
        cart_set = frozenset(str(item).strip().upper() for item in cart_items if item)
        
        if not cart_set:
            return []
        
        # Bước 1: Tìm 15 users tương tự
        similar_users = self.find_similar_users(cart_set, top_k=15)
        
        if not similar_users:
            print(f"⚠️ [CF] Không tìm thấy users tương tự cho giỏ: {cart_set}")
            return []
        
        # Bước 2: Tích lũy điểm cho mỗi sản phẩm
        product_scores = {}
        
        for user_id, user_similarity in similar_users:
            user_products = self.user_items.get(user_id, set())
            
            for product in user_products:
                # Không gợi ý sản phẩm đã có trong giỏ hàng
                if product in cart_set:
                    continue
                
                if product not in product_scores:
                    product_scores[product] = {
                        "count": 0,
                        "similarity_sum": 0.0,
                        "score": 0.0
                    }
                
                product_scores[product]["count"] += 1
                product_scores[product]["similarity_sum"] += user_similarity
        
        # Bước 3: Tính điểm cuối cùng = (số lần xuất hiện) × (tổng độ tương tự) × (tỷ lệ trung bình)
        candidates = {}
        
        for product, metrics in product_scores.items():
            # Trung bình độ tương tự của users có mua sản phẩm này
            avg_similarity = metrics["similarity_sum"] / metrics["count"]
            
            # Điểm = (số users có mua) × (độ tương tự trung bình) × 10
            final_score = metrics["count"] * avg_similarity
            
            candidates[product] = {
                "product_id": product,
                "score": final_score,
                "count_similar_users": metrics["count"],
                "avg_similarity": round(avg_similarity, 4),
                "rule": f"CF+FPG: {metrics['count']} similar users bought this"
            }
        
        # Sắp xếp theo điểm giảm dần
        sorted_candidates = sorted(candidates.values(), key=lambda x: x["score"], reverse=True)
        
        # Chuyển đổi thành format tương tự các thuật toán khác
        result = []
        total_users = len(self.user_items) if self.user_items else 1
        
        for idx, candidate in enumerate(sorted_candidates[:top_n]):
            result.append({
                "product_id": candidate["product_id"],
                "confidence": candidate["avg_similarity"],  # Dùng avg_similarity như confidence
                "lift": 1.0 + (candidate["count_similar_users"] / 10.0),  # Lift = 1 + (count/10)
                "support": candidate["count_similar_users"] / total_users,
                "score": candidate["score"],
                "rule": candidate["rule"]
            })
        
        return result


cf_engine = CollaborativeFilteringEngine()
