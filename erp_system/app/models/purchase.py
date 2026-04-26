from datetime import datetime
from app.database import db


class Supplier(db.Model):
    __tablename__ = 'suppliers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    contact = db.Column(db.String(64))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(64))
    address = db.Column(db.String(256))
    is_active = db.Column(db.Boolean, default=True)
    purchase_orders = db.relationship('PurchaseOrder', backref='supplier', lazy='dynamic')


class PurchaseOrder(db.Model):
    __tablename__ = 'purchase_orders'

    id = db.Column(db.Integer, primary_key=True)
    order_no = db.Column(db.String(32), unique=True, nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'))
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    total_amount = db.Column(db.Float, default=0)
    status = db.Column(db.String(20), default='pending')
    remark = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship('PurchaseItem', backref='order', lazy='dynamic', cascade='all, delete-orphan')


class PurchaseItem(db.Model):
    __tablename__ = 'purchase_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('purchase_orders.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    quantity = db.Column(db.Integer, default=0)
    unit_price = db.Column(db.Float, default=0)
    total_price = db.Column(db.Float, default=0)
    product = db.relationship('Product', backref='purchase_items')
