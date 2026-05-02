from flask import Blueprint, request, jsonify
from services.hostel_service import get_hostels_by_city, get_cities_with_hostels

hostel_bp = Blueprint('hostel', __name__, url_prefix='/api/hostel')


@hostel_bp.route('/list', methods=['GET'])
def get_hostel_list():
    city = request.args.get('city', '')
    sort_by = request.args.get('sort_by', 'price')
    type_filter = request.args.get('type', '')

    if not city:
        return jsonify({'code': 1, 'message': '缺少必要参数: city'}), 400

    try:
        result = get_hostels_by_city(city, sort_by=sort_by, type_filter=type_filter)
        return jsonify({'code': 0, 'message': 'success', 'data': result})
    except Exception as e:
        print(f'查询青旅数据失败: {e}')
        return jsonify({'code': 1, 'message': '服务器内部错误'}), 500


@hostel_bp.route('/cities', methods=['GET'])
def get_hostel_cities():
    try:
        result = get_cities_with_hostels()
        return jsonify({'code': 0, 'message': 'success', 'data': result})
    except Exception as e:
        print(f'查询青旅城市列表失败: {e}')
        return jsonify({'code': 1, 'message': '服务器内部错误'}), 500
