import json
import os

_hostel_data = None


def _load_hostel_data():
    global _hostel_data
    if _hostel_data is None:
        data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'hostel_data.json')
        with open(data_path, 'r', encoding='utf-8') as f:
            _hostel_data = json.load(f)
    return _hostel_data


def get_hostels_by_city(city, sort_by='price', type_filter=''):
    data = _load_hostel_data()
    city_data = data.get(city)

    if not city_data:
        return {
            'city': city,
            'avgPrice': 0,
            'hostels': [],
        }

    hostels = city_data.get('hostels', [])

    if type_filter:
        hostels = [h for h in hostels if h.get('type') == type_filter]

    if sort_by == 'price':
        hostels.sort(key=lambda x: x.get('price', 9999))
    elif sort_by == 'rating':
        hostels.sort(key=lambda x: x.get('rating', 0), reverse=True)

    return {
        'city': city,
        'avgPrice': city_data.get('avgPrice', 0),
        'hostels': hostels,
    }


def get_cities_with_hostels():
    data = _load_hostel_data()
    result = []
    for city, info in data.items():
        cheapest = None
        for h in info.get('hostels', []):
            if h.get('type') == '青旅':
                if cheapest is None or h.get('price', 9999) < cheapest:
                    cheapest = h.get('price', 0)
        result.append({
            'city': city,
            'avgPrice': info.get('avgPrice', 0),
            'cheapestHostel': cheapest,
        })
    result.sort(key=lambda x: x.get('avgPrice', 9999))
    return result
