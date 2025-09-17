from flask import Blueprint, request, redirect, url_for, flash, render_template
from ..models import Product
from .utils import add_to_cart, remove_from_cart, cart_items, cart_total, clear_cart

bp = Blueprint("cart", __name__, template_folder="../templates/cart")

@bp.route("/")
def detail():
    return render_template("cart/cart.html", items=cart_items(), total=cart_total())

@bp.route("/add", methods=["POST"])
def add():
    product_id = request.form.get("product_id")
    quantity = request.form.get("quantity", "1")
    try:
        product = Product.query.filter_by(id=int(product_id), is_active=True).first()
        if not product:
            flash("Invalid product.", "danger")
            return redirect(request.referrer or url_for("catalog.product_list"))
        qty = max(1, int(quantity))
        if product.stock <= 0:
            flash("This product is out of stock.", "danger")
        else:
            add_to_cart(product.id, qty)
            flash(f"Added {qty} x {product.name} to cart.", "success")
    except Exception:
        flash("Error adding to cart.", "danger")
    return redirect(request.referrer or url_for("catalog.product_list"))

@bp.route("/update", methods=["POST"])
def update():
    # Update quantities: form fields named qty_<product_id>
    for key, val in request.form.items():
        if key.startswith("qty_"):
            pid = key.split("_", 1)[1]
            try:
                qty = int(val)
                add_to_cart(int(pid), qty, update=True)
            except Exception:
                continue
    flash("Cart updated.", "success")
    return redirect(url_for("cart.detail"))

@bp.route("/remove/<int:product_id>")
def remove(product_id):
    remove_from_cart(product_id)
    flash("Item removed from cart.", "info")
    return redirect(url_for("cart.detail"))