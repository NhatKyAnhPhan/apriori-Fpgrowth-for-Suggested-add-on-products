import { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import { useCart } from "../context/CartContext";
import api from "../services/api";
import RecommendBox from "../components/RecommendBox";
import CartPanel    from "../components/CartPanel";

export default function ComparePage() {
  const { user } = useAuth();
  const { cartNames } = useCart(); // Lấy tên sản phẩm từ giỏ hàng trang chủ
  const [analysisCart, setAnalysisCart] = useState([]);
  const [method, setMethod] = useState("fpgrowth");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Khi trang load: ưu tiên dùng giỏ hàng hiện tại, nếu trống thì load lịch sử mua
  useEffect(() => {
    if (cartNames.length > 0) {
      // Có sản phẩm trong giỏ → dùng luôn
      setAnalysisCart(cartNames);
    } else if (user) {
      // Giỏ trống → fallback: load lịch sử đơn hàng cũ
      api.get("/api/orders/my")
        .then(res => {
          const orders = res.data.orders || [];
          const historicalItems = new Set();
          orders.forEach(order => {
            if (order.status !== "cancelled" && order.items) {
              order.items.forEach(item => {
                if (item.product_name) historicalItems.add(item.product_name.toUpperCase());
              });
            }
          });
          setAnalysisCart(Array.from(historicalItems));
        })
        .catch(err => console.error("Không thể load lịch sử mua hàng:", err));
    }
  }, [cartNames, user]);

  const handleRecommend = async () => {
    if (analysisCart.length === 0) { setError("Vui lòng thêm sản phẩm vào giỏ hàng để phân tích."); return; }
    setError("");
    setLoading(true);
    setResults([]);  // Reset results trước khi gọi API mới
    try {
      const res = await api.post("/api/recommend", { items: analysisCart, method });
      setResults(res.data.recommendations || []);
    } catch (err) {
      setError(err.response?.data?.error || err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="home-page">
      <h2 style={{ color: "#2c3e50", marginBottom: "5px" }}>🔮 Gợi ý mua kèm sản phẩm </h2>
      <p style={{ color: "#7f8c8d", fontSize: "14px", marginBottom: "25px" }}>
        {cartNames.length > 0
          ? <>💡 Đã tự động đồng bộ <b>{cartNames.length} sản phẩm</b> từ giỏ hàng của bạn vào phân tích bên dưới.</>
          : <>💡 Hệ thống đã tự động đồng bộ các sản phẩm bạn <b>đã mua trước đây</b> vào giỏ phân tích.</>
        }
      </p>

      <div style={{ display: "flex", gap: "25px" }}>
        {/* Khối trái: Giỏ sản phẩm phân tích */}
        <div style={{ flex: 1 }}>
          <CartPanel cart={analysisCart} setCart={setAnalysisCart} />
        </div>

        {/* Khối phải: Thuật toán & Kết quả */}
        <div style={{ flex: 2, background: "#fff", padding: "20px", border: "1px solid #e0e0e0", borderRadius: "8px" }}>
          <div style={{ display: "flex", gap: "10px", alignItems: "center", marginBottom: "15px", flexWrap: "wrap" }}>
            <span style={{ fontWeight: "bold", color: "#2c3e50" }}>Mô hình khai phá:</span>
            {["apriori", "fpgrowth", "collab"].map((m) => (
              <button
                key={m}
                onClick={() => setMethod(m)}
                style={{ padding: "6px 15px", borderRadius: "4px", border: "1px solid #2c3e50", background: method === m ? "#2c3e50" : "#fff", color: method === m ? "#fff" : "#2c3e50", cursor: "pointer", fontWeight: "bold", textTransform: "uppercase", fontSize: "13px" }}
              >
                {m === "fpgrowth" ? "FP-Growth" : m === "collab" ? "CF + FP-G" : "Apriori"}
              </button>
            ))}
          </div>

          <button
            onClick={handleRecommend}
            disabled={loading}
            style={{ width: "100%", padding: "12px", background: "#3498db", color: "#fff", border: "none", borderRadius: "6px", cursor: "pointer", fontWeight: "bold", fontSize: "15px", marginBottom: "15px" }}
          >
            {loading ? "Hệ thống đang quét tập luật..." : "🔍 Phân tích luật kết hợp"}
          </button>

          {error && <p style={{ color: "#e74c3c", fontWeight: "500" }}>{error}</p>}
          <RecommendBox results={results} />
        </div>
      </div>
    </div>
  );
}
