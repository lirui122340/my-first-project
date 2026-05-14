import os

from flask import Flask, jsonify
from flask_cors import CORS
from routes.ticket import ticket_bp
from routes.city import city_bp
from routes.route import route_bp
from routes.hostel import hostel_bp

app = Flask(__name__)
CORS(app)

app.register_blueprint(ticket_bp)
app.register_blueprint(city_bp)
app.register_blueprint(route_bp)
app.register_blueprint(hostel_bp)


@app.route('/')
def index():
    return jsonify({'code': 0, 'message': '省钱旅游小程序后端服务运行中'})


@app.route('/health')
def health():
    return jsonify({'status': 'ok'}), 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    print(f'服务器已启动: http://0.0.0.0:{port}')
    app.run(host='0.0.0.0', port=port, debug=True)
