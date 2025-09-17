from decimal import Decimal
from flask import session
from ..models import Product
from ..extensions import db

CART_KEY = "cart"

def _ensure_cart():
    if CART_KEY not in session:
        session[CART_KEY] = {}
    return session[CART_KEY]

def add_to_cart(product_id: int, quantity: int, update=False):
    cart = _ensure_cart()
    pid = str(product_id)
    if pid not in cart:
        cart[pid] = {"quantity": 0}
    if update:
        cart[pid]["quantity"] = max(1, int(quantity))
    else:
        cart[pid]["quantity"] += max(1, int(quantity))
    session.modified = True

def remove_from_cart(product_id: int):
    cart = _ensure_cart()
    pid = str(product_id)
    if pid in cart:
        del cart[pid]
    session.modified = True

def clear_cart():
    session[CART_KEY] = {}
    session.modified = True

def cart_items():
    cart = _ensure_cart()
    ids = [int(pid) for pid in cart.keys()]
    if not ids:
        return []
    products = Product.query.filter(Product.id.in_(ids)).all()
    items = []
    for p in products:
        qty = int(cart[str(p.id)]["quantity"])
        items.append({
            "product": p,
            "quantity": qty,
            "price": Decimal(p.price),
            "total_price": Decimal(p.price) * qty,
        })
    return items

def cart_total():
    total = Decimal("0.00")
    for item in cart_items():
        total += item["total_price"]
    return total

def cart_len():
    cart = _ensure_cart()
    return sum(int(v["quantity"]) for v in cart.values())