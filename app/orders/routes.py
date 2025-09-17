from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from ..forms import CheckoutForm
from ..extensions import db
from ..models import Order, OrderItem, Product
from ..cart.utils import cart_items, cart_total, clear_cart

bp = Blueprint("orders", __name__, template_folder="../templates/orders")

@bp.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    items = cart_items()
    if not items:
        flash("Your cart is empty.", "warning")
        return redirect(url_for("cart.detail"))

    form = CheckoutForm()
    if form.validate_on_submit():
        try:
            # Create order and items atomically
            order = Order(
                user=current_user,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                email=form.email.data,
                address=form.address.data,
                city=form.city.data,
                postal_code=form.postal_code.data,
                payment_reference=form.payment_reference.data or "",
                status="pending",
            )
            db.session.add(order)
            db.session.flush()  # get order.id

            for it in items:
                product: Product = it["product"]
                qty = int(it["quantity"])
                if product.stock < qty:
                    db.session.rollback()
                    flash(f"Insufficient stock for {product.name}.", "danger")
                    return redirect(url_for("cart.detail"))
                db.session.add(OrderItem(
                    order=order,
                    product=product,
                    price=product.price,
                    quantity=qty
                ))
                product.stock -= qty
                db.session.add(product)

            db.session.commit()
            clear_cart()
            flash(f"Order #{order.id} placed successfully!", "success")
            return redirect(url_for("orders.success", order_id=order.id))
        except Exception:
            db.session.rollback()
            flash("Error placing order. Please try again.", "danger")

    return render_template("orders/checkout.html", items=items, total=cart_total(), form=form)

@bp.route("/success/<int:order_id>")
@login_required
def success(order_id):
    return render_template("orders/success.html", order_id=order_id)