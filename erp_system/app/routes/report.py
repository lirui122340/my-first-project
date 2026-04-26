from flask import Blueprint, render_template
from flask_login import login_required
from app.database import db
from app.models.inventory import Product, Stock
from app.models.purchase import PurchaseOrder
from app.models.sales import SalesOrder
from app.models.finance import Account, Transaction
from app.models.customer import Customer
from app.models.hr import Employee
from sqlalchemy import func
from datetime import datetime, timedelta

report_bp = Blueprint('report', __name__)


@report_bp.route('/')
@login_required
def index():
    return render_template('report/index.html')


@report_bp.route('/inventory')
@login_required
def inventory():
    products = Product.query.all()
    stock_data = []
    for p in products:
        total_stock = db.session.query(func.sum(Stock.quantity)).filter(
            Stock.product_id == p.id
        ).scalar() or 0
        stock_data.append({
            'product': p,
            'stock': total_stock,
            'value': total_stock * p.purchase_price,
            'status': '低库存' if total_stock < p.min_stock else '正常'
        })
    return render_template('report/inventory.html', stock_data=stock_data)


@report_bp.route('/sales')
@login_required
def sales():
    today = datetime.now().date()
    month_start = today.replace(day=1)

    daily_sales = db.session.query(
        func.date(SalesOrder.order_date).label('date'),
        func.sum(SalesOrder.total_amount).label('total')
    ).filter(
        SalesOrder.status == 'completed',
        SalesOrder.order_date >= month_start
    ).group_by(func.date(SalesOrder.order_date)).all()

    top_customers = db.session.query(
        Customer.name,
        func.sum(SalesOrder.total_amount).label('total')
    ).join(SalesOrder).filter(
        SalesOrder.status == 'completed'
    ).group_by(Customer.id).order_by(func.sum(SalesOrder.total_amount).desc()).limit(10).all()

    return render_template('report/sales.html', daily_sales=daily_sales, top_customers=top_customers)


@report_bp.route('/purchase')
@login_required
def purchase():
    month_start = datetime.now().date().replace(day=1)

    monthly_purchase = db.session.query(
        func.sum(PurchaseOrder.total_amount).label('total')
    ).filter(
        PurchaseOrder.status == 'completed',
        PurchaseOrder.order_date >= month_start
    ).scalar() or 0

    supplier_stats = db.session.query(
        PurchaseOrder.supplier_id,
        func.count(PurchaseOrder.id).label('order_count'),
        func.sum(PurchaseOrder.total_amount).label('total')
    ).filter(
        PurchaseOrder.status == 'completed'
    ).group_by(PurchaseOrder.supplier_id).all()

    return render_template('report/purchase.html',
                           monthly_purchase=monthly_purchase,
                           supplier_stats=supplier_stats)


@report_bp.route('/finance')
@login_required
def finance():
    accounts = Account.query.all()
    total_balance = sum(a.balance for a in accounts)

    month_start = datetime.now().date().replace(day=1)

    income = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.transaction_type == 'income',
        Transaction.transaction_date >= month_start
    ).scalar() or 0

    expense = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.transaction_type == 'expense',
        Transaction.transaction_date >= month_start
    ).scalar() or 0

    return render_template('report/finance.html',
                           total_balance=total_balance,
                           income=income,
                           expense=expense,
                           profit=income - expense)
