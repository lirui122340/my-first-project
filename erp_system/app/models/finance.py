from datetime import datetime
from app.database import db


class Account(db.Model):
    __tablename__ = 'accounts'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    account_type = db.Column(db.String(20))
    balance = db.Column(db.Float, default=0)
    bank_name = db.Column(db.String(64))
    account_number = db.Column(db.String(32))
    is_active = db.Column(db.Boolean, default=True)
    transactions = db.relationship('Transaction', backref='account', lazy='dynamic')


class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'))
    transaction_type = db.Column(db.String(20))
    amount = db.Column(db.Float, default=0)
    balance_after = db.Column(db.Float, default=0)
    description = db.Column(db.String(256))
    reference_no = db.Column(db.String(32))
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Invoice(db.Model):
    __tablename__ = 'invoices'

    id = db.Column(db.Integer, primary_key=True)
    invoice_no = db.Column(db.String(32), unique=True, nullable=False)
    order_type = db.Column(db.String(20))
    order_id = db.Column(db.Integer)
    amount = db.Column(db.Float, default=0)
    status = db.Column(db.String(20), default='unpaid')
    invoice_date = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime)
    paid_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
