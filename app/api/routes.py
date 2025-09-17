from flask import Blueprint, request, jsonify, current_app
from sqlalchemy import or_
from ..models import Product, Category

bp = Blueprint("api", __name__)

def serialize_product(p: Product):
    return {
        "id": p.id,
        "name": p.name,
        "slug": p.slug,
        "description": p.description,
        "price": float(p.price),
        "stock": p.stock,
        "featured": p.featured,
        "created_at": p.created_at.isoformat(),
        "category": {
            "id": p.category.id,
            "name": p.category.name,
            "slug": p.category.slug,
            "parent_id": p.category.parent_id,
        } if p.category else None,
        "images": [{"id": img.id, "image_url": img.image_url, "alt_text": img.alt_text} for img in p.images],
    }

@bp.get("/products")
def products():
    q = request.args.get("search", "").strip()
    cat = request.args.get("category", "").strip()
    min_price = request.args.get("min_price", "").strip()
    max_price = request.args.get("max_price", "").strip()
    ordering = request.args.get("ordering", "").strip()
    page = max(1, int(request.args.get("page", 1)))
    per_page = min(max(1, int(request.args.get("per_page", current_app.config.get("ITEMS_PER_PAGE", 12)))), 100)

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
        "name": Product.name.asc(),
        "-name": Product.name.desc(),
        "price": Product.price.asc(),
        "-price": Product.price.desc(),
        "created_at": Product.created_at.asc(),
        "-created_at": Product.created_at.desc(),
    }
    if ordering in ordering_map:
        query = query.order_by(ordering_map[ordering])
    else:
        query = query.order_by(Product.created_at.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        "page": page,
        "per_page": per_page,
        "total": pagination.total,
        "products": [serialize_product(p) for p in pagination.items],
    })

@bp.get("/products/<id_or_slug>")
def product_detail(id_or_slug):
    product = None
    if id_or_slug.isdigit():
        product = Product.query.filter_by(id=int(id_or_slug), is_active=True).first()
    if not product:
        product = Product.query.filter_by(slug=id_or_slug, is_active=True).first()
    if not product:
        return jsonify({"error": "Not found"}), 404
    return jsonify(serialize_product(product))