from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required
from app.database import db
from app.models.customer import Customer
from app.models.sales import SalesOrder
from wtforms import StringField, FloatField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm

customer_bp = Blueprint('customer', __name__)


class CustomerForm(FlaskForm):
    name = StringField('客户名称', validators=[DataRequired()])
    contact = StringField('联系人')
    phone = StringField('电话')
    email = StringField('邮箱')
    address = TextAreaField('地址')
    credit_limit = FloatField('信用额度', default=0)
    level = SelectField('客户等级', choices=[('normal', '普通'), ('silver', '银卡'), ('gold', '金卡'), ('diamond', '钻石')])
    submit = SubmitField('保存')


@customer_bp.route('/')
@login_required
def index():
    customers = Customer.query.all()
    return render_template('customer/index.html', customers=customers)


@customer_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    form = CustomerForm()
    if form.validate_on_submit():
        customer = Customer(
            name=form.name.data,
            contact=form.contact.data,
            phone=form.phone.data,
            email=form.email.data,
            address=form.address.data,
            credit_limit=form.credit_limit.data,
            level=form.level.data
        )
        db.session.add(customer)
        db.session.commit()
        flash('客户添加成功', 'success')
        return redirect(url_for('customer.index'))
    return render_template('customer/form.html', form=form)


@customer_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    customer = Customer.query.get_or_404(id)
    form = CustomerForm(obj=customer)
    if form.validate_on_submit():
        customer.name = form.name.data
        customer.contact = form.contact.data
        customer.phone = form.phone.data
        customer.email = form.email.data
        customer.address = form.address.data
        customer.credit_limit = form.credit_limit.data
        customer.level = form.level.data
        db.session.commit()
        flash('客户更新成功', 'success')
        return redirect(url_for('customer.index'))
    return render_template('customer/form.html', form=form, customer=customer)


@customer_bp.route('/delete/<int:id>')
@login_required
def delete(id):
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()
    flash('客户删除成功', 'success')
    return redirect(url_for('customer.index'))


@customer_bp.route('/<int:id>')
@login_required
def detail(id):
    customer = Customer.query.get_or_404(id)
    orders = SalesOrder.query.filter_by(customer_id=id).order_by(SalesOrder.created_at.desc()).all()
    total_amount = sum(o.total_amount for o in orders if o.status == 'completed')
    return render_template('customer/detail.html', customer=customer, orders=orders, total_amount=total_amount)
