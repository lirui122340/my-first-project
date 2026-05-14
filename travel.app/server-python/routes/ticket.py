import json
import os
from flask import Blueprint, request, jsonify
from services.aggregator import batch_query_destinations
from services.ticket_service import query_tickets_with_prices
from services.city_service import get_city_mapping, get_destinations_from_db

ticket_bp = Blueprint('ticket', __name__, url_prefix='/api/ticket')


@ticket_bp.route('/destinations', methods=['GET'])
def get_destinations():
    from_city = request.args.get('from_city', '')
    date = request.args.get('date', '')
    sort_by = request.args.get('sort_by', '')

    if not from_city or not date:
        return jsonify({'code': 1, 'message': '缺少必要参数: from_city, date'}), 400

    try:
        city_mapping = get_city_mapping()
        result = batch_query_destinations(from_city, date, city_mapping)

        if sort_by == 'price':
            result['destinations'].sort(key=lambda x: (
                0 if x['minPrice'] > 0 else 1,
                x['minPrice'] if x['minPrice'] > 0 else float('inf'),
                -x['totalSeats']
            ))
        else:
            result['destinations'].sort(key=lambda x: x['totalSeats'], reverse=True)

        return jsonify({'code': 0, 'message': 'success', 'data': result})
    except Exception as e:
        print(f'查询可直达城市失败: {e}')
        return jsonify({'code': 1, 'message': '服务器内部错误'}), 500


@ticket_bp.route('/quick-destinations', methods=['GET'])
def get_quick_destinations():
    from_city = request.args.get('from_city', '')

    if not from_city:
        return jsonify({'code': 1, 'message': '缺少必要参数: from_city'}), 400

    try:
        destinations = get_destinations_from_db(from_city)

        return jsonify({
            'code': 0,
            'message': 'success',
            'data': {
                'fromCity': from_city,
                'destinations': destinations,
            }
        })
    except Exception as e:
        print(f'查询可直达城市列表失败: {e}')
        return jsonify({'code': 1, 'message': '服务器内部错误'}), 500


@ticket_bp.route('/trains', methods=['GET'])
def get_trains():
    from_city = request.args.get('from_city', '')
    to_city = request.args.get('to_city', '')
    date = request.args.get('date', '')
    train_type = request.args.get('train_type', '')

    if not from_city or not to_city or not date:
        return jsonify({'code': 1, 'message': '缺少必要参数: from_city, to_city, date'}), 400

    try:
        result = query_tickets_with_prices(from_city, to_city, date)

        if not result or not result.get('data') or len(result['data']) == 0:
            return jsonify({
                'code': 0,
                'message': 'success',
                'data': {
                    'fromStation': from_city,
                    'toStation': to_city,
                    'date': date,
                    'tickets': [],
                },
            })

        tickets = result['data']
        if train_type and train_type != 'all':
            prefix_map = {
                'G-D': ['G', 'D', 'C'],
                'K-T-Z': ['K', 'T', 'Z'],
            }
            prefixes = prefix_map.get(train_type, [train_type])
            tickets = [t for t in tickets if any(t['trainNo'].startswith(p) for p in prefixes)]

        for t in tickets:
            t.pop('trainNoInternal', None)
            t.pop('fromStationNo', None)
            t.pop('toStationNo', None)
            t.pop('seatTypes', None)

        from_station = tickets[0]['fromStation'] if tickets else from_city
        to_station = tickets[0]['toStation'] if tickets else to_city

        return jsonify({
            'code': 0,
            'message': 'success',
            'data': {
                'fromStation': from_station,
                'toStation': to_station,
                'date': date,
                'tickets': tickets,
            },
        })
    except Exception as e:
        print(f'查询车次详情失败: {e}')
        return jsonify({'code': 1, 'message': '服务器内部错误'}), 500
