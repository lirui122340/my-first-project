import json
import os
import asyncio
from services.ticket_service import query_12306, query_juhe

_city_mapping = None


def _get_city_mapping():
    global _city_mapping
    if _city_mapping is None:
        data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'city_mapping.json')
        with open(data_path, 'r', encoding='utf-8') as f:
            _city_mapping = json.load(f)
    return _city_mapping


def _find_transit_cities(from_city, to_city, city_mapping):
    from_destinations = set(city_mapping.get(from_city, []))
    to_sources = set()
    for city, destinations in city_mapping.items():
        if to_city in destinations:
            to_sources.add(city)

    transit_candidates = from_destinations & to_sources
    transit_candidates.discard(from_city)
    transit_candidates.discard(to_city)

    return list(transit_candidates)


def _get_min_price(trains):
    if not trains:
        return None
    min_price = float('inf')
    for train in trains:
        prices = train.get('prices', {})
        for p in prices.values():
            try:
                val = int(p)
                if 0 < val < min_price:
                    min_price = val
            except (ValueError, TypeError):
                pass
    return min_price if min_price != float('inf') else None


def _get_min_duration(trains):
    if not trains:
        return None
    min_duration = float('inf')
    for train in trains:
        duration = train.get('duration', '')
        if not duration:
            continue
        parts = duration.split(':')
        if len(parts) >= 2:
            try:
                hours = int(parts[0]) + int(parts[1]) / 60
                if hours < min_duration:
                    min_duration = hours
            except ValueError:
                pass
    return min_duration if min_duration != float('inf') else None


def _format_duration(hours):
    if hours is None:
        return ''
    h = int(hours)
    m = int(round((hours - h) * 60))
    return f'{h:02d}:{m:02d}'


async def _query_leg(from_city, to_city, date):
    loop = asyncio.get_event_loop()
    try:
        trains = await loop.run_in_executor(None, query_12306, from_city, to_city, date)
        if trains and len(trains) > 0:
            return trains
        trains = await loop.run_in_executor(None, query_juhe, from_city, to_city, date)
        if trains and len(trains) > 0:
            return trains
        return None
    except Exception:
        return None


async def find_transfer_routes(from_city, to_city, date):
    city_mapping = _get_city_mapping()
    transit_cities = _find_transit_cities(from_city, to_city, city_mapping)

    direct_trains = await _query_leg(from_city, to_city, date)
    direct_price = _get_min_price(direct_trains) if direct_trains else None
    direct_duration = _get_min_duration(direct_trains) if direct_trains else None
    direct_train_count = len(direct_trains) if direct_trains else 0

    direct_info = {
        'fromCity': from_city,
        'toCity': to_city,
        'minPrice': direct_price,
        'duration': _format_duration(direct_duration),
        'trainCount': direct_train_count,
    }

    if not transit_cities:
        return {
            'direct': direct_info,
            'transfers': [],
            'recommendations': [],
        }

    semaphore = asyncio.Semaphore(3)

    async def query_transit(transit_city):
        async with semaphore:
            leg1 = await _query_leg(from_city, transit_city, date)
            await asyncio.sleep(0.5)
            leg2 = await _query_leg(transit_city, to_city, date)
            return transit_city, leg1, leg2

    tasks = [query_transit(tc) for tc in transit_cities[:15]]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    transfer_routes = []
    for r in results:
        if isinstance(r, Exception):
            continue
        transit_city, leg1, leg2 = r
        if not leg1 or not leg2:
            continue

        price1 = _get_min_price(leg1)
        price2 = _get_min_price(leg2)
        if price1 is None or price2 is None:
            continue

        total_price = price1 + price2
        duration1 = _get_min_duration(leg1)
        duration2 = _get_min_duration(leg2)
        total_duration = (duration1 or 0) + (duration2 or 0)

        savings = 0
        if direct_price and total_price < direct_price:
            savings = direct_price - total_price

        transfer_routes.append({
            'transitCity': transit_city,
            'leg1': {
                'fromCity': from_city,
                'toCity': transit_city,
                'minPrice': price1,
                'duration': _format_duration(duration1),
                'trainCount': len(leg1),
            },
            'leg2': {
                'fromCity': transit_city,
                'toCity': to_city,
                'minPrice': price2,
                'duration': _format_duration(duration2),
                'trainCount': len(leg2),
            },
            'totalPrice': total_price,
            'totalDuration': _format_duration(total_duration),
            'savings': savings,
        })

    transfer_routes.sort(key=lambda x: x['totalPrice'])

    recommendations = []
    for route in transfer_routes:
        if direct_price and route['totalPrice'] < direct_price:
            route['tag'] = '更省钱'
            recommendations.append(route)
        elif not direct_price:
            route['tag'] = '可到达'
            recommendations.append(route)

    return {
        'direct': direct_info,
        'transfers': transfer_routes,
        'recommendations': recommendations[:5],
    }


def find_transfer_routes_sync(from_city, to_city, date):
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                return pool.submit(
                    lambda: asyncio.run(find_transfer_routes(from_city, to_city, date))
                ).result()
        else:
            return loop.run_until_complete(find_transfer_routes(from_city, to_city, date))
    except RuntimeError:
        return asyncio.run(find_transfer_routes(from_city, to_city, date))
