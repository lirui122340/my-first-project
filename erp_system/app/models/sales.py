from datetime import datetime
from app.database import db


class SalesOrder(db.Model):
    __tablename__ = 'sales_orders'

    id = db.Column(db.Integer, primary_key=True)
    order_no = db.Column(db.String(32), unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    total_amount = db.Column(db.Float, default=0)
    status = db.Column(db.String(20), default='pending')
    remark = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship('SalesItem', backref='order', lazy='dynamic', cascade='all, delete-orphan')


class SalesItem(db.Model):
    __tablename__ = 'sales_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('sales_orders.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    quantity = db.Column(db.Integer, default=0)
    unit_price = db.Column(db.Float, default=0)
    total_price = db.Column(db.Float, default=0)
    product = db.relationship('Product', backref='sales_items')
