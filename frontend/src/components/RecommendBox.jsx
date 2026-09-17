import { useState } from "react";
import api from "../services/api";
import { useAuth } from "../context/AuthContext";

export default function RecommendBox({ results }) {
  const { user }          = useAuth();
  const [saved, setSaved] = useState(new Set());

  const toggleFavorite = async (productId) => {
    if (!user) return;
    try {
      await api.post("/user/favorites", { product_id: productId });
      setSaved((prev) => {
        const next = new Set(prev);
        next.has(productId) ? next.delete(productId) : next.add(productId);
        return next;
      });
    } catch (err) {
      console.error(err);
    }
  };

  // Trạng thái khi chưa bấm nút tìm kiếm hoặc không có kết quả phù hợp
  if (!results || results.length === 0) {
    return (
      <div style={{ textAlign: "center", padding: "40px", color: "#bbb", border: "2px dashed #eee", borderRadius: "8px", marginTop: "25px" }}>
        <p style={{ fontSize: "16px", margin: 0, fontWeight: "500" }}>🔮 Kết quả gợi ý sẽ xuất hiện ở đây.</p>
        <p style={{ fontSize: "13px", margin: "5px 0 0 0", color: "#aaa" }}>Hãy chọn sản phẩm vào giỏ hàng và bấm nút phân tích.</p>
      </div>
    );
  }

  return (
    <div className="recommend-box" style={{ marginTop: "25px" }}>
      <h4 style={{ color: "#2c3e50", fontSize: "16px", marginBottom: "15px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <span>📋 Danh sách sản phẩm được khuyên dùng mua kèm:</span>
        <span style={{ color: "#7f8c8d", fontWeight: "normal", fontSize: "13px", background: "#f1f2f6", padding: "3px 10px", borderRadius: "12px" }}>
          Tìm thấy {results.length} gợi ý
        </span>
      </h4>

      <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
        {results.map((r, i) => (
          <div 
            key={r.product_id} 
            className="recommend-item"
            style={{
              padding: "15px",
              border: "1px solid #e0e0e0",
              borderRadius: "8px",
              background: "#fff",
              boxShadow: "0 2px 4px rgba(0,0,0,0.02)",
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              transition: "transform 0.2s, box-shadow 0.2s"
            }}
          >
            {/* Khối bên trái: Thứ hạng và Tên sản phẩm */}
            <div style={{ display: "flex", alignItems: "center", gap: "15px" }}>
              {/* Vòng tròn xếp hạng (Rank #1, #2, #3...) */}
              <div style={{ 
                background: i === 0 ? "#e74c3c" : i === 1 ? "#f39c12" : i === 2 ? "#3498db" : "#95a5a6", 
                color: "#fff", 
                width: "28px", 
                height: "28px", 
                borderRadius: "50%", 
                display: "flex", 
                alignItems: "center", 
                justifyContent: "center", 
                fontSize: "13px", 
                fontWeight: "bold",
                boxShadow: "0 2px 4px rgba(0,0,0,0.1)"
              }}>
                {i + 1}
              </div>

              {/* Tên sản phẩm */}
              <div>
                <strong style={{ fontSize: "16px", color: "#2c3e50" }} className="product-name">
                  {r.product_id}
                </strong>
                {/* Hiển thị chi tiết luật kết hợp tương ứng để giảng viên dễ chấm điểm thuật toán */}
                {r.rule && (
                  <div style={{ fontSize: "11px", color: "#7f8c8d", marginTop: "3px", fontFamily: "monospace" }}>
                    Rule: {r.rule}
                  </div>
                )}
              </div>
            </div>

            {/* Khối bên phải: Chỉ số khai phá dữ liệu & Nút yêu thích */}
            <div style={{ display: "flex", gap: "12px", alignItems: "center" }}>
              
              {/* Chỉ số Support (Độ hỗ trợ) */}
              <div style={{ textAlign: "center", padding: "4px 10px", background: "#f8f9fa", borderRadius: "6px", border: "1px solid #f1f2f6", minWidth: "55px" }} title="Support">
                <div style={{ fontSize: "10px", color: "#95a5a6", textTransform: "uppercase", letterSpacing: "0.5px" }}>Support</div>
                <strong style={{ color: "#7f8c8d", fontSize: "13px" }}>{(r.support * 100).toFixed(1)}%</strong>
              </div>

              {/* Chỉ số Confidence (Độ tin cậy) */}
              <div style={{ textAlign: "center", padding: "4px 10px", background: "#e8f4fd", borderRadius: "6px", minWidth: "55px" }} title="Confidence">
                <div style={{ fontSize: "10px", color: "#2980b9", textTransform: "uppercase", letterSpacing: "0.5px" }}>Confidence</div>
                <strong style={{ color: "#2980b9", fontSize: "13px" }}>{(r.confidence * 100).toFixed(1)}%</strong>
              </div>

              {/* Chỉ số Lift (Độ nâng cao) */}
              <div style={{ textAlign: "center", padding: "4px 10px", background: "#fff3e0", borderRadius: "6px", minWidth: "55px" }} title="Lift">
                <div style={{ fontSize: "10px", color: "#e65100", textTransform: "uppercase", letterSpacing: "0.5px" }}>Lift</div>
                <strong style={{ color: "#e65100", fontSize: "13px" }}>{r.lift.toFixed(2)}</strong>
              </div>

              {/* Nút Yêu thích (Chỉ hiển thị khi đã đăng nhập hệ thống) */}
              {user && (
                <button
                  onClick={() => toggleFavorite(r.product_id)}
                  style={{
                    background: "none",
                    border: "none",
                    fontSize: "20px",
                    cursor: "pointer",
                    padding: "5px",
                    lineHeight: 1,
                    transition: "transform 0.1s"
                  }}
                  className={saved.has(r.product_id) ? "btn-fav saved" : "btn-fav"}
                  title={saved.has(r.product_id) ? "Xóa khỏi danh sách yêu thích" : "Lưu vào danh sách yêu thích"}
                >
                  {saved.has(r.product_id) ? "❤️" : "🤍"}
                </button>
              )}
            </div>

          </div>
        ))}
      </div>
    </div>
  );
}