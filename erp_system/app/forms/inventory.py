from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FloatField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired


class ProductForm(FlaskForm):
    sku = StringField('SKU', validators=[DataRequired()])
    name = StringField('产品名称', validators=[DataRequired()])
    description = TextAreaField('描述')
    category_id = SelectField('分类', coerce=int)
    unit = StringField('单位', default='件')
    purchase_price = FloatField('采购价', default=0)
    sale_price = FloatField('销售价', default=0)
    min_stock = IntegerField('最低库存', default=0)
    submit = SubmitField('保存')


class CategoryForm(FlaskForm):
    name = StringField('分类名称', validators=[DataRequired()])
    description = TextAreaField('描述')
    submit = SubmitField('保存')


class WarehouseForm(FlaskForm):
    name = StringField('仓库名称', validators=[DataRequired()])
    location = StringField('位置')
    capacity = IntegerField('容量', default=0)
    submit = SubmitField('保存')
