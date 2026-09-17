import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function LoginPage() {
  const { login }   = useAuth();
  const navigate    = useNavigate();
  const [form,     setForm]   = useState({ email: "", password: "" });
  const [error,    setError]  = useState("");
  const [loading,  setLoading] = useState(false);

  const handleChange = (e) =>
    setForm((f) => ({ ...f, [e.target.name]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(form.email, form.password);
      navigate("/");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-wrapper">
      <div className="auth-card">
        <h1>Đăng nhập</h1>
        <p className="auth-sub">Hệ thống gợi ý sản phẩm mua kèm</p>

        {error && <div className="auth-error">{error}</div>}

        <form onSubmit={handleSubmit}>
          <label>Email</label>
          <input
            type="email" name="email" required
            value={form.email} onChange={handleChange}
            placeholder="example@email.com"
          />

          <label>Mật khẩu</label>
          <input
            type="password" name="password" required
            value={form.password} onChange={handleChange}
            placeholder="••••••••"
          />

          <button type="submit" disabled={loading}>
            {loading ? "Đang đăng nhập..." : "Đăng nhập"}
          </button>
        </form>

        <p className="auth-link">
          Chưa có tài khoản? <Link to="/register">Đăng ký ngay</Link>
        </p>
        <p className="auth-link">
         <Link to="/forgot-password">Quên mật khẩu?</Link>
        </p>
      </div>
    </div>
  );
}
