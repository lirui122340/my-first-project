import json
import os
from services.db import execute_query

_city_mapping_cache = None
_city_mapping_ts = 0
_CACHE_TTL = 300


def get_city_mapping():
    global _city_mapping_cache, _city_mapping_ts
    import time
    now = time.time()
    if _city_mapping_cache and now - _city_mapping_ts < _CACHE_TTL:
        return _city_mapping_cache

    rows = execute_query('SELECT from_city, to_city FROM city_routes ORDER BY from_city, id')
    if rows:
        mapping = {}
        for row in rows:
            from_city = row['from_city']
            to_city = row['to_city']
            if from_city not in mapping:
                mapping[from_city] = []
            mapping[from_city].append(to_city)
        _city_mapping_cache = mapping
        _city_mapping_ts = now
        return mapping

    data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'city_mapping.json')
    with open(data_path, 'r', encoding='utf-8') as f:
        _city_mapping_cache = json.load(f)
        _city_mapping_ts = now
    return _city_mapping_cache


def get_destinations_from_db(from_city):
    rows = execute_query(
        'SELECT to_city FROM city_routes WHERE from_city = %s ORDER BY id',
        (from_city,)
    )
    if rows:
        return [row['to_city'] for row in rows]
    mapping = get_city_mapping()
    return mapping.get(from_city, [])


def get_city_list_from_db():
    rows = execute_query('SELECT name, province, is_hot, first_letter FROM cities ORDER BY first_letter, name')
    if not rows:
        return None

    hot = []
    all_cities = {}
    for row in rows:
        name = row['name']
        if row['is_hot'] is True or row['is_hot'] == 1:
            hot.append(name)
        letter = row.get('first_letter', name[0]).upper()
        if not letter or not letter.isalpha():
            letter = name[0].upper()
        if letter not in all_cities:
            all_cities[letter] = []
        all_cities[letter].append(name)

    return {'hot': hot, 'all': all_cities}
