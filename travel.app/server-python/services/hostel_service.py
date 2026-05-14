from services.db import execute_query, execute_query_one

_hostel_cache = {}
_hostel_cache_ts = {}
_CACHE_TTL = 300


def get_hostels_by_city(city, sort_by='price', type_filter=''):
    import time
    now = time.time()
    cache_key = f'{city}_{sort_by}_{type_filter}'
    if cache_key in _hostel_cache and now - _hostel_cache_ts.get(cache_key, 0) < _CACHE_TTL:
        return _hostel_cache[cache_key]

    sql = 'SELECT * FROM hostels WHERE city = %s'
    params = [city]

    if type_filter:
        sql += ' AND type = %s'
        params.append(type_filter)

    if sort_by == 'rating':
        sql += ' ORDER BY rating DESC, price ASC'
    else:
        sql += ' ORDER BY price ASC, rating DESC'

    rows = execute_query(sql, params)

    if rows:
        hostels = []
        for row in rows:
            tags = row.get('tags', '')
            hostel = {
                'name': row['name'],
                'type': row['type'],
                'price': row['price'],
                'rating': float(row['rating']) if row['rating'] else 0.0,
                'location': row.get('location', ''),
                'tags': [t.strip() for t in tags.split(',') if t.strip()] if tags else [],
            }
            if row.get('phone'):
                hostel['phone'] = row['phone']
            if row.get('address'):
                hostel['address'] = row['address']
            hostels.append(hostel)

        avg_result = execute_query_one(
            'SELECT AVG(price) as avg_price FROM hostels WHERE city = %s AND type = %s',
            (city, '青旅')
        )
        avg_price = int(avg_result['avg_price']) if avg_result and avg_result['avg_price'] else 0

        result = {
            'city': city,
            'avgPrice': avg_price,
            'hostels': hostels,
        }
        _hostel_cache[cache_key] = result
        _hostel_cache_ts[cache_key] = now
        return result

    return _fallback_hostel_data(city, sort_by, type_filter)


def get_cities_with_hostels():
    rows = execute_query(
        'SELECT city, MIN(price) as cheapest, AVG(CASE WHEN type=%s THEN price ELSE NULL END) as avg_price '
        'FROM hostels GROUP BY city ORDER BY avg_price ASC',
        ('青旅',)
    )
    if rows:
        result = []
        for row in rows:
            cheapest = int(row['cheapest']) if row['cheapest'] else 0
            avg_price = int(row['avg_price']) if row['avg_price'] else 0
            result.append({
                'city': row['city'],
                'avgPrice': avg_price,
                'cheapestHostel': cheapest,
            })
        return result
    return []


def _fallback_hostel_data(city, sort_by, type_filter):
    import json
    import os
    data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'hostel_data.json')
    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        city_data = data.get(city)
        if not city_data:
            return {'city': city, 'avgPrice': 0, 'hostels': []}
        hostels = city_data.get('hostels', [])
        if type_filter:
            hostels = [h for h in hostels if h.get('type') == type_filter]
        if sort_by == 'price':
            hostels.sort(key=lambda x: x.get('price', 9999))
        elif sort_by == 'rating':
            hostels.sort(key=lambda x: x.get('rating', 0), reverse=True)
        return {'city': city, 'avgPrice': city_data.get('avgPrice', 0), 'hostels': hostels}
    except Exception:
        return {'city': city, 'avgPrice': 0, 'hostels': []}
