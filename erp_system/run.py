from app import create_app
from app.database import db
from app.models.user import User

app = create_app()

with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', email='admin@erp.com', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print('Admin user created: admin / admin123')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
