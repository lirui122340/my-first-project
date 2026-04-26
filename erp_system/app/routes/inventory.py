from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required
from app.database import db
from app.models.inventory import Product, Category, Stock, Warehouse
from app.forms.inventory import ProductForm, CategoryForm, WarehouseForm

inventory_bp = Blueprint('inventory', __name__)


@inventory_bp.route('/')
@login_required
def index():
    products = Product.query.all()
    return render_template('inventory/index.html', products=products)


@inventory_bp.route('/product/add', methods=['GET', 'POST'])
@login_required
def add_product():
    form = ProductForm()
    form.category_id.choices = [(c.id, c.name) for c in Category.query.all()]
    if form.validate_on_submit():
        product = Product(
            sku=form.sku.data,
            name=form.name.data,
            description=form.description.data,
            category_id=form.category_id.data,
            unit=form.unit.data,
            purchase_price=form.purchase_price.data,
            sale_price=form.sale_price.data,
            min_stock=form.min_stock.data
        )
        db.session.add(product)
        db.session.commit()
        flash('产品添加成功', 'success')
        return redirect(url_for('inventory.index'))
    return render_template('inventory/product_form.html', form=form)


@inventory_bp.route('/product/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    product = Product.query.get_or_404(id)
    form = ProductForm(obj=product)
    form.category_id.choices = [(c.id, c.name) for c in Category.query.all()]
    if form.validate_on_submit():
        product.sku = form.sku.data
        product.name = form.name.data
        product.description = form.description.data
        product.category_id = form.category_id.data
        product.unit = form.unit.data
        product.purchase_price = form.purchase_price.data
        product.sale_price = form.sale_price.data
        product.min_stock = form.min_stock.data
        db.session.commit()
        flash('产品更新成功', 'success')
        return redirect(url_for('inventory.index'))
    return render_template('inventory/product_form.html', form=form, product=product)


@inventory_bp.route('/product/delete/<int:id>')
@login_required
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash('产品删除成功', 'success')
    return redirect(url_for('inventory.index'))


@inventory_bp.route('/category')
@login_required
def categories():
    categories = Category.query.all()
    return render_template('inventory/categories.html', categories=categories)


@inventory_bp.route('/category/add', methods=['GET', 'POST'])
@login_required
def add_category():
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(name=form.name.data, description=form.description.data)
        db.session.add(category)
        db.session.commit()
        flash('分类添加成功', 'success')
        return redirect(url_for('inventory.categories'))
    return render_template('inventory/category_form.html', form=form)


@inventory_bp.route('/warehouse')
@login_required
def warehouses():
    warehouses = Warehouse.query.all()
    return render_template('inventory/warehouses.html', warehouses=warehouses)


@inventory_bp.route('/warehouse/add', methods=['GET', 'POST'])
@login_required
def add_warehouse():
    form = WarehouseForm()
    if form.validate_on_submit():
        warehouse = Warehouse(
            name=form.name.data,
            location=form.location.data,
            capacity=form.capacity.data
        )
        db.session.add(warehouse)
        db.session.commit()
        flash('仓库添加成功', 'success')
        return redirect(url_for('inventory.warehouses'))
    return render_template('inventory/warehouse_form.html', form=form)


@inventory_bp.route('/stock')
@login_required
def stocks():
    stocks = Stock.query.all()
    return render_template('inventory/stocks.html', stocks=stocks)
