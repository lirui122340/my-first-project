from datetime import datetime, date
from app.database import db


class Department(db.Model):
    __tablename__ = 'departments'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    manager_id = db.Column(db.Integer)
    description = db.Column(db.String(256))
    employees = db.relationship('Employee', backref='department', lazy='dynamic')


class Employee(db.Model):
    __tablename__ = 'employees'

    id = db.Column(db.Integer, primary_key=True)
    employee_no = db.Column(db.String(32), unique=True, nullable=False)
    name = db.Column(db.String(64), nullable=False)
    gender = db.Column(db.String(10))
    birth_date = db.Column(db.Date)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(64))
    address = db.Column(db.String(256))
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    position = db.Column(db.String(64))
    hire_date = db.Column(db.Date, default=date.today)
    salary = db.Column(db.Float, default=0)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Attendance(db.Model):
    __tablename__ = 'attendances'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    date = db.Column(db.Date, nullable=False)
    check_in = db.Column(db.DateTime)
    check_out = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='present')
    remark = db.Column(db.String(256))
    employee = db.relationship('Employee', backref=db.backref('attendances', lazy='dynamic'))
