from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import os

from database import db, init_db
from config import Config
from auth.routes import auth_bp
from auth.reset import reset_bp
from user.routes import user_bp
from api.recommend import recommend_bp
from api.compare import compare_bp
from api.stats import stats_bp
from products.routes import products_bp
from orders.routes import orders_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, resources={r"/*": {"origins": ["http://localhost:3000", "http://localhost:5173"]}},
         supports_credentials=True)
    
    JWTManager(app)
    db.init_app(app)

    # Đảm bảo import model nằm đúng trong app_context chuẩn để tạo bảng không lỗi
    with app.app_context():
        from database import User, Product, CartHistory, Favorite, ViewedRecommendation, Order, OrderItem
        
        # ─── CHÈN ĐOẠN CÓ ĐỂ VÁ DATABASE VÀO ĐÂY ──────────────────────────────
        try:
            # Kiểm tra xem cột address đã thực sự tồn tại trong file SQLite chưa
            result = db.session.execute(db.text("PRAGMA table_info(users);")).fetchall()
            columns = [row[1] for row in result]
            
            if "address" not in columns:
                # Nếu chưa có, ép SQLite thực thi thêm cột 'address' vào bảng users ngay lập tức
                db.session.execute(db.text("ALTER TABLE users ADD COLUMN address TEXT DEFAULT '';"))
                db.session.commit()
                print("⚠️ [Database] Đã vá thành công cột 'address' vào bảng users trên đĩa cứng!")
        except Exception as e:
            print(f"Không thể vá database: {e}")
        init_db(app)

    # Đăng ký các Blueprint (Đã loại bỏ đoạn trùng lặp luồng)
    app.register_blueprint(auth_bp,      url_prefix="/auth")
    app.register_blueprint(reset_bp,     url_prefix="/auth")
    app.register_blueprint(user_bp,      url_prefix="/user")
    app.register_blueprint(recommend_bp, url_prefix="/api")
    app.register_blueprint(compare_bp,   url_prefix="/api")
    app.register_blueprint(stats_bp,     url_prefix="/api")
    app.register_blueprint(products_bp,  url_prefix="/api")
    app.register_blueprint(orders_bp,    url_prefix="/api")

    # Serve uploaded images
    @app.route("/uploads/<filename>")
    def uploaded_file(filename):
        upload_dir = os.path.join(app.root_path, "uploads")
        return send_from_directory(upload_dir, filename)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)