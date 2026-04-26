from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required
from datetime import datetime
from app.database import db
from app.models.production import ProductionOrder, BillOfMaterial
from app.models.inventory import Product
from wtforms import StringField, IntegerField, DateField, SelectField, FloatField, TextAreaField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm

production_bp = Blueprint('production', __name__)


class ProductionOrderForm(FlaskForm):
    product_id = SelectField('产品', coerce=int, validators=[DataRequired()])
    quantity = IntegerField('生产数量', validators=[DataRequired()])
    start_date = DateField('开始日期', format='%Y-%m-%d')
    end_date = DateField('结束日期', format='%Y-%m-%d')
    remark = TextAreaField('备注')
    submit = SubmitField('保存')


class BOMForm(FlaskForm):
    product_id = SelectField('产品', coerce=int, validators=[DataRequired()])
    material_id = SelectField('物料', coerce=int, validators=[DataRequired()])
    quantity = FloatField('用量', validators=[DataRequired()])
    unit = StringField('单位')
    remark = StringField('备注')
    submit = SubmitField('保存')


@production_bp.route('/')
@login_required
def index():
    orders = ProductionOrder.query.order_by(ProductionOrder.created_at.desc()).all()
    return render_template('production/index.html', orders=orders)


@production_bp.route('/order/add', methods=['GET', 'POST'])
@login_required
def add_order():
    form = ProductionOrderForm()
    form.product_id.choices = [(p.id, f'{p.sku} - {p.name}') for p in Product.query.filter_by(is_active=True)]
    if form.validate_on_submit():
        order = ProductionOrder(
            order_no=f'MO{datetime.now().strftime("%Y%m%d%H%M%S")}',
            product_id=form.product_id.data,
            quantity=form.quantity.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            remark=form.remark.data
        )
        db.session.add(order)
        db.session.commit()
        flash('生产订单创建成功', 'success')
        return redirect(url_for('production.index'))
    return render_template('production/order_form.html', form=form)


@production_bp.route('/order/<int:id>')
@login_required
def order_detail(id):
    order = ProductionOrder.query.get_or_404(id)
    return render_template('production/order_detail.html', order=order)


@production_bp.route('/order/<int:id>/start')
@login_required
def start_order(id):
    order = ProductionOrder.query.get_or_404(id)
    if order.status == 'pending':
        order.status = 'in_progress'
        order.start_date = datetime.now()
        db.session.commit()
        flash('生产订单已开始', 'success')
    return redirect(url_for('production.order_detail', id=id))


@production_bp.route('/order/<int:id>/complete')
@login_required
def complete_order(id):
    order = ProductionOrder.query.get_or_404(id)
    if order.status == 'in_progress':
        order.status = 'completed'
        order.completed_quantity = order.quantity
        order.end_date = datetime.now()
        db.session.commit()
        flash('生产订单已完成', 'success')
    return redirect(url_for('production.order_detail', id=id))


@production_bp.route('/bom')
@login_required
def bom_list():
    boms = BillOfMaterial.query.all()
    return render_template('production/bom_list.html', boms=boms)


@production_bp.route('/bom/add', methods=['GET', 'POST'])
@login_required
def add_bom():
    form = BOMForm()
    products = Product.query.filter_by(is_active=True).all()
    form.product_id.choices = [(p.id, f'{p.sku} - {p.name}') for p in products]
    form.material_id.choices = [(p.id, f'{p.sku} - {p.name}') for p in products]
    if form.validate_on_submit():
        bom = BillOfMaterial(
            product_id=form.product_id.data,
            material_id=form.material_id.data,
            quantity=form.quantity.data,
            unit=form.unit.data,
            remark=form.remark.data
        )
        db.session.add(bom)
        db.session.commit()
        flash('BOM添加成功', 'success')
        return redirect(url_for('production.bom_list'))
    return render_template('production/bom_form.html', form=form)
