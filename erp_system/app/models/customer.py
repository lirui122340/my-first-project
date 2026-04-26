from datetime import datetime
from app.database import db


class Customer(db.Model):
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    contact = db.Column(db.String(64))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(64))
    address = db.Column(db.String(256))
    credit_limit = db.Column(db.Float, default=0)
    balance = db.Column(db.Float, default=0)
    level = db.Column(db.String(20), default='normal')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sales_orders = db.relationship('SalesOrder', backref='customer', lazy='dynamic')
