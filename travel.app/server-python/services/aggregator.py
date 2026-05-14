import time
import asyncio
import config
from services.ticket_service import query_12306, query_juhe

_cache = {}

MAX_DESTINATIONS = 12
OVERALL_TIMEOUT = 45


def _get_cache_key(from_city, date):
    return f'{from_city}_{date}'


def _get_from_cache(key):
    entry = _cache.get(key)
    if entry and time.time() - entry['timestamp'] < config.CACHE_TTL:
        return entry['data']
    _cache.pop(key, None)
    return None


def _set_cache(key, data):
    _cache[key] = {'data': data, 'timestamp': time.time()}


def _find_cheapest_train_by_duration(trains):
    min_price = float('inf')
    for train in trains:
        duration = train.get('duration', '')
        if not duration:
            continue
        parts = duration.split(':')
        if len(parts) < 2:
            continue
        try:
            hours = int(parts[0]) + int(parts[1]) / 60
        except ValueError:
            continue

        prefix = train['trainNo'][0] if train['trainNo'] else ''
        if prefix == 'G':
            estimated_price = round(hours * 115)
        elif prefix in ('D', 'C'):
            estimated_price = round(hours * 50)
        else:
            estimated_price = round(hours * 15)

        if estimated_price < min_price:
            min_price = estimated_price
    return min_price


def _aggregate_results(from_city, date, results):
    destination_list = []

    for city, trains in results:
        if not trains or len(trains) == 0:
            continue

        total_seats = 0
        min_price = float('inf')
        train_count = len(trains)

        for train in trains:
            seats = train.get('seats', {})
            for seat_info in seats.values():
                try:
                    total_seats += int(seat_info)
                except (ValueError, TypeError):
                    pass

            prices = train.get('prices', {})
            valid_prices = []
            for p in prices.values():
                try:
                    val = int(p)
                    if val > 0:
                        valid_prices.append(val)
                except (ValueError, TypeError):
                    pass
            if valid_prices:
                min_val = min(valid_prices)
                if min_val < min_price:
                    min_price = min_val

        if min_price == float('inf'):
            min_price = _find_cheapest_train_by_duration(trains)

        destination_list.append({
            'city': city,
            'totalSeats': total_seats or 0,
            'minPrice': min_price if min_price != float('inf') else 0,
            'trainCount': train_count,
        })

    destination_list.sort(key=lambda x: x['totalSeats'], reverse=True)

    return {'fromCity': from_city, 'date': date, 'destinations': destination_list}


async def _query_single_city(from_city, to_city, date):
    loop = asyncio.get_event_loop()
    try:
        result = await asyncio.wait_for(
            loop.run_in_executor(None, query_12306, from_city, to_city, date),
            timeout=10
        )
        if result and len(result) > 0:
            return to_city, result

        result = await asyncio.wait_for(
            loop.run_in_executor(None, query_juhe, from_city, to_city, date),
            timeout=8
        )
        if result and len(result) > 0:
            return to_city, result

        return to_city, []
    except asyncio.TimeoutError:
        print(f'查询 {from_city}→{to_city} 超时')
        return to_city, []
    except Exception as e:
        print(f'查询 {from_city}→{to_city} 失败: {e}')
        return to_city, []


async def _batch_query_async(from_city, date, destinations):
    results = []
    semaphore = asyncio.Semaphore(3)

    async def limited_query(to_city):
        async with semaphore:
            return await _query_single_city(from_city, to_city, date)

    for i in range(0, len(destinations), 3):
        batch = destinations[i:i + 3]
        tasks = [limited_query(to_city) for to_city in batch]
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)

        for r in batch_results:
            if isinstance(r, Exception):
                results.append(('', []))
            else:
                results.append(r)

        if i + 3 < len(destinations):
            await asyncio.sleep(0.2)

    return results


def batch_query_destinations(from_city, date, city_mapping):
    cache_key = _get_cache_key(from_city, date)
    cached = _get_from_cache(cache_key)
    if cached:
        return cached

    all_destinations = city_mapping.get(from_city, [])
    if not all_destinations:
        return {'fromCity': from_city, 'date': date, 'destinations': []}

    destinations = all_destinations[:MAX_DESTINATIONS]

    try:
        results = asyncio.run(
            asyncio.wait_for(
                _batch_query_async(from_city, date, destinations),
                timeout=OVERALL_TIMEOUT
            )
        )
    except asyncio.TimeoutError:
        print(f'批量查询总体超时({OVERALL_TIMEOUT}s)，返回已获取的结果')
        results = []
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            results = loop.run_until_complete(
                asyncio.wait_for(
                    _batch_query_async(from_city, date, destinations),
                    timeout=OVERALL_TIMEOUT
                )
            )
        except asyncio.TimeoutError:
            print(f'批量查询总体超时({OVERALL_TIMEOUT}s)，返回已获取的结果')
            results = []
        finally:
            loop.close()

    aggregated = _aggregate_results(from_city, date, results)
    _set_cache(cache_key, aggregated)
    return aggregated
