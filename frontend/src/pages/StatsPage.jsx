import { useState, useEffect } from "react";
import api from "../services/api";

export default function StatsPage() {
  const [stats, setStats] = useState({ day: [], week: [], month: [] });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get("/api/stats")
      .then(res => {
        if (res.data?.data) setStats(res.data.data);
      })
      .catch(err => console.error("Lỗi lấy dữ liệu thống kê:", err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div style={{ textAlign: "center", padding: "40px" }}>Đang kết nối cơ sở dữ liệu thống kê...</div>;

  const renderTable = (title, list, color) => (
    <div style={{ flex: 1, minWidth: "280px", background: "#fff", padding: "15px", borderRadius: "8px", border: "1px solid #e0e0e0", boxShadow: "0 2px 4px rgba(0,0,0,0.02)" }}>
      <h3 style={{ color: color, marginTop: 0, borderBottom: `2px solid ${color}`, paddingBottom: "8px", display: "flex", justifyContent: "space-between" }}>
        <span>{title}</span>
        <span style={{ fontSize: "12px", background: "#f1f2f6", padding: "2px 8px", borderRadius: "10px", color: "#555" }}>Top 5</span>
      </h3>
      {list.length === 0 ? (
        <p style={{ color: "#aaa", textAlign: "center", fontSize: "14px", padding: "15px 0" }}>Chưa có đơn hàng nào trong chu kỳ này.</p>
      ) : (
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "13px" }}>
          <thead>
            <tr style={{ textAlign: "left", color: "#7f8c8d", borderBottom: "1px solid #eee" }}>
              <th style={{ padding: "8px 4px" }}>Tên sản phẩm</th>
              <th style={{ padding: "8px 4px", textAlign: "right" }}>Số lượng mua</th>
            </tr>
          </thead>
          <tbody>
            {list.map((item, index) => (
              <tr key={index} style={{ borderBottom: "1px solid #f9f9f9" }}>
                <td style={{ padding: "10px 4px", fontWeight: "500", color: "#2c3e50" }}>{item.name}</td>
                <td style={{ padding: "10px 4px", textAlign: "right", fontWeight: "bold", color: color }}>{item.quantity}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );

  return (
    <div>
      <h2 style={{ color: "#2c3e50", marginBottom: "5px" }}>📈 Thống kê các sản phẩm bán chạy</h2>
      <p style={{ color: "#7f8c8d", fontSize: "14px", marginBottom: "25px" }}>
        Dữ liệu được cập nhật tự động theo thời gian thực dựa trên các đơn hàng đã thanh toán thành công.
      </p>

      <div style={{ display: "flex", flexWrap: "wrap", gap: "20px" }}>
        {renderTable("🔥 Bán chạy trong ngày", stats.day, "#e74c3c")}
        {renderTable("⭐️ Bán chạy trong tuần", stats.week, "#3498db")}
        {renderTable("📊 Bán chạy trong tháng", stats.month, "#1abc9c")}
      </div>
    </div>
  );
}