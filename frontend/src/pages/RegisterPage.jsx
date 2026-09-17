import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function RegisterPage() {
  const { register } = useAuth();
  const navigate     = useNavigate();
  const [form,    setForm]    = useState({ username: "", email: "", password: "", confirm: "" });
  const [error,   setError]   = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (e) =>
    setForm((f) => ({ ...f, [e.target.name]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    if (form.password !== form.confirm) {
      setError("Mật khẩu xác nhận không khớp.");
      return;
    }
    if (form.password.length < 6) {
      setError("Mật khẩu ít nhất 6 ký tự.");
      return;
    }
    setLoading(true);
    try {
      await register(form.username, form.email, form.password);
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
        <h1>Đăng ký</h1>
        <p className="auth-sub">Tạo tài khoản để lưu lịch sử gợi ý</p>

        {error && <div className="auth-error">{error}</div>}

        <form onSubmit={handleSubmit}>
          <label>Tên người dùng</label>
          <input
            type="text" name="username" required
            value={form.username} onChange={handleChange}
            placeholder="nguyenvana"
          />

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
            placeholder="Ít nhất 6 ký tự"
          />

          <label>Xác nhận mật khẩu</label>
          <input
            type="password" name="confirm" required
            value={form.confirm} onChange={handleChange}
            placeholder="Nhập lại mật khẩu"
          />

          <button type="submit" disabled={loading}>
            {loading ? "Đang tạo tài khoản..." : "Đăng ký"}
          </button>
        </form>

        <p className="auth-link">
          Đã có tài khoản? <Link to="/login">Đăng nhập</Link>
        </p>
      </div>
    </div>
  );
}
