from flask import Flask
from .extensions import db, migrate, login_manager
from .admin import init_admin
from .models import User
from .cart.utils import cart_len

def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    # Init extensions
    db.init_app(app)
    migrate.init_app(app, db)

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "warning"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Blueprints
    from .auth.routes import bp as auth_bp
    from .catalog.routes import bp as catalog_bp
    from .cart.routes import bp as cart_bp
    from .orders.routes import bp as orders_bp
    from .api.routes import bp as api_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(catalog_bp)
    app.register_blueprint(cart_bp, url_prefix="/cart")
    app.register_blueprint(orders_bp, url_prefix="/orders")
    app.register_blueprint(api_bp, url_prefix="/api")

    # Admin
    init_admin(app)

    # Template context: cart length
    @app.context_processor
    def inject_globals():
        return {"cart_count": cart_len()}

    return app