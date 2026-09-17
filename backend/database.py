from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


def init_db(app=None):
    if app:
        with app.app_context():
            db.create_all()
    else:
        db.create_all()
    print("✅ [Database] Khởi tạo cấu trúc các bảng thành công!")


class User(db.Model):
    __tablename__ = "users"
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(80), unique=True, nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    address       = db.Column(db.Text, nullable=True, default="") # Giữ lại 1 cột duy nhất ở đây
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Các mối quan hệ relationships
    cart_history  = db.relationship("CartHistory", backref="user", lazy=True, cascade="all, delete")
    favorites     = db.relationship("Favorite", backref="user", lazy=True, cascade="all, delete")
    viewed        = db.relationship("ViewedRecommendation", backref="user", lazy=True, cascade="all, delete")
    orders        = db.relationship("Order", backref="user", lazy=True, cascade="all, delete")

    def to_dict(self):
        return {
            "id": self.id, 
            "username": self.username, 
            "email": self.email, 
            "address": self.address or "", 
            "created_at": self.created_at.isoformat()
        }

class Product(db.Model):
    __tablename__ = "products"
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(200), unique=True, nullable=False)
    description = db.Column(db.Text, default="")
    price       = db.Column(db.Float, nullable=False, default=0.0)
    image_url   = db.Column(db.String(500), default="")
    category    = db.Column(db.String(100), default="")
    stock       = db.Column(db.Integer, default=100)
    is_active   = db.Column(db.Boolean, default=True)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    order_items = db.relationship("OrderItem", backref="product", lazy=True)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "description": self.description,
                "price": self.price, "image_url": self.image_url, "category": self.category,
                "stock": self.stock, "is_active": self.is_active}


class Order(db.Model):
    __tablename__ = "orders"
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    total      = db.Column(db.Float, nullable=False, default=0.0)
    status     = db.Column(db.String(20), default="pending")
    address    = db.Column(db.Text, default="")
    note       = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    items      = db.relationship("OrderItem", backref="order", lazy=True, cascade="all, delete")

    def to_dict(self):
        return {"id": self.id, "user_id": self.user_id, "total": self.total,
                "status": self.status, "address": self.address, "note": self.note,
                "created_at": self.created_at.isoformat(), "items": [i.to_dict() for i in self.items]}


class OrderItem(db.Model):
    __tablename__ = "order_items"
    id         = db.Column(db.Integer, primary_key=True)
    order_id   = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity   = db.Column(db.Integer, nullable=False, default=1)
    price      = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {"id": self.id, "product_id": self.product_id,
                "product_name": self.product.name if self.product else "",
                "product_image": self.product.image_url if self.product else "",
                "quantity": self.quantity, "price": self.price,
                "subtotal": round(self.quantity * self.price, 2)}


class CartHistory(db.Model):
    __tablename__ = "cart_history"
    id              = db.Column(db.Integer, primary_key=True)
    user_id         = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    cart_items      = db.Column(db.Text, nullable=False)
    recommendations = db.Column(db.Text, nullable=True)
    algorithm       = db.Column(db.String(20), default="fpgrowth")
    searched_at     = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        import json
        return {"id": self.id, "cart_items": json.loads(self.cart_items),
                "recommendations": json.loads(self.recommendations) if self.recommendations else [],
                "algorithm": self.algorithm, "searched_at": self.searched_at.isoformat()}


class Favorite(db.Model):
    __tablename__ = "favorites"
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    product_id = db.Column(db.String(100), nullable=False)
    added_at   = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint("user_id", "product_id"),)

    def to_dict(self):
        return {"id": self.id, "product_id": self.product_id, "added_at": self.added_at.isoformat()}


class ViewedRecommendation(db.Model):
    __tablename__ = "viewed_recommendations"
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    product_id = db.Column(db.String(100), nullable=False)
    algorithm  = db.Column(db.String(20))
    viewed_at  = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {"id": self.id, "product_id": self.product_id,
                "algorithm": self.algorithm, "viewed_at": self.viewed_at.isoformat()}