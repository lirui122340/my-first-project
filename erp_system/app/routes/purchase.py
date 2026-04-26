from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required
from datetime import datetime
from app.database import db
from app.models.purchase import Supplier, PurchaseOrder, PurchaseItem
from app.models.inventory import Product, Stock, Warehouse
from wtforms import StringField, TextAreaField, FloatField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm

purchase_bp = Blueprint('purchase', __name__)


class SupplierForm(FlaskForm):
    name = StringField('供应商名称', validators=[DataRequired()])
    contact = StringField('联系人')
    phone = StringField('电话')
    email = StringField('邮箱')
    address = StringField('地址')
    submit = SubmitField('保存')


class PurchaseOrderForm(FlaskForm):
    supplier_id = SelectField('供应商', coerce=int, validators=[DataRequired()])
    remark = TextAreaField('备注')
    submit = SubmitField('保存')


@purchase_bp.route('/')
@login_required
def index():
    orders = PurchaseOrder.query.order_by(PurchaseOrder.created_at.desc()).all()
    return render_template('purchase/index.html', orders=orders)


@purchase_bp.route('/supplier')
@login_required
def suppliers():
    suppliers = Supplier.query.all()
    return render_template('purchase/suppliers.html', suppliers=suppliers)


@purchase_bp.route('/supplier/add', methods=['GET', 'POST'])
@login_required
def add_supplier():
    form = SupplierForm()
    if form.validate_on_submit():
        supplier = Supplier(
            name=form.name.data,
            contact=form.contact.data,
            phone=form.phone.data,
            email=form.email.data,
            address=form.address.data
        )
        db.session.add(supplier)
        db.session.commit()
        flash('供应商添加成功', 'success')
        return redirect(url_for('purchase.suppliers'))
    return render_template('purchase/supplier_form.html', form=form)


@purchase_bp.route('/order/add', methods=['GET', 'POST'])
@login_required
def add_order():
    form = PurchaseOrderForm()
    form.supplier_id.choices = [(s.id, s.name) for s in Supplier.query.filter_by(is_active=True)]
    if form.validate_on_submit():
        order = PurchaseOrder(
            order_no=f'PO{datetime.now().strftime("%Y%m%d%H%M%S")}',
            supplier_id=form.supplier_id.data,
            remark=form.remark.data
        )
        db.session.add(order)
        db.session.commit()
        flash('采购订单创建成功', 'success')
        return redirect(url_for('purchase.order_detail', id=order.id))
    return render_template('purchase/order_form.html', form=form)


@purchase_bp.route('/order/<int:id>')
@login_required
def order_detail(id):
    order = PurchaseOrder.query.get_or_404(id)
    products = Product.query.filter_by(is_active=True).all()
    return render_template('purchase/order_detail.html', order=order, products=products)


@purchase_bp.route('/order/<int:order_id>/add_item', methods=['POST'])
@login_required
def add_item(order_id):
    order = PurchaseOrder.query.get_or_404(order_id)
    product_id = request.form.get('product_id', type=int)
    quantity = request.form.get('quantity', type=int)
    unit_price = request.form.get('unit_price', type=float)

    product = Product.query.get_or_404(product_id)
    item = PurchaseItem(
        order_id=order_id,
        product_id=product_id,
        quantity=quantity,
        unit_price=unit_price,
        total_price=quantity * unit_price
    )
    db.session.add(item)
    order.total_amount += item.total_price
    db.session.commit()
    flash('商品添加成功', 'success')
    return redirect(url_for('purchase.order_detail', id=order_id))


@purchase_bp.route('/order/<int:order_id>/confirm')
@login_required
def confirm_order(order_id):
    order = PurchaseOrder.query.get_or_404(order_id)
    if order.status != 'pending':
        flash('订单状态不正确', 'danger')
        return redirect(url_for('purchase.order_detail', id=order_id))

    warehouse = Warehouse.query.first()
    for item in order.items:
        stock = Stock.query.filter_by(product_id=item.product_id, warehouse_id=warehouse.id).first()
        if stock:
            stock.quantity += item.quantity
        else:
            stock = Stock(product_id=item.product_id, warehouse_id=warehouse.id, quantity=item.quantity)
            db.session.add(stock)

    order.status = 'completed'
    db.session.commit()
    flash('采购订单已确认，库存已更新', 'success')
    return redirect(url_for('purchase.order_detail', id=order_id))
