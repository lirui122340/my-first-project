from datetime import datetime
from app.database import db


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.String(256))
    products = db.relationship('Product', backref='category', lazy='dynamic')


class Warehouse(db.Model):
    __tablename__ = 'warehouses'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    location = db.Column(db.String(128))
    capacity = db.Column(db.Integer, default=0)
    stocks = db.relationship('Stock', backref='warehouse', lazy='dynamic')


class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(32), unique=True, nullable=False)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    unit = db.Column(db.String(20), default='件')
    purchase_price = db.Column(db.Float, default=0)
    sale_price = db.Column(db.Float, default=0)
    min_stock = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    stocks = db.relationship('Stock', backref='product', lazy='dynamic')


class Stock(db.Model):
    __tablename__ = 'stocks'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'))
    quantity = db.Column(db.Integer, default=0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
