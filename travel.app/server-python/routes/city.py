import json
import os
from flask import Blueprint, jsonify

city_bp = Blueprint('city', __name__, url_prefix='/api/city')

_city_data = None
_city_mapping = None


def _get_city_data():
    global _city_data
    if _city_data is None:
        _city_data = {
            'hot': [
                '北京', '上海', '广州', '深圳', '成都',
                '杭州', '武汉', '西安', '南京', '重庆',
            ],
            'all': {
                'A': ['安阳', '安庆', '鞍山'],
                'B': ['北京', '蚌埠', '包头', '保定', '宝鸡'],
                'C': ['成都', '长沙', '常州', '长春', '沧州'],
                'D': ['大连', '东莞', '大庆', '大同'],
                'F': ['福州', '佛山', '抚顺'],
                'G': ['广州', '贵阳', '桂林', '赣州'],
                'H': ['杭州', '哈尔滨', '合肥', '海口', '呼和浩特', '惠州', '邯郸', '衡阳'],
                'J': ['济南', '济宁', '嘉兴', '金华', '江门', '九江'],
                'K': ['昆明', '开封'],
                'L': ['兰州', '洛阳', '连云港', '临沂', '柳州', '泸州'],
                'M': ['绵阳', '牡丹江'],
                'N': ['南京', '南昌', '南宁', '南通', '宁波'],
                'Q': ['青岛', '秦皇岛', '泉州', '齐齐哈尔'],
                'S': ['上海', '深圳', '沈阳', '石家庄', '苏州', '绍兴', '三亚'],
                'T': ['天津', '太原', '唐山', '台州'],
                'W': ['武汉', '无锡', '温州', '乌鲁木齐', '潍坊', '芜湖', '威海'],
                'X': ['西安', '厦门', '徐州', '西宁', '湘潭', '襄阳', '新乡'],
                'Y': ['银川', '烟台', '扬州', '宜昌', '榆林'],
                'Z': ['郑州', '珠海', '中山', '株洲', '遵义', '漳州', '淄博'],
            },
        }
    return _city_data


def _get_city_mapping():
    global _city_mapping
    if _city_mapping is None:
        data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'city_mapping.json')
        with open(data_path, 'r', encoding='utf-8') as f:
            _city_mapping = json.load(f)
    return _city_mapping


@city_bp.route('/list', methods=['GET'])
def get_city_list():
    data = _get_city_data()
    return jsonify({'code': 0, 'data': data})


@city_bp.route('/destinations', methods=['GET'])
def get_destinations():
    from_city = __import__('flask').request.args.get('from_city', '')
    city_mapping = _get_city_mapping()
    destinations = city_mapping.get(from_city, [])
    return jsonify({'code': 0, 'data': {'fromCity': from_city, 'destinations': destinations}})
