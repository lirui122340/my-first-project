from dotenv import load_dotenv
load_dotenv()

from flask import Flask, jsonify
from flask_cors import CORS
from routes.ticket import ticket_bp
from routes.city import city_bp
from routes.route import route_bp
from routes.hostel import hostel_bp
import config

app = Flask(__name__)
CORS(app)

app.register_blueprint(ticket_bp)
app.register_blueprint(city_bp)
app.register_blueprint(route_bp)
app.register_blueprint(hostel_bp)


@app.route('/')
def index():
    return jsonify({'code': 0, 'message': '省钱旅游小程序后端服务运行中'})


if __name__ == '__main__':
    print(f'服务器已启动: http://localhost:{config.PORT}')
    app.run(host='0.0.0.0', port=config.PORT, debug=True)
