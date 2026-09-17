import { useState, useEffect, useMemo } from "react";
import { useAuth } from "../context/AuthContext";
import { useCart } from "../context/CartContext";
import { useNavigate } from "react-router-dom";
import api from "../services/api";
import { Link } from "react-router-dom";

export default function HomePage() {
  const { user } = useAuth();
  const { cart, addToCart, updateQuantity, removeFromCart, clearCart } = useCart();
  const navigate = useNavigate();
  const [userAddress, setUserAddress] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [search, setSearch] = useState("");
  const [products, setProducts] = useState([]);
  const [productsLoading, setProductsLoading] = useState(true);

  useEffect(() => {
    // Fetch danh sách sản phẩm từ backend
    setProductsLoading(true);
    api.get("/api/products")
      .then(res => {
        const productData = res.data.products.map((product, index) => ({
          id: product.id,
          name: product.name,
          price: product.price || 99999,
          image: product.image_url || `https://picsum.photos/id/${(index + 10) * 3}/200/180`
        }));
        setProducts(productData);
      })
      .catch(err => console.error("Không lấy được danh sách sản phẩm:", err))
      .finally(() => setProductsLoading(false));
  }, []);

  useEffect(() => {
    if (user) {
      api.get("/user/profile/address")
        .then(res => setUserAddress(res.data.address || ""))
        .catch(err => console.error("Không lấy được địa chỉ người dùng:", err));
    }
  }, [user]);

  const filteredProducts = useMemo(() => 
    products.filter(p =>
      p.name.toLowerCase().includes(search.toLowerCase())
    ),
    [products, search]
  );

  const handleCheckout = async () => {
    if (!user) { alert("Vui lòng đăng nhập để thực hiện thanh toán!"); return; }
    if (cart.length === 0) return;
    if (!userAddress) { alert("Vui lòng thiết lập địa chỉ nhận hàng trước khi thanh toán!"); return; }

    setLoading(true);
    setMessage("");
    try {
      const orderItems = cart.map(item => ({ product_id: item.id, quantity: item.quantity }));
      await api.post("/api/orders", { items: orderItems, address: userAddress });
      await api.post("/api/admin/re-train");
      setMessage("🎉 Thanh toán thành công! Hệ thống đã nhận đơn và tự động Re-train dữ liệu.");
      clearCart();
    } catch (err) {
      setMessage("❌ Lỗi thanh toán: " + (err.response?.data?.message || err.message));
    } finally {
      setLoading(false);
    }
  };

  const totalAmount = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);

  return (
    <div style={{ display: "flex", gap: "25px" }}>
      {/* Danh sách sản phẩm */}
      <div style={{ flex: 3 }}>
        <h2 style={{ color: "#2c3e50", marginBottom: "15px" }}>🛒 Cửa hàng công nghệ & Quà lưu niệm</h2>

        {message && (
          <div style={{ padding: "12px", background: message.startsWith("❌") ? "#fdecea" : "#e8f4fd", color: message.startsWith("❌") ? "#c0392b" : "#2980b9", borderRadius: "6px", marginBottom: "15px", fontWeight: "500" }}>
            {message}
          </div>
        )}

        {/* Thanh tìm kiếm */}
        <div style={{ marginBottom: "20px", display: "flex", alignItems: "center", gap: "10px" }}>
          <input
            type="text"
            placeholder="🔍 Tìm kiếm sản phẩm..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            disabled={productsLoading}
            style={{ flex: 1, padding: "10px 14px", border: "1px solid #ddd", borderRadius: "6px", fontSize: "14px", outline: "none", boxShadow: "0 1px 3px rgba(0,0,0,0.05)" }}
          />
          {search && (
            <button onClick={() => setSearch("")} style={{ padding: "10px 14px", background: "#ecf0f1", border: "none", borderRadius: "6px", cursor: "pointer", fontSize: "13px", color: "#7f8c8d" }}>
              ✕ Xóa
            </button>
          )}
          <span style={{ fontSize: "13px", color: "#95a5a6", whiteSpace: "nowrap" }}>{productsLoading ? "Đang tải..." : `${filteredProducts.length} sản phẩm`}</span>
        </div>

        {productsLoading ? (
          <div style={{ textAlign: "center", padding: "40px", color: "#aaa" }}>
            <div style={{ fontSize: "24px", marginBottom: "10px", animation: "spin 1s linear infinite" }}>⏳</div>
            <div>Đang tải danh sách sản phẩm...</div>
          </div>
        ) : products.length === 0 ? (
          <div style={{ textAlign: "center", padding: "40px", color: "#aaa" }}>
            <div style={{ fontSize: "40px", marginBottom: "10px" }}>📭</div>
            <div>Không có sản phẩm nào.</div>
          </div>
        ) : filteredProducts.length === 0 ? (
          <div style={{ textAlign: "center", padding: "40px", color: "#aaa" }}>
            <div style={{ fontSize: "40px", marginBottom: "10px" }}>🔍</div>
            <div>Không tìm thấy sản phẩm nào khớp với "<strong>{search}</strong>"</div>
          </div>
        ) : (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))", gap: "20px" }}>
            {filteredProducts.map(p => {
              const inCart = cart.some(item => item.id === p.id);
              return (
                // 2. Bọc toàn bộ card sản phẩm bằng Link
                <Link 
                  key={p.id} 
                  to={`/product/${p.id}`} 
                  style={{ textDecoration: "none", color: "inherit" }}
                >
                  <div style={{ border: "1px solid #e0e0e0", borderRadius: "8px", background: "#fff", overflow: "hidden", display: "flex", flexDirection: "column", justifyContent: "space-between", boxShadow: "0 2px 5px rgba(0,0,0,0.05)", height: "100%" }}>
                    <img src={p.image} alt={p.name} style={{ width: "100%", height: "140px", objectFit: "cover" }} />
                    <div style={{ padding: "12px", flex: 1, display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
                      <div style={{ fontWeight: "bold", fontSize: "13px", color: "#2c3e50", minHeight: "36px", marginBottom: "8px" }}>{p.name}</div>
                      <div>
                        <div style={{ color: "#e74c3c", fontWeight: "bold", marginBottom: "10px" }}>{p.price.toLocaleString()} VNĐ</div>
                        {/* Ngăn sự kiện click vào nút Add to cart làm chuyển hướng trang */}
                        <button
                          onClick={(e) => {
                            e.preventDefault(); // Ngăn Link kích hoạt
                            inCart ? removeFromCart(p.id) : addToCart(p);
                          }}
                          style={{ width: "100%", padding: "8px", background: inCart ? "#e74c3c" : "#2c3e50", color: "#fff", border: "none", borderRadius: "4px", cursor: "pointer", fontWeight: "500" }}
                        >
                          {inCart ? "✕ Bỏ khỏi giỏ" : "+ Thêm vào giỏ"}
                        </button>
                      </div>
                    </div>
                  </div>
                </Link>
              );
            })}
          </div>
        )}
      </div>
        

      {/* Giỏ hàng sidebar */}
      <div style={{ flex: 1, background: "#f8f9fa", border: "1px solid #e0e0e0", borderRadius: "8px", padding: "20px", height: "fit-content", minWidth: "280px", position: "sticky", top: "20px" }}>
        <h3 style={{ marginTop: 0, color: "#2c3e50", borderBottom: "2px solid #eee", paddingBottom: "10px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <span>Giỏ hàng hiện tại</span>
          {cart.length > 0 && (
            <span style={{ fontSize: "12px", background: "#e74c3c", color: "#fff", borderRadius: "50%", width: "22px", height: "22px", display: "flex", alignItems: "center", justifyContent: "center" }}>
              {cart.length}
            </span>
          )}
        </h3>

        {cart.length === 0 ? (
          <p style={{ color: "#aaa", textAlign: "center", padding: "20px 0" }}>Giỏ hàng đang trống.</p>
        ) : (
          <div>
            <div style={{ maxHeight: "250px", overflowY: "auto", marginBottom: "15px" }}>
              {cart.map(item => (
                <div key={item.id} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "10px 0", borderBottom: "1px dashed #ddd" }}>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontSize: "12px", fontWeight: "bold", color: "#2c3e50", marginBottom: "4px" }}>{item.name}</div>
                    <div style={{ fontSize: "11px", color: "#7f8c8d", marginBottom: "6px" }}>{item.price.toLocaleString()}đ</div>
                    {/* Quantity Controls */}
                    <div style={{ display: "flex", alignItems: "center", gap: "4px" }}>
                      <button 
                        onClick={() => updateQuantity(item.id, item.quantity - 1)}
                        style={{ background: "#ecf0f1", border: "none", borderRadius: "3px", width: "20px", height: "20px", cursor: "pointer", fontSize: "12px", color: "#2c3e50" }}
                      >
                        −
                      </button>
                      <span style={{ fontSize: "11px", fontWeight: "bold", minWidth: "20px", textAlign: "center" }}>{item.quantity}</span>
                      <button 
                        onClick={() => updateQuantity(item.id, item.quantity + 1)}
                        style={{ background: "#ecf0f1", border: "none", borderRadius: "3px", width: "20px", height: "20px", cursor: "pointer", fontSize: "12px", color: "#2c3e50" }}
                      >
                        +
                      </button>
                    </div>
                  </div>
                  <button 
                    onClick={() => removeFromCart(item.id)} 
                    style={{ background: "none", border: "none", color: "#e74c3c", cursor: "pointer", fontSize: "16px", marginLeft: "8px" }}
                  >
                    ✕
                  </button>
                </div>
              ))}
            </div>

            {/* Gợi ý mua kèm */}
            {cart.length > 0 && (
              <button
                onClick={() => navigate("/compare")}
                style={{ width: "100%", padding: "9px", background: "#9b59b6", color: "#fff", border: "none", borderRadius: "6px", cursor: "pointer", fontWeight: "bold", fontSize: "13px", marginBottom: "10px" }}
              >
                🔮 Xem gợi ý mua kèm ({cart.length} SP)
              </button>
            )}

            <div style={{ marginBottom: "15px", background: "#fff", padding: "12px", borderRadius: "6px", border: "1px solid #ebdada" }}>
              <span style={{ display: "block", fontSize: "12px", fontWeight: "bold", color: "#2c3e50", marginBottom: "4px" }}>📍 Địa chỉ giao hàng:</span>
              {userAddress ? (
                <p style={{ margin: 0, fontSize: "12px", color: "#27ae60", fontWeight: "500", lineHeight: "1.4" }}>{userAddress}</p>
              ) : (
                <div>
                  <p style={{ margin: "0 0 6px 0", fontSize: "11px", color: "#e67e22", fontWeight: "500" }}>⚠️ Bạn chưa thiết lập địa chỉ nhận hàng!</p>
                  <button onClick={() => navigate("/profile")} style={{ background: "none", border: "none", color: "#2980b9", padding: 0, textDecoration: "underline", fontSize: "11px", cursor: "pointer", fontWeight: "bold" }}>
                    Cài đặt địa chỉ tại đây
                  </button>
                </div>
              )}
            </div>

            <div style={{ borderTop: "2px solid #eee", paddingTop: "12px", marginBottom: "15px", display: "flex", justifyContent: "space-between", fontWeight: "bold" }}>
              <span>Tổng tiền:</span>
              <span style={{ color: "#e74c3c" }}>{totalAmount.toLocaleString()} VNĐ</span>
            </div>

            <button
              onClick={handleCheckout}
              disabled={loading || !userAddress}
              style={{ width: "100%", padding: "12px", background: userAddress ? "#1abc9c" : "#95a5a6", color: "#fff", border: "none", borderRadius: "6px", cursor: userAddress ? "pointer" : "not-allowed", fontWeight: "bold", fontSize: "15px" }}
            >
              {loading ? "Đang xử lý..." : !userAddress ? "🔒 Cài địa chỉ để mua hàng" : "💳 Thanh toán đơn hàng"}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
