from flask import Blueprint, request, jsonify
from services.route_service import find_transfer_routes_sync

route_bp = Blueprint('route', __name__, url_prefix='/api/route')


@route_bp.route('/transfer', methods=['GET'])
def get_transfer_routes():
    from_city = request.args.get('from_city', '')
    to_city = request.args.get('to_city', '')
    date = request.args.get('date', '')

    if not from_city or not to_city or not date:
        return jsonify({'code': 1, 'message': '缺少必要参数: from_city, to_city, date'}), 400

    try:
        result = find_transfer_routes_sync(from_city, to_city, date)
        return jsonify({'code': 0, 'message': 'success', 'data': result})
    except Exception as e:
        print(f'查询中转路线失败: {e}')
        return jsonify({'code': 1, 'message': '服务器内部错误'}), 500
