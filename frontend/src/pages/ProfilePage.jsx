import { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import api from "../services/api";

export default function ProfilePage() {
  const { user, logout }   = useAuth();
  const [tab,       setTab]       = useState("history"); 
  const [history,   setHistory]   = useState([]);
  const [favorites, setFavorites] = useState([]);
  const [address,   setAddress]   = useState(""); 
  const [loading,   setLoading]   = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [msg,       setMsg]       = useState("");

  useEffect(() => {
    const fetchAll = async () => {
      try {
        const [hRes, fRes, aRes] = await Promise.all([
          api.get("/user/history"),
          api.get("/user/favorites"),
          api.get("/user/profile/address").catch(() => ({ data: { address: "" } }))
        ]);
        setHistory(hRes.data.history || []);
        setFavorites(fRes.data.favorites || []);
        setAddress(aRes.data?.address || "");
      } catch (err) {
        console.error("Lỗi tải thông tin profile:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchAll();
  }, []);

  const deleteHistory = async (id) => {
    await api.delete(`/user/history/${id}`);
    setHistory((h) => h.filter((r) => r.id !== id));
  };

  const removeFavorite = async (productId) => {
    await api.post("/user/favorites", { product_id: productId });
    setFavorites((f) => f.filter((r) => r.product_id !== productId));
  };

  const handleSaveAddress = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setMsg("");
    try {
      const res = await api.put("/user/profile/address", { address: address });
      setMsg("🎉 " + (res.data.message || "Cập nhật địa chỉ thành công!"));
    } catch (err) {
      setMsg("❌ Lỗi: " + (err.response?.data?.error || err.message));
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <div className="loading" style={{ textAlign: "center", padding: "40px" }}>Đang tải dữ liệu...</div>;

  return (
    <div className="profile-page" style={{ maxWidth: "800px", margin: "20px auto", padding: "20px", background: "#fff", borderRadius: "8px", border: "1px solid #e0e0e0" }}>
      <div className="profile-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: "2px solid #eee", paddingBottom: "15px", marginBottom: "20px" }}>
        <div>
          <h2 style={{ margin: 0, color: "#2c3e50" }}>👤 Trang cá nhân</h2>
          <p style={{ margin: "5px 0 0 0", color: "#7f8c8d", fontSize: "14px" }}>Xin chào, <b>{user?.username}</b> ({user?.email})</p>
        </div>
        <button onClick={logout} className="btn-outline-sm" style={{ padding: "6px 12px", background: "#e74c3c", color: "#fff", border: "none", borderRadius: "4px", cursor: "pointer", fontWeight: "bold" }}>Đăng xuất</button>
      </div>

      {/* Tabs Selector Navigation */}
      <div className="profile-tabs" style={{ display: "flex", gap: "10px", marginBottom: "20px", borderBottom: "1px solid #ddd", paddingBottom: "10px" }}>
        <button 
          className={tab === "history" ? "tab-btn active" : "tab-btn"} 
          onClick={() => setTab("history")}
          style={{ padding: "8px 16px", cursor: "pointer", background: tab === "history" ? "#2c3e50" : "#f1f2f6", color: tab === "history" ? "#fff" : "#333", border: "none", borderRadius: "4px", fontWeight: "bold" }}
        >
          📜 Lịch sử gợi ý
        </button>
        <button 
          className={tab === "favorites" ? "tab-btn active" : "tab-btn"} 
          onClick={() => setTab("favorites")}
          style={{ padding: "8px 16px", cursor: "pointer", background: tab === "favorites" ? "#2c3e50" : "#f1f2f6", color: tab === "favorites" ? "#fff" : "#333", border: "none", borderRadius: "4px", fontWeight: "bold" }}
        >
          ❤️ Sản phẩm yêu thích
        </button>
        <button 
          className={tab === "address" ? "tab-btn active" : "tab-btn"} 
          onClick={() => setTab("address")}
          style={{ padding: "8px 16px", cursor: "pointer", background: tab === "address" ? "#2c3e50" : "#f1f2f6", color: tab === "address" ? "#fff" : "#333", border: "none", borderRadius: "4px", fontWeight: "bold" }}
        >
          📍 Địa chỉ nhận hàng
        </button>
      </div>

      {/* History Tab */}
      {tab === "history" && (
        <div className="tab-content">
          {history.length === 0 ? (
            <p className="empty">Chưa có lịch sử tìm kiếm.</p>
          ) : (
            history.map((record) => (
              <div key={record.id} className="history-card" style={{ border: "1px solid #eee", padding: "15px", borderRadius: "6px", marginBottom: "15px" }}>
                <div className="history-meta" style={{ display: "flex", justifyContent: "space-between", marginBottom: "8px", fontSize: "12px", color: "#95a5a6" }}>
                  <span className="algo-badge" style={{ background: "#3498db", color: "#fff", padding: "2px 6px", borderRadius: "4px", fontWeight: "bold" }}>{record.algorithm}</span>
                  <span className="date">{new Date(record.searched_at).toLocaleString("vi-VN")}</span>
                </div>
                <p style={{ margin: "5px 0" }}><strong>Giỏ hàng:</strong> {record.cart_items.join(", ")}</p>
                <p style={{ margin: "5px 0" }}>
                  <strong>Gợi ý:</strong>{" "}
                  {record.recommendations.map((r) => r.product_id).join(", ") || "Không có"}
                </p>
                <button className="btn-delete" onClick={() => deleteHistory(record.id)} style={{ background: "none", border: "none", color: "#e74c3c", cursor: "pointer", fontSize: "13px", padding: 0, textDecoration: "underline" }}>Xóa</button>
              </div>
            ))
          )}
        </div>
      )}

      {/* Favorites Tab */}
      {tab === "favorites" && (
        <div className="tab-content">
          {favorites.length === 0 ? (
            <p className="empty">Chưa có sản phẩm yêu thích.</p>
          ) : (
            <div className="favorites-grid" style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))", gap: "15px" }}>
              {favorites.map((fav) => (
                <div key={fav.id} className="fav-card" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "12px", border: "1px solid #eee", borderRadius: "6px", background: "#fdfefe" }}>
                  <span style={{ fontSize: "13px", fontWeight: "500", color: "#2c3e50" }}>{fav.product_id}</span>
                  <button onClick={() => removeFavorite(fav.product_id)} style={{ background: "none", border: "none", color: "#ccc", cursor: "pointer", fontSize: "16px" }}>✕</button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Address Tab */}
      {tab === "address" && (
        <div className="tab-content" style={{ background: "#f8f9fa", padding: "20px", borderRadius: "6px", border: "1px solid #e2e8f0" }}>
          <h3 style={{ marginTop: 0, color: "#2c3e50" }}>📍 Sổ địa chỉ giao hàng</h3>
          <p style={{ color: "#7f8c8d", fontSize: "13px", marginBottom: "15px" }}>
            Địa chỉ này sẽ được hệ thống tự động điền vào hóa đơn mỗi khi bạn thực hiện mua sắm tại Cửa hàng.
          </p>

          {msg && (
            <div style={{ padding: "10px", background: msg.startsWith("❌") ? "#fce4e4" : "#e8f4fd", color: msg.startsWith("❌") ? "#c0392b" : "#2980b9", borderRadius: "6px", marginBottom: "15px", fontSize: "13px", fontWeight: "500" }}>
              {msg}
            </div>
          )}

          <form onSubmit={handleSaveAddress}>
            <div style={{ marginBottom: "15px" }}>
              <label style={{ display: "block", fontWeight: "bold", fontSize: "13px", color: "#34495e", marginBottom: "6px" }}>
                Địa chỉ nhận hàng mặc định của bạn:
              </label>
              <textarea
                rows="4"
                placeholder="Nhập chính xác số nhà, tên đường, phường/xã, quận/huyện, tỉnh/thành phố..."
                value={address}
                onChange={(e) => setAddress(e.target.value)}
                style={{ width: "100%", padding: "10px", border: "1px solid #cbd5e1", borderRadius: "6px", fontSize: "14px", fontFamily: "inherit", resize: "none" }}
                required
              />
            </div>
            <button
              type="submit"
              disabled={submitting}
              style={{ background: "#1abc9c", color: "#fff", border: "none", padding: "10px 20px", borderRadius: "4px", cursor: "pointer", fontWeight: "bold", fontSize: "14px" }}
            >
              {submitting ? "Đang lưu cấu hình..." : "💾 Lưu địa chỉ"}
            </button>
          </form>
        </div>
      )}
    </div>
  );
}