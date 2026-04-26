from flask import Flask
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from config import config
from app.database import db

login_manager = LoginManager()
csrf = CSRFProtect()
login_manager.login_view = 'auth.login'
login_manager.login_message = '请先登录'


def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.inventory import inventory_bp
    from app.routes.purchase import purchase_bp
    from app.routes.sales import sales_bp
    from app.routes.finance import finance_bp
    from app.routes.customer import customer_bp
    from app.routes.hr import hr_bp
    from app.routes.production import production_bp
    from app.routes.report import report_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(inventory_bp, url_prefix='/inventory')
    app.register_blueprint(purchase_bp, url_prefix='/purchase')
    app.register_blueprint(sales_bp, url_prefix='/sales')
    app.register_blueprint(finance_bp, url_prefix='/finance')
    app.register_blueprint(customer_bp, url_prefix='/customer')
    app.register_blueprint(hr_bp, url_prefix='/hr')
    app.register_blueprint(production_bp, url_prefix='/production')
    app.register_blueprint(report_bp, url_prefix='/report')

    @app.route('/')
    def index():
        from flask import redirect, url_for
        return redirect(url_for('auth.login'))

    return app
