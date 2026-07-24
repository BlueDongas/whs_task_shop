from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from . import db


def utcnow():
    return datetime.now(timezone.utc)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)

    products = db.relationship(
        "Product",
        back_populates="seller",
        cascade="all, delete-orphan",
        lazy=True,
    )
    purchase_requests = db.relationship(
        "PurchaseRequest",
        back_populates="buyer",
        cascade="all, delete-orphan",
        lazy=True,
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Product(db.Model):
    STATUS_SELLING = "SELLING"
    STATUS_SOLD = "SOLD"
    VALID_STATUSES = {STATUS_SELLING, STATUS_SOLD}

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default=STATUS_SELLING, nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)

    seller = db.relationship("User", back_populates="products")
    purchase_requests = db.relationship(
        "PurchaseRequest",
        back_populates="product",
        cascade="all, delete-orphan",
        lazy=True,
    )


class PurchaseRequest(db.Model):
    STATUS_PENDING = "PENDING"
    STATUS_ACCEPTED = "ACCEPTED"
    STATUS_REJECTED = "REJECTED"
    VALID_STATUSES = {STATUS_PENDING, STATUS_ACCEPTED, STATUS_REJECTED}

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False, index=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    status = db.Column(db.String(20), default=STATUS_PENDING, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)

    product = db.relationship("Product", back_populates="purchase_requests")
    buyer = db.relationship("User", back_populates="purchase_requests")

    __table_args__ = (
        db.UniqueConstraint("product_id", "buyer_id", name="uq_product_buyer"),
    )
