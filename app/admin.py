from flask import redirect, url_for, request
from flask_login import current_user
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from .extensions import db
from .models import User, Category, Product, ProductImage, Order, OrderItem

class MyAdminIndex(AdminIndexView):
    @expose("/")
    def index(self):
        if not (current_user.is_authenticated and current_user.is_admin):
            return redirect(url_for("auth.login", next=request.url))
        return super().index()

    def is_visible(self):
        return True

class SecureModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("auth.login", next=request.url))

def init_admin(app):
    admin = Admin(app, name="Shop Admin", template_mode="bootstrap4", index_view=MyAdminIndex())
    admin.add_view(SecureModelView(User, db.session))
    admin.add_view(SecureModelView(Category, db.session))
    admin.add_view(SecureModelView(Product, db.session))
    admin.add_view(SecureModelView(ProductImage, db.session))
    admin.add_view(SecureModelView(Order, db.session))
    admin.add_view(SecureModelView(OrderItem, db.session))