import { useState } from "react";
import { Link } from "react-router-dom";
import api from "../services/api";

export default function ForgotPasswordPage() {
  const [step,        setStep]        = useState(1); // 1: nhập email, 2: nhập OTP + mật khẩu mới
  const [email,       setEmail]       = useState("");
  const [otp,         setOtp]         = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirm,     setConfirm]     = useState("");
  const [message,     setMessage]     = useState("");
  const [error,       setError]       = useState("");
  const [loading,     setLoading]     = useState(false);

  // ── Step 1: Gửi OTP ────────────────────────────────────────────────────────
  const handleSendOtp = async () => {
    if (!email) { setError("Vui lòng nhập email."); return; }
    setError(""); setLoading(true);
    try {
      const res = await api.post("/auth/forgot-password", { email });
      setMessage(res.data.message);
      setStep(2);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // ── Step 2: Xác nhận OTP + đổi mật khẩu ───────────────────────────────────
  const handleResetPassword = async () => {
    if (!otp || !newPassword || !confirm) { setError("Vui lòng điền đầy đủ."); return; }
    if (newPassword !== confirm) { setError("Mật khẩu xác nhận không khớp."); return; }
    if (newPassword.length < 6)  { setError("Mật khẩu ít nhất 6 ký tự."); return; }
    setError(""); setLoading(true);
    try {
      const res = await api.post("/auth/reset-password", { email, otp, new_password: newPassword });
      setMessage(res.data.message);
      setStep(3);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-wrapper">
      <div className="auth-card">

        {/* Step 1 — Nhập email */}
        {step === 1 && (
          <>
            <h1>Quên mật khẩu</h1>
            <p className="auth-sub">Nhập email để nhận mã OTP</p>
            {error   && <div className="auth-error">{error}</div>}
            <div style={{display:"flex",flexDirection:"column",gap:12}}>
              <label>Email</label>
              <input
                type="email" value={email} placeholder="example@gmail.com"
                onChange={e => setEmail(e.target.value)}
              />
              <button
                onClick={handleSendOtp} disabled={loading}
                style={{background:"#4f46e5",color:"#fff",border:"none",borderRadius:8,
                        padding:"12px",fontSize:"1rem",cursor:"pointer",fontWeight:600,marginTop:8}}
              >
                {loading ? "Đang gửi..." : "Gửi mã OTP"}
              </button>
            </div>
          </>
        )}

        {/* Step 2 — Nhập OTP + mật khẩu mới */}
        {step === 2 && (
          <>
            <h1>Xác nhận OTP</h1>
            <p className="auth-sub" style={{color:"#16a34a"}}>{message}</p>
            {error && <div className="auth-error">{error}</div>}
            <div style={{display:"flex",flexDirection:"column",gap:12}}>
              <label>Mã OTP (6 số)</label>
              <input
                type="text" value={otp} placeholder="123456" maxLength={6}
                onChange={e => setOtp(e.target.value)}
                style={{letterSpacing:6, fontSize:"1.2rem", textAlign:"center"}}
              />
              <label>Mật khẩu mới</label>
              <input
                type="password" value={newPassword} placeholder="Ít nhất 6 ký tự"
                onChange={e => setNewPassword(e.target.value)}
              />
              <label>Xác nhận mật khẩu</label>
              <input
                type="password" value={confirm} placeholder="Nhập lại mật khẩu"
                onChange={e => setConfirm(e.target.value)}
              />
              <button
                onClick={handleResetPassword} disabled={loading}
                style={{background:"#4f46e5",color:"#fff",border:"none",borderRadius:8,
                        padding:"12px",fontSize:"1rem",cursor:"pointer",fontWeight:600,marginTop:8}}
              >
                {loading ? "Đang xử lý..." : "Đổi mật khẩu"}
              </button>
              <button
                onClick={() => { setStep(1); setError(""); setOtp(""); }}
                style={{background:"none",border:"1px solid #e5e7eb",borderRadius:8,
                        padding:"10px",cursor:"pointer",fontSize:"0.875rem",color:"#555"}}
              >
                Gửi lại OTP
              </button>
            </div>
          </>
        )}

        {/* Step 3 — Thành công */}
        {step === 3 && (
          <>
            <div style={{textAlign:"center",padding:"20px 0"}}>
              <div style={{fontSize:"3rem",marginBottom:12}}>✅</div>
              <h1 style={{marginBottom:8}}>Thành công!</h1>
              <p style={{color:"#555",marginBottom:24}}>{message}</p>
              <Link
                to="/login"
                style={{background:"#4f46e5",color:"#fff",borderRadius:8,
                        padding:"12px 32px",textDecoration:"none",fontWeight:600}}
              >
                Đăng nhập ngay
              </Link>
            </div>
          </>
        )}

        {step !== 3 && (
          <p className="auth-link" style={{marginTop:20}}>
            <Link to="/login">← Quay lại đăng nhập</Link>
          </p>
        )}
      </div>
    </div>
  );
}
