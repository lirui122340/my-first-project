from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required
from datetime import date
from app.database import db
from app.models.hr import Employee, Department, Attendance
from wtforms import StringField, DateField, FloatField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm

hr_bp = Blueprint('hr', __name__)


class DepartmentForm(FlaskForm):
    name = StringField('部门名称', validators=[DataRequired()])
    description = TextAreaField('描述')
    submit = SubmitField('保存')


class EmployeeForm(FlaskForm):
    employee_no = StringField('工号', validators=[DataRequired()])
    name = StringField('姓名', validators=[DataRequired()])
    gender = SelectField('性别', choices=[('male', '男'), ('female', '女')])
    birth_date = DateField('出生日期', format='%Y-%m-%d')
    phone = StringField('电话')
    email = StringField('邮箱')
    address = TextAreaField('地址')
    department_id = SelectField('部门', coerce=int)
    position = StringField('职位')
    hire_date = DateField('入职日期', format='%Y-%m-%d', default=date.today())
    salary = FloatField('薪资')
    submit = SubmitField('保存')


@hr_bp.route('/')
@login_required
def index():
    employees = Employee.query.all()
    return render_template('hr/index.html', employees=employees)


@hr_bp.route('/department')
@login_required
def departments():
    departments = Department.query.all()
    return render_template('hr/departments.html', departments=departments)


@hr_bp.route('/department/add', methods=['GET', 'POST'])
@login_required
def add_department():
    form = DepartmentForm()
    if form.validate_on_submit():
        department = Department(name=form.name.data, description=form.description.data)
        db.session.add(department)
        db.session.commit()
        flash('部门添加成功', 'success')
        return redirect(url_for('hr.departments'))
    return render_template('hr/department_form.html', form=form)


@hr_bp.route('/employee/add', methods=['GET', 'POST'])
@login_required
def add_employee():
    form = EmployeeForm()
    form.department_id.choices = [(d.id, d.name) for d in Department.query.all()]
    form.department_id.choices.insert(0, (0, '-- 请选择 --'))
    if form.validate_on_submit():
        employee = Employee(
            employee_no=form.employee_no.data,
            name=form.name.data,
            gender=form.gender.data,
            birth_date=form.birth_date.data,
            phone=form.phone.data,
            email=form.email.data,
            address=form.address.data,
            department_id=form.department_id.data if form.department_id.data else None,
            position=form.position.data,
            hire_date=form.hire_date.data,
            salary=form.salary.data
        )
        db.session.add(employee)
        db.session.commit()
        flash('员工添加成功', 'success')
        return redirect(url_for('hr.index'))
    return render_template('hr/employee_form.html', form=form)


@hr_bp.route('/employee/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_employee(id):
    employee = Employee.query.get_or_404(id)
    form = EmployeeForm(obj=employee)
    form.department_id.choices = [(d.id, d.name) for d in Department.query.all()]
    if form.validate_on_submit():
        employee.employee_no = form.employee_no.data
        employee.name = form.name.data
        employee.gender = form.gender.data
        employee.birth_date = form.birth_date.data
        employee.phone = form.phone.data
        employee.email = form.email.data
        employee.address = form.address.data
        employee.department_id = form.department_id.data
        employee.position = form.position.data
        employee.hire_date = form.hire_date.data
        employee.salary = form.salary.data
        db.session.commit()
        flash('员工更新成功', 'success')
        return redirect(url_for('hr.index'))
    return render_template('hr/employee_form.html', form=form, employee=employee)


@hr_bp.route('/attendance')
@login_required
def attendance():
    today = date.today()
    records = Attendance.query.filter_by(date=today).all()
    return render_template('hr/attendance.html', records=records, today=today)


@hr_bp.route('/attendance/check_in/<int:employee_id>')
@login_required
def check_in(employee_id):
    today = date.today()
    from datetime import datetime
    attendance = Attendance.query.filter_by(employee_id=employee_id, date=today).first()
    if not attendance:
        attendance = Attendance(employee_id=employee_id, date=today, check_in=datetime.now())
        db.session.add(attendance)
        db.session.commit()
        flash('签到成功', 'success')
    else:
        flash('今日已签到', 'warning')
    return redirect(url_for('hr.attendance'))


@hr_bp.route('/attendance/check_out/<int:employee_id>')
@login_required
def check_out(employee_id):
    today = date.today()
    from datetime import datetime
    attendance = Attendance.query.filter_by(employee_id=employee_id, date=today).first()
    if attendance and not attendance.check_out:
        attendance.check_out = datetime.now()
        db.session.commit()
        flash('签退成功', 'success')
    return redirect(url_for('hr.attendance'))
