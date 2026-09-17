import { BrowserRouter, Routes, Route, Link, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import { CartProvider } from "./context/CartContext";
import ProtectedRoute  from "./components/ProtectedRoute";
import HomePage        from "./pages/HomePage";
import ComparePage     from "./pages/ComparePage"; 
import StatsPage       from "./pages/StatsPage";
import LoginPage       from "./pages/LoginPage";
import RegisterPage    from "./pages/RegisterPage";
import ProfilePage     from "./pages/ProfilePage";
import ForgotPasswordPage from "./pages/ForgotPasswordPage";
import ProductDetail from "./pages/ProductDetail";

function Navbar() {
  const { user, logout } = useAuth();
  return (
    <nav className="navbar" style={{ display: "flex", justifyContent: "space-between", padding: "15px 30px", background: "#2c3e50", color: "#fff" }}>
      <Link to="/" className="nav-brand" style={{ color: "#fff", fontWeight: "bold", textDecoration: "none", fontSize: "18px" }}>🛒 Siêu thị gia dụng</Link>
      <div className="nav-links" style={{ display: "flex", gap: "20px", alignItems: "center" }}>
        <Link to="/" style={{ color: "#fff", textDecoration: "none" }}>🏪 Cửa hàng</Link>
        <Link to="/compare" style={{ color: "#fff", textDecoration: "none" }}>💡 Gợi ý mua kèm</Link>
        <Link to="/stats" style={{ color: "#fff", textDecoration: "none" }}>📈 Thống kê</Link>
        {user ? (
          <>
            <Link to="/profile" style={{ color: "#1abc9c", textDecoration: "none", fontWeight: "bold" }}>🧑 {user.username}</Link>
            <button onClick={logout} className="btn-outline-sm" style={{ background: "none", border: "1px solid #fff", color: "#fff", padding: "4px 10px", borderRadius: "4px", cursor: "pointer" }}>Đăng xuất</button>
          </>
        ) : (
          <>
            <Link to="/login" style={{ color: "#fff", textDecoration: "none" }}>Đăng nhập</Link>
            <Link to="/register" style={{ background: "#1abc9c", color: "#fff", padding: "5px 12px", borderRadius: "4px", textDecoration: "none" }}>Đăng ký</Link>
          </>
        )}
      </div>
    </nav>
  );
}

function AppRoutes() {
  return (
    <>
      <Navbar />
      <main className="main-content" style={{ padding: "25px" }}>
        <Routes>
          <Route path="/"          element={<HomePage />} />
          <Route path="/compare"   element={<ComparePage />} />
          <Route path="/stats"     element={<StatsPage />} />
          <Route path="/login"     element={<LoginPage />} />
          <Route path="/register"  element={<RegisterPage />} />
          <Route path="/profile"   element={<ProtectedRoute><ProfilePage /></ProtectedRoute>} />
          <Route path="/forgot-password" element={<ForgotPasswordPage />} />
          <Route path="/product/:id" element={<ProductDetail />} />
          <Route path="*"          element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <CartProvider>
        <AppRoutes />
        </CartProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}
