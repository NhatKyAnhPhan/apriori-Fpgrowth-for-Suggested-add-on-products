import { useState } from "react";
import api from "../services/api";

export default function AdminDashboard() {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const handleRetrain = async () => {
    setLoading(true);
    setMessage("");
    setError("");
    try {
      // Gọi API yêu cầu backend quét database, chạy lại Apriori và cập nhật RAM
      const res = await api.post("/api/admin/re-train");
      setMessage(res.data.message || "🔄 Đã huấn luyện lại dữ liệu và đồng bộ luật mới thành công!");
    } catch (err) {
      setError(err.response?.data?.error || "Không thể kết nối đến máy chủ hoặc bạn không có quyền Admin.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: "800px", margin: "40px auto", padding: "30px", border: "1px solid #e0e0e0", borderRadius: "12px", background: "#fff", boxShadow: "0 4px 12px rgba(0,0,0,0.05)" }}>
      <h2 style={{ color: "#2c3e50", borderBottom: "2px solid #e74c3c", paddingBottom: "12px", marginTop: 0 }}>
        🛡️ BÀN LÀM VIỆC CỦA QUẢN TRỊ VIÊN (ADMIN DASHBOARD)
      </h2>
      
      <p style={{ color: "#666", lineHeight: "1.6", fontSize: "15px" }}>
        Mỗi khi hệ thống e-commerce phát sinh thêm nhiều đơn đặt hàng mới từ khách hàng, Admin có thể kích hoạt tiến trình dưới đây để <strong>Cập nhật mô hình gợi ý sản phẩm</strong>.
      </p>

      <div style={{ background: "#fff3cd", color: "#856404", padding: "15px", borderRadius: "6px", margin: "20px 0", borderLeft: "5px solid #ffc107", fontSize: "14px" }}>
        <strong>💡 Mô tả luồng chạy thuật toán khép kín:</strong>
        <ol style={{ margin: "5px 0 0 20px", padding: 0 }}>
          <li>Hệ thống thực hiện quét toàn bộ hóa đơn thành công trong Database.</li>
          <li>Xuất lịch sử mua sắm thực tế ra tập tin cấu trúc dữ liệu <code>data/transactions.csv</code>.</li>
          <li>Chạy thuật toán <strong>Apriori</strong> (Thuần Python) để tự động tính toán Support, Confidence và kết xuất tập luật kết hợp mới.</li>
          <li>Nạp nóng tập luật mới vào bộ nhớ đệm RAM của hệ thống Flask ngay lập tức mà không cần khởi động lại Server.</li>
        </ol>
      </div>

      <div style={{ textAlign: "center", marginTop: "30px" }}>
        <button
          onClick={handleRetrain}
          disabled={loading}
          style={{
            padding: "15px 35px",
            background: loading ? "#bdc3c7" : "#e74c3c",
            color: "#fff",
            border: "none",
            borderRadius: "30px",
            fontSize: "16px",
            fontWeight: "bold",
            cursor: loading ? "not-allowed" : "pointer",
            boxShadow: "0 4px 10px rgba(231, 76, 60, 0.3)",
            transition: "all 0.2s"
          }}
        >
          {loading ? "⏳ Hệ thống đang chạy thuật toán Apriori..." : "🔄 Cập nhật & Tái huấn luyện bộ luật gợi ý"}
        </button>
      </div>

      {/* Thông báo trạng thái */}
      {message && (
        <div style={{ marginTop: "20px", padding: "15px", background: "#d4edda", color: "#155724", borderRadius: "6px", borderLeft: "5px solid #28a745", fontWeight: "500" }}>
          🚀 {message}
        </div>
      )}

      {error && (
        <div style={{ marginTop: "20px", padding: "15px", background: "#f8d7da", color: "#721c24", borderRadius: "6px", borderLeft: "5px solid #dc3545", fontWeight: "500" }}>
          ❌ {error}
        </div>
      )}
    </div>
  );
}