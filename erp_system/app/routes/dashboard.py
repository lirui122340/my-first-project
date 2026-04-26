from flask import Blueprint, render_template
from flask_login import login_required
from app.database import db
from app.models.inventory import Product, Stock
from app.models.purchase import PurchaseOrder, Supplier
from app.models.sales import SalesOrder
from app.models.customer import Customer
from app.models.hr import Employee
from app.models.finance import Account
from sqlalchemy import func

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@login_required
def index():
    product_count = Product.query.count()
    supplier_count = Supplier.query.count()
    customer_count = Customer.query.count()
    employee_count = Employee.query.count()

    pending_purchase = PurchaseOrder.query.filter_by(status='pending').count()
    pending_sales = SalesOrder.query.filter_by(status='pending').count()

    total_stock = db.session.query(func.sum(Stock.quantity)).scalar() or 0

    accounts = Account.query.all()
    total_balance = sum(a.balance for a in accounts)

    low_stock_products = Product.query.filter(Product.id.notin_(
        db.session.query(Stock.product_id).filter(Stock.quantity > Product.min_stock)
    )).limit(5).all()

    return render_template('dashboard/index.html',
                           product_count=product_count,
                           supplier_count=supplier_count,
                           customer_count=customer_count,
                           employee_count=employee_count,
                           pending_purchase=pending_purchase,
                           pending_sales=pending_sales,
                           total_stock=total_stock,
                           total_balance=total_balance,
                           low_stock_products=low_stock_products)
