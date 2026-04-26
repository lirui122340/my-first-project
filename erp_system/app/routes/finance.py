from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required
from datetime import datetime
from app.database import db
from app.models.finance import Account, Transaction, Invoice
from wtforms import StringField, FloatField, DateField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm

finance_bp = Blueprint('finance', __name__)


class AccountForm(FlaskForm):
    name = StringField('账户名称', validators=[DataRequired()])
    account_type = SelectField('账户类型', choices=[('cash', '现金'), ('bank', '银行'), ('alipay', '支付宝'), ('wechat', '微信')])
    bank_name = StringField('银行名称')
    account_number = StringField('账号')
    balance = FloatField('初始余额', default=0)
    submit = SubmitField('保存')


class TransactionForm(FlaskForm):
    account_id = SelectField('账户', coerce=int, validators=[DataRequired()])
    transaction_type = SelectField('类型', choices=[('income', '收入'), ('expense', '支出')])
    amount = FloatField('金额', validators=[DataRequired()])
    description = TextAreaField('描述')
    submit = SubmitField('保存')


@finance_bp.route('/')
@login_required
def index():
    accounts = Account.query.all()
    total_balance = sum(a.balance for a in accounts)
    recent_transactions = Transaction.query.order_by(Transaction.created_at.desc()).limit(10).all()
    return render_template('finance/index.html', accounts=accounts, total_balance=total_balance,
                           transactions=recent_transactions)


@finance_bp.route('/account')
@login_required
def accounts():
    accounts = Account.query.all()
    return render_template('finance/accounts.html', accounts=accounts)


@finance_bp.route('/account/add', methods=['GET', 'POST'])
@login_required
def add_account():
    form = AccountForm()
    if form.validate_on_submit():
        account = Account(
            name=form.name.data,
            account_type=form.account_type.data,
            bank_name=form.bank_name.data,
            account_number=form.account_number.data,
            balance=form.balance.data
        )
        db.session.add(account)
        db.session.commit()
        flash('账户添加成功', 'success')
        return redirect(url_for('finance.accounts'))
    return render_template('finance/account_form.html', form=form)


@finance_bp.route('/transaction')
@login_required
def transactions():
    transactions = Transaction.query.order_by(Transaction.created_at.desc()).all()
    return render_template('finance/transactions.html', transactions=transactions)


@finance_bp.route('/transaction/add', methods=['GET', 'POST'])
@login_required
def add_transaction():
    form = TransactionForm()
    form.account_id.choices = [(a.id, a.name) for a in Account.query.filter_by(is_active=True)]
    if form.validate_on_submit():
        account = Account.query.get(form.account_id.data)
        amount = form.amount.data
        if form.transaction_type.data == 'expense':
            amount = -amount
        account.balance += amount
        transaction = Transaction(
            account_id=form.account_id.data,
            transaction_type=form.transaction_type.data,
            amount=abs(form.amount.data),
            balance_after=account.balance,
            description=form.description.data
        )
        db.session.add(transaction)
        db.session.commit()
        flash('交易记录添加成功', 'success')
        return redirect(url_for('finance.transactions'))
    return render_template('finance/transaction_form.html', form=form)


@finance_bp.route('/invoice')
@login_required
def invoices():
    invoices = Invoice.query.order_by(Invoice.created_at.desc()).all()
    return render_template('finance/invoices.html', invoices=invoices)
