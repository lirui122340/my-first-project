from datetime import datetime
from app.database import db


class ProductionOrder(db.Model):
    __tablename__ = 'production_orders'

    id = db.Column(db.Integer, primary_key=True)
    order_no = db.Column(db.String(32), unique=True, nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    quantity = db.Column(db.Integer, default=0)
    completed_quantity = db.Column(db.Integer, default=0)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='pending')
    remark = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    product = db.relationship('Product', backref='production_orders')


class BillOfMaterial(db.Model):
    __tablename__ = 'bill_of_materials'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    material_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    quantity = db.Column(db.Float, default=1)
    unit = db.Column(db.String(20))
    remark = db.Column(db.String(256))
    product = db.relationship('Product', foreign_keys=[product_id], backref='bom_products')
    material = db.relationship('Product', foreign_keys=[material_id], backref='bom_materials')
