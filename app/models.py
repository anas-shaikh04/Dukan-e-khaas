from datetime import datetime
from sqlalchemy import event
from werkzeug.security import generate_password_hash, check_password_hash
from slugify import slugify
from .extensions import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True, nullable=False)
    slug = db.Column(db.String(220), unique=True, index=True, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey("category.id"))
    parent = db.relationship("Category", remote_side=[id], backref="children")

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False)
    category = db.relationship("Category", backref="products")
    name = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(280), unique=True, index=True, nullable=False)
    description = db.Column(db.Text, default="")
    price = db.Column(db.Numeric(10, 2), nullable=False)
    stock = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    featured = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ProductImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    product = db.relationship("Product", backref="images")
    image_url = db.Column(db.String(500), nullable=False)
    alt_text = db.Column(db.String(255), default="")

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = db.relationship("User", backref="orders")
    first_name = db.Column(db.String(120), nullable=False)
    last_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    postal_code = db.Column(db.String(20), nullable=False)
    payment_reference = db.Column(db.String(120), default="")
    status = db.Column(db.String(20), default="pending")  # pending, processing, shipped, delivered, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def total_cost(self):
        return sum(item.price * item.quantity for item in self.items)

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=False)
    order = db.relationship("Order", backref="items")
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    product = db.relationship("Product")
    price = db.Column(db.Numeric(10, 2), nullable=False)
    quantity = db.Column(db.Integer, default=1)

# Helpers to auto-generate slugs
def _unique_slug(model, base):
    base = slugify(base)
    slug = base or "item"
    i = 1
    with db.session.no_autoflush:
        while db.session.query(model).filter_by(slug=slug).first():
            i += 1
            slug = f"{base}-{i}"
    return slug

@event.listens_for(Category, "before_insert")
def cat_before_insert(mapper, connection, target):
    if not target.slug:
        target.slug = _unique_slug(Category, target.name)

@event.listens_for(Product, "before_insert")
def prod_before_insert(mapper, connection, target):
    if not target.slug:
        target.slug = _unique_slug(Product, target.name)