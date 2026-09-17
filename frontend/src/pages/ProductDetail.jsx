import { useParams, useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
import { useCart } from "../context/CartContext";
import api from "../services/api";

export default function ProductDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { addToCart } = useCart();
  const [quantity, setQuantity] = useState(1);
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");

  useEffect(() => {
    api
      .get(`/api/products/${id}`)
      .then((res) => setProduct(res.data.product))
      .catch(() => setProduct(null))
      .finally(() => setLoading(false));
  }, [id]);

  const handleAddToCart = () => {
    if (quantity > product.stock) {
      setMessage(`❌ Số lượng không vượt quá ${product.stock}`);
      setTimeout(() => setMessage(""), 3000);
      return;
    }
    addToCart({ id: product.id, name: product.name, price: product.price, quantity });
    setMessage(`✅ Đã thêm ${quantity} ${product.name} vào giỏ hàng`);
    setQuantity(1);
    setTimeout(() => setMessage(""), 3000);
  };

  const handleBuyNow = () => {
    if (quantity > product.stock) {
      setMessage(`❌ Số lượng không vượt quá ${product.stock}`);
      setTimeout(() => setMessage(""), 3000);
      return;
    }
    addToCart({ id: product.id, name: product.name, price: product.price, quantity });
    navigate("/");
  };

  if (loading) return <div style={{ padding: 40, textAlign: "center" }}>Đang tải...</div>;

  if (!product) return <div style={{ padding: 40, textAlign: "center" }}>Sản phẩm không tồn tại!</div>;

  const imageSrc = product.image_url?.startsWith("http")
    ? product.image_url
    : product.image_url
      ? `http://localhost:5000${product.image_url}`
      : `https://picsum.photos/seed/${product.name}/600/400`;

  return (
    <div style={{ maxWidth: "900px", margin: "40px auto", padding: "20px", fontFamily: "Arial, sans-serif" }}>
      <button onClick={() => navigate(-1)} style={{ marginBottom: "20px", cursor: "pointer" }}>⬅ Quay lại</button>

      {message && (
        <div style={{ padding: "12px 16px", background: message.startsWith("❌") ? "#fdecea" : "#e8f4fd", color: message.startsWith("❌") ? "#c0392b" : "#27ae60", borderRadius: "6px", marginBottom: "20px", fontWeight: "500" }}>
          {message}
        </div>
      )}

      <div style={{ display: "flex", gap: "40px", flexWrap: "wrap" }}>
        <div style={{ flex: "1", minWidth: "300px" }}>
          <img src={imageSrc} alt={product.name} style={{ width: "100%", borderRadius: "12px", boxShadow: "0 4px 12px rgba(0,0,0,0.1)" }} />
        </div>

        <div style={{ flex: "1", minWidth: "300px" }}>
          <h1>{product.name}</h1>
          <p style={{ fontSize: "1.5rem", color: "#e74c3c", fontWeight: "bold" }}>
            {product.price.toLocaleString()} VNĐ
          </p>
          <p style={{ color: "#666", lineHeight: "1.6" }}>
            {product.description || `Mô tả sản phẩm: Đây là thông tin chi tiết về ${product.name}.`}
          </p>
          {product.category && (
            <p style={{ color: "#888", fontSize: "0.9rem" }}>Danh mục: {product.category}</p>
          )}
          {product.stock > 0 ? (
            <p style={{ color: "#27ae60", fontSize: "0.9rem" }}>Còn hàng ({product.stock})</p>
          ) : (
            <p style={{ color: "#e74c3c", fontSize: "0.9rem" }}>Hết hàng</p>
          )}

          <div style={{ margin: "20px 0" }}>
            <label>Số lượng: </label>
            <input 
              type="number" 
              min="1" 
              max={product.stock} 
              value={quantity} 
              onChange={(e) => setQuantity(Math.max(1, Math.min(product.stock, Number(e.target.value))))}
              disabled={product.stock === 0}
              style={{ padding: "8px", width: "50px" }} 
            />
          </div>

          <div style={{ display: "flex", gap: "10px" }}>
            <button
              onClick={handleAddToCart}
              disabled={product.stock === 0}
              style={{ padding: "12px 24px", background: product.stock === 0 ? "#95a5a6" : "#1abc9c", color: "#fff", border: "none", borderRadius: "5px", cursor: product.stock === 0 ? "not-allowed" : "pointer", fontSize: "1rem", fontWeight: "bold" }}
            >
              {product.stock === 0 ? "Hết hàng" : "Thêm vào giỏ"}
            </button>
            <button 
              onClick={handleBuyNow}
              disabled={product.stock === 0}
              style={{ padding: "12px 24px", background: product.stock === 0 ? "#95a5a6" : "#f39c12", color: "#fff", border: "none", borderRadius: "5px", cursor: product.stock === 0 ? "not-allowed" : "pointer", fontSize: "1rem", fontWeight: "bold" }}
            >
              {product.stock === 0 ? "Hết hàng" : "Mua ngay"}
            </button>
          </div>
        </div>
      </div>

      <div style={{ marginTop: "60px", borderTop: "1px solid #eee", paddingTop: "20px" }}>
        <h3>Bình luận</h3>
        <textarea style={{ width: "100%", height: "80px", marginBottom: "10px", padding: "10px" }} placeholder="Viết bình luận của bạn..."></textarea>
        <button style={{ padding: "8px 16px", background: "#3498db", color: "#fff", border: "none", borderRadius: "4px" }}>Gửi bình luận</button>
      </div>
    </div>
  );
}
