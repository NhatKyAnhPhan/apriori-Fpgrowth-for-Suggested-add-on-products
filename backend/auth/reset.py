import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

from flask import Blueprint, request, jsonify
import bcrypt

from database import db, User

reset_bp = Blueprint("reset", __name__)

# ─── Lưu OTP tạm trong memory (dùng được cho demo/đồ án) ─────────────────────
# Key: email, Value: {otp, expires_at}
otp_store = {}

# ─── Cấu hình Gmail ───────────────────────────────────────────────────────────
GMAIL_ADDRESS  = "aphan1499@gmail.com"   # ← thay bằng Gmail của bạn
GMAIL_APP_PASS = "eway jswx idia tuif"    # ← App Password vừa tạo


def send_otp_email(to_email: str, otp: str) -> bool:
    """Gửi OTP qua Gmail SMTP."""
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "🔐 Mã xác nhận đặt lại mật khẩu"
        msg["From"]    = GMAIL_ADDRESS
        msg["To"]      = to_email

        html = f"""
        <div style="font-family:sans-serif;max-width:480px;margin:0 auto;padding:32px;
                    border:1px solid #e5e7eb;border-radius:12px;">
          <h2 style="color:#4f46e5;">Đặt lại mật khẩu</h2>
          <p>Mã OTP của bạn là:</p>
          <div style="font-size:2rem;font-weight:700;letter-spacing:8px;
                      color:#4f46e5;margin:20px 0;">{otp}</div>
          <p style="color:#888;font-size:0.875rem;">
            Mã có hiệu lực trong <strong>5 phút</strong>.<br>
            Nếu bạn không yêu cầu đặt lại mật khẩu, hãy bỏ qua email này.
          </p>
        </div>
        """
        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_ADDRESS, GMAIL_APP_PASS)
            server.sendmail(GMAIL_ADDRESS, to_email, msg.as_string())
        return True
    except Exception as e:
        print(f"❌ Lỗi gửi email: {e}")
        return False


# ─── Step 1: Yêu cầu OTP ─────────────────────────────────────────────────────

@reset_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    email = request.get_json().get("email", "").strip().lower()
    if not email:
        return jsonify({"error": "Vui lòng nhập email."}), 400

    user = User.query.filter_by(email=email).first()
    # Không tiết lộ email có tồn tại hay không (bảo mật)
    if not user:
        return jsonify({"message": "Nếu email tồn tại, mã OTP đã được gửi."}), 200

    # Tạo OTP 6 số
    otp = "".join(random.choices(string.digits, k=6))
    otp_store[email] = {
        "otp":        otp,
        "expires_at": datetime.utcnow() + timedelta(minutes=5),
    }

    success = send_otp_email(email, otp)
    if not success:
        return jsonify({"error": "Không thể gửi email. Vui lòng thử lại."}), 500

    return jsonify({"message": "Mã OTP đã được gửi đến email của bạn."}), 200


# ─── Step 2: Verify OTP + đổi mật khẩu ──────────────────────────────────────

@reset_bp.route("/reset-password", methods=["POST"])
def reset_password():
    data         = request.get_json()
    email        = data.get("email", "").strip().lower()
    otp          = data.get("otp", "").strip()
    new_password = data.get("new_password", "")

    if not email or not otp or not new_password:
        return jsonify({"error": "Vui lòng điền đầy đủ thông tin."}), 400

    if len(new_password) < 6:
        return jsonify({"error": "Mật khẩu mới ít nhất 6 ký tự."}), 400

    # Kiểm tra OTP
    record = otp_store.get(email)
    if not record:
        return jsonify({"error": "Mã OTP không hợp lệ hoặc đã hết hạn."}), 400

    if datetime.utcnow() > record["expires_at"]:
        del otp_store[email]
        return jsonify({"error": "Mã OTP đã hết hạn. Vui lòng yêu cầu lại."}), 400

    if record["otp"] != otp:
        return jsonify({"error": "Mã OTP không đúng."}), 400

    # Đổi mật khẩu
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "Không tìm thấy tài khoản."}), 404

    user.password_hash = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
    db.session.commit()

    # Xóa OTP đã dùng
    del otp_store[email]

    return jsonify({"message": "Đổi mật khẩu thành công! Vui lòng đăng nhập lại."}), 200
