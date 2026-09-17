"""
Chạy script này để thêm sản phẩm mẫu vào database.
Tên sản phẩm khớp với dataset để thuật toán gợi ý hoạt động đúng.

Cách chạy:
    cd backend
    venv\Scripts\activate
    python products/seed.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from database import db, Product

SAMPLE_PRODUCTS = [
    # ── Sản phẩm gốc ──────────────────────────────────────────────────────────
    {
        "name":        "GREEN REGENCY TEACUP AND SAUCER",
        "description": "Bộ tách trà và đĩa lót thiết kế Regency màu xanh lá sang trọng, gốm cao cấp.",
        "price":       185000,
        "image_url":   "https://picsum.photos/id/30/200/180",
        "category":    "Đồ gia dụng",
        "stock":       50,
    },
    {
        "name":        "PINK REGENCY TEACUP AND SAUCER",
        "description": "Bộ tách trà và đĩa lót thiết kế Regency màu hồng pastel dịu dàng.",
        "price":       185000,
        "image_url":   "https://picsum.photos/id/33/200/180",
        "category":    "Đồ gia dụng",
        "stock":       50,
    },
    {
        "name":        "ROSES REGENCY TEACUP AND SAUCER",
        "description": "Bộ tách trà và đĩa lót họa tiết hoa hồng phong cách Regency cổ điển.",
        "price":       195000,
        "image_url":   "https://picsum.photos/id/36/200/180",
        "category":    "Đồ gia dụng",
        "stock":       45,
    },
    {
        "name":        "ALARM CLOCK BAKELIKE GREEN",
        "description": "Đồng hồ báo thức phong cách retro Bakelite màu xanh lá vintage.",
        "price":       320000,
        "image_url":   "https://picsum.photos/id/39/200/180",
        "category":    "Phụ kiện",
        "stock":       30,
    },
    {
        "name":        "ALARM CLOCK BAKELIKE PINK",
        "description": "Đồng hồ báo thức phong cách retro Bakelite màu hồng dễ thương.",
        "price":       320000,
        "image_url":   "https://picsum.photos/id/42/200/180",
        "category":    "Phụ kiện",
        "stock":       30,
    },
    {
        "name":        "ALARM CLOCK BAKELIKE RED",
        "description": "Đồng hồ báo thức phong cách retro Bakelite màu đỏ nổi bật.",
        "price":       320000,
        "image_url":   "https://picsum.photos/id/45/200/180",
        "category":    "Phụ kiện",
        "stock":       25,
    },
    {
        "name":        "DOLLY GIRL LUNCH BOX",
        "description": "Hộp đựng cơm in hình Dolly Girl ngộ nghĩnh, chất liệu thiếc bền đẹp.",
        "price":       145000,
        "image_url":   "https://picsum.photos/id/48/200/180",
        "category":    "Đồ dùng học sinh",
        "stock":       60,
    },
    {
        "name":        "GARDENERS KNEELING PAD CUP OF TEA",
        "description": "Đệm quỳ gối làm vườn họa tiết tách trà, chống thấm nước.",
        "price":       95000,
        "image_url":   "https://picsum.photos/id/51/200/180",
        "category":    "Làm vườn",
        "stock":       40,
    },
    {
        "name":        "GARDENERS KNEELING PAD KEEP CALM",
        "description": "Đệm quỳ gối làm vườn in chữ Keep Calm, chất liệu foam cao su.",
        "price":       95000,
        "image_url":   "https://picsum.photos/id/54/200/180",
        "category":    "Làm vườn",
        "stock":       40,
    },
    {
        "name":        "SET OF 4 PANTRY JELLY MOULDS",
        "description": "Bộ 4 khuôn thạch/jelly hình pantry vintage, làm từ nhựa an toàn thực phẩm.",
        "price":       125000,
        "image_url":   "https://picsum.photos/id/57/200/180",
        "category":    "Nhà bếp",
        "stock":       35,
    },

    # ── Sản phẩm bán chạy từ dataset lớn (để test thống kê) ──────────────────
    {
        "name":        "PAPER CRAFT , LITTLE BIRDIE",
        "description": "Bộ thủ công giấy hình chim nhỏ xinh, phù hợp trang trí và làm quà.",
        "price":       48000,
        "image_url":   "https://picsum.photos/id/60/200/180",
        "category":    "Thủ công mỹ nghệ",
        "stock":       200,
    },
    {
        "name":        "MEDIUM CERAMIC TOP STORAGE JAR",
        "description": "Hũ đựng đồ gốm sứ nắp đậy kích thước vừa, thiết kế vintage.",
        "price":       28000,
        "image_url":   "https://picsum.photos/id/63/200/180",
        "category":    "Nhà bếp",
        "stock":       150,
    },
    {
        "name":        "WORLD WAR 2 GLIDERS ASSTD DESIGNS",
        "description": "Bộ máy bay lượn thiết kế thời Thế chiến II, nhiều mẫu đa dạng.",
        "price":       67000,
        "image_url":   "https://picsum.photos/id/66/200/180",
        "category":    "Đồ chơi",
        "stock":       120,
    },
    {
        "name":        "JUMBO BAG RED RETROSPOT",
        "description": "Túi vải jumbo họa tiết chấm bi đỏ phong cách retro.",
        "price":       46000,
        "image_url":   "https://picsum.photos/id/69/200/180",
        "category":    "Túi xách",
        "stock":       100,
    },
    {
        "name":        "WHITE HANGING HEART T-LIGHT HOLDER",
        "description": "Đèn tealight treo hình trái tim màu trắng, trang trí lãng mạn.",
        "price":       67000,
        "image_url":   "https://picsum.photos/id/72/200/180",
        "category":    "Trang trí",
        "stock":       80,
    },
    {
        "name":        "ASSORTED COLOUR BIRD ORNAMENT",
        "description": "Đồ trang trí hình chim nhiều màu sắc, phù hợp decor nhà cửa.",
        "price":       39000,
        "image_url":   "https://picsum.photos/id/75/200/180",
        "category":    "Trang trí",
        "stock":       90,
    },
    {
        "name":        "POPCORN HOLDER",
        "description": "Hộp đựng bắp rang bơ xinh xắn, dùng cho tiệc và rạp chiếu phim tại nhà.",
        "price":       19000,
        "image_url":   "https://picsum.photos/id/78/200/180",
        "category":    "Nhà bếp",
        "stock":       200,
    },
    {
        "name":        "RABBIT NIGHT LIGHT",
        "description": "Đèn ngủ hình thỏ dễ thương, ánh sáng dịu nhẹ cho phòng trẻ em.",
        "price":       46000,
        "image_url":   "https://picsum.photos/id/81/200/180",
        "category":    "Trang trí",
        "stock":       75,
    },
    {
        "name":        "MINI PAINT SET VINTAGE",
        "description": "Bộ màu vẽ mini phong cách vintage, thích hợp cho người yêu hội họa.",
        "price":       15000,
        "image_url":   "https://picsum.photos/id/84/200/180",
        "category":    "Thủ công mỹ nghệ",
        "stock":       110,
    },
    {
        "name":        "JUMBO BAG PINK POLKADOT",
        "description": "Túi vải jumbo họa tiết chấm bi hồng, dung tích lớn tiện dụng.",
        "price":       46000,
        "image_url":   "https://picsum.photos/id/87/200/180",
        "category":    "Túi xách",
        "stock":       95,
    },
    {
        "name":        "SMALL POPCORN HOLDER",
        "description": "Hộp đựng bắp rang bơ cỡ nhỏ, tiện lợi cho bữa xem phim.",
        "price":       19000,
        "image_url":   "https://picsum.photos/id/90/200/180",
        "category":    "Nhà bếp",
        "stock":       180,
    },
    {
        "name":        "LUNCH BAG RED RETROSPOT",
        "description": "Túi đựng cơm họa tiết chấm bi đỏ retro, giữ nhiệt tốt.",
        "price":       38000,
        "image_url":   "https://picsum.photos/id/93/200/180",
        "category":    "Đồ dùng học sinh",
        "stock":       85,
    },
    {
        "name":        "JUMBO BAG STRAWBERRY",
        "description": "Túi vải jumbo in hình dâu tây tươi sắc, thích hợp đi chợ.",
        "price":       46000,
        "image_url":   "https://picsum.photos/id/96/200/180",
        "category":    "Túi xách",
        "stock":       70,
    },
    {
        "name":        "VICTORIAN GLASS HANGING T-LIGHT",
        "description": "Đèn tealight treo thủy tinh phong cách Victorian sang trọng.",
        "price":       33000,
        "image_url":   "https://picsum.photos/id/99/200/180",
        "category":    "Trang trí",
        "stock":       60,
    },
    {
        "name":        "RED  HARMONICA IN BOX",
        "description": "Kèn harmonica màu đỏ đựng trong hộp, âm thanh trong trẻo.",
        "price":       29000,
        "image_url":   "https://picsum.photos/id/102/200/180",
        "category":    "Âm nhạc",
        "stock":       55,
    },
    {
        "name":        "BROCADE RING PURSE",
        "description": "Ví nhỏ vải gấm đựng nhẫn và trang sức, thiết kế tinh tế.",
        "price":       74000,
        "image_url":   "https://picsum.photos/id/105/200/180",
        "category":    "Phụ kiện",
        "stock":       65,
    },
]


def seed():
    app = create_app()
    with app.app_context():
        added = 0
        for data in SAMPLE_PRODUCTS:
            if not Product.query.filter_by(name=data["name"]).first():
                p = Product(**data)
                db.session.add(p)
                added += 1
                print(f"  ✅ Thêm: {data['name']}")
            else:
                print(f"  ⏭️  Đã có: {data['name']}")

        db.session.commit()
        print(f"\n🎉 Hoàn thành! Đã thêm {added} sản phẩm mới.")
        print(f"   Tổng sản phẩm trong DB: {Product.query.count()}")


if __name__ == "__main__":
    seed()