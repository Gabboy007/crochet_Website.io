from app import db


class Product(db.Model):
    __tablename__ = "product"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=True)
    rarity = db.Column(db.String(50), nullable=True)
    condition = db.Column(db.String(50), nullable=True)
    sort_order = db.Column(db.Integer, default=0, nullable=False)

    images = db.relationship(
        "ProductImage",
        backref="product",
        cascade="all, delete-orphan",
        lazy=True,
        order_by="ProductImage.sort_order",
    )

    @property
    def main_image(self):
        for image in self.images:
            if image.is_main:
                return image
        return self.images[0] if self.images else None


class ProductImage(db.Model):
    __tablename__ = "product_image"

    id = db.Column(db.Integer, primary_key=True)
    image_path = db.Column(db.String(300), nullable=False)
    is_main = db.Column(db.Boolean, default=False, nullable=False)
    sort_order = db.Column(db.Integer, default=0, nullable=False)

    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)


class Review(db.Model):
    __tablename__ = "review"

    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(120), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    review_text = db.Column(db.Text, nullable=False)
    badge = db.Column(db.String(100), nullable=True)
    score = db.Column(db.String(20), default="\u2605\u2605\u2605\u2605\u2605", nullable=False)
    sort_order = db.Column(db.Integer, default=0, nullable=False)

    images = db.relationship(
        "ReviewImage",
        backref="review",
        cascade="all, delete-orphan",
        lazy=True,
        order_by="ReviewImage.sort_order",
    )

    @property
    def main_image(self):
        for image in self.images:
            if image.is_main:
                return image
        return self.images[0] if self.images else None


class ReviewImage(db.Model):
    __tablename__ = "review_image"

    id = db.Column(db.Integer, primary_key=True)
    image_path = db.Column(db.String(300), nullable=False)
    is_main = db.Column(db.Boolean, default=False, nullable=False)
    sort_order = db.Column(db.Integer, default=0, nullable=False)

    review_id = db.Column(db.Integer, db.ForeignKey("review.id"), nullable=False)
