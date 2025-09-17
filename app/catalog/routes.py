from flask import Blueprint, render_template, request
from sqlalchemy import or_
from ..extensions import db
from ..models import Product, Category

bp = Blueprint("catalog", __name__, template_folder="../templates")

@bp.route("/")
def home():
    featured = Product.query.filter_by(is_active=True, featured=True).order_by(Product.created_at.desc()).limit(8).all()
    categories = Category.query.order_by(Category.name.asc()).all()
    return render_template("home.html", featured_products=featured, categories=categories)

@bp.route("/products")
def product_list():
    q = request.args.get("q", "").strip()
    cat = request.args.get("category", "").strip()
    min_price = request.args.get("min_price", "").strip()
    max_price = request.args.get("max_price", "").strip()
    sort = request.args.get("sort", "").strip()
    page = max(1, int(request.args.get("page", 1)))

    query = Product.query.filter_by(is_active=True).join(Category)
    if q:
        like = f"%{q}%"
        query = query.filter(or_(Product.name.ilike(like), Product.description.ilike(like)))
    if cat:
        query = query.filter(Category.slug == cat)
    if min_price:
        try:
            query = query.filter(Product.price >= float(min_price))
        except ValueError:
            pass
    if max_price:
        try:
            query = query.filter(Product.price <= float(max_price))
        except ValueError:
            pass

    ordering_map = {
        "price_asc": Product.price.asc(),
        "price_desc": Product.price.desc(),
        "name_asc": Product.name.asc(),
        "name_desc": Product.name.desc(),
        "newest": Product.created_at.desc(),
        "oldest": Product.created_at.asc(),
    }
    if sort in ordering_map:
        query = query.order_by(ordering_map[sort])
    else:
        query = query.order_by(Product.created_at.desc())

    per_page = int(request.args.get("per_page", 12))
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    categories = Category.query.order_by(Category.name.asc()).all()
    return render_template(
        "catalog/product_list.html",
        products=pagination.items,
        pagination=pagination,
        categories=categories,
        current_filters={"q": q, "category": cat, "min_price": min_price, "max_price": max_price, "sort": sort},
    )

@bp.route("/products/<slug>")
def product_detail(slug):
    product = Product.query.filter_by(slug=slug, is_active=True).first_or_404()
    return render_template("catalog/product_detail.html", product=product)