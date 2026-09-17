import { useState } from "react";
import PRODUCTS from "../products.json";

export default function CartPanel({ cart, setCart }) {
  const [search, setSearch] = useState("");

  const filtered = PRODUCTS.filter(
    (p) => p.toLowerCase().includes(search.toLowerCase()) && !cart.includes(p)
  );

  const addItem    = (item) => {
    setCart((c) => [...c, item]);
    setSearch(""); // Xóa chữ đã tìm kiếm sau khi chọn
  };
  const removeItem = (item) => setCart((c) => c.filter((x) => x !== item));

  return (
    <div className="cart-panel" style={{ padding: "20px", border: "1px solid #ddd", borderRadius: "8px", background: "#fff" }}>
      <h3 style={{ borderBottom: "2px solid #3498db", paddingBottom: "10px", marginVertical: "0 15px" }}>
        🛒 Giỏ hàng của bạn ({cart.length})
      </h3>

      {/* Danh sách các sản phẩm đã chọn */}
      <div className="cart-items" style={{ display: "flex", flexWrap: "wrap", gap: "8px", marginBottom: "15px", minHeight: "40px" }}>
        {cart.length === 0 && <p className="empty" style={{ color: "#999", fontSize: "14px" }}>Chưa có sản phẩm nào trong giỏ.</p>}
        {cart.map((item) => (
          <div key={item} className="cart-tag" style={{ background: "#e1f5fe", color: "#0288d1", padding: "6px 12px", borderRadius: "20px", display: "flex", alignItems: "center", gap: "8px", fontSize: "14px", fontWeight: "500" }}>
            <span>{item}</span>
            <button onClick={() => removeItem(item)} style={{ background: "none", border: "none", color: "#e53935", cursor: "pointer", fontWeight: "bold" }}>✕</button>
          </div>
        ))}
      </div>

      {/* Thanh Tìm kiếm */}
      <div style={{ marginBottom: "10px" }}>
        <input
          type="text"
          placeholder="🔎 Nhập tên sản phẩm để thêm vào giỏ..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="search-input"
          style={{ width: "100%", padding: "10px", borderRadius: "6px", border: "1px solid #ccc", boxSizing: "border-box" }}
        />
      </div>

      {/* Kết quả tìm kiếm nhanh */}
      {search && (
        <div className="product-list" style={{ border: "1px solid #eee", borderRadius: "6px", maxHeight: "200px", overflowY: "auto", background: "#fafafa" }}>
          {filtered.length === 0 && <p style={{ padding: "10px", color: "#999", fontSize: "13px" }}>Không tìm thấy sản phẩm phù hợp.</p>}
          {filtered.slice(0, 10).map((p) => (
            <div 
              key={p} 
              className="product-item" 
              onClick={() => addItem(p)}
              style={{ padding: "10px 15px", borderBottom: "1px solid #eee", cursor: "pointer", display: "flex", justifyContent: "space-between", alignItems: "center", transition: "background 0.2s" }}
              onMouseEnter={(e) => e.currentTarget.style.background = "#f1f1f1"}
              onMouseLeave={(e) => e.currentTarget.style.background = "none"}
            >
              <span style={{ fontSize: "14px" }}>{p}</span>
              <span style={{ color: "#2ecc71", fontWeight: "bold" }}>+ Thêm</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}