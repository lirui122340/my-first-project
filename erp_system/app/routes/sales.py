from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required
from datetime import datetime
from app.database import db
from app.models.sales import SalesOrder, SalesItem
from app.models.customer import Customer
from app.models.inventory import Product, Stock
from wtforms import TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm

sales_bp = Blueprint('sales', __name__)


class SalesOrderForm(FlaskForm):
    customer_id = SelectField('客户', coerce=int, validators=[DataRequired()])
    remark = TextAreaField('备注')
    submit = SubmitField('保存')


@sales_bp.route('/')
@login_required
def index():
    orders = SalesOrder.query.order_by(SalesOrder.created_at.desc()).all()
    return render_template('sales/index.html', orders=orders)


@sales_bp.route('/order/add', methods=['GET', 'POST'])
@login_required
def add_order():
    form = SalesOrderForm()
    form.customer_id.choices = [(c.id, c.name) for c in Customer.query.filter_by(is_active=True)]
    if form.validate_on_submit():
        order = SalesOrder(
            order_no=f'SO{datetime.now().strftime("%Y%m%d%H%M%S")}',
            customer_id=form.customer_id.data,
            remark=form.remark.data
        )
        db.session.add(order)
        db.session.commit()
        flash('销售订单创建成功', 'success')
        return redirect(url_for('sales.order_detail', id=order.id))
    return render_template('sales/order_form.html', form=form)


@sales_bp.route('/order/<int:id>')
@login_required
def order_detail(id):
    order = SalesOrder.query.get_or_404(id)
    products = Product.query.filter_by(is_active=True).all()
    return render_template('sales/order_detail.html', order=order, products=products)


@sales_bp.route('/order/<int:order_id>/add_item', methods=['POST'])
@login_required
def add_item(order_id):
    order = SalesOrder.query.get_or_404(order_id)
    product_id = request.form.get('product_id', type=int)
    quantity = request.form.get('quantity', type=int)
    unit_price = request.form.get('unit_price', type=float)

    item = SalesItem(
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
    return redirect(url_for('sales.order_detail', id=order_id))


@sales_bp.route('/order/<int:order_id>/confirm')
@login_required
def confirm_order(order_id):
    order = SalesOrder.query.get_or_404(order_id)
    if order.status != 'pending':
        flash('订单状态不正确', 'danger')
        return redirect(url_for('sales.order_detail', id=order_id))

    for item in order.items:
        stock = Stock.query.filter_by(product_id=item.product_id).first()
        if stock and stock.quantity >= item.quantity:
            stock.quantity -= item.quantity
        else:
            flash(f'商品 {item.product.name} 库存不足', 'danger')
            return redirect(url_for('sales.order_detail', id=order_id))

    order.status = 'completed'
    db.session.commit()
    flash('销售订单已确认，库存已扣减', 'success')
    return redirect(url_for('sales.order_detail', id=order_id))
