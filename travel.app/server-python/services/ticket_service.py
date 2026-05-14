import time
import requests
import config
from services.station_service import fetch_station_data, get_code_to_name_map

JUHE_URL = 'https://apis.juhe.cn/fapigw/train/query'
API_12306_BASE = 'https://kyfw.12306.cn/otn/leftTicket/'
INIT_URL = 'https://kyfw.12306.cn/otn/leftTicket/init'

USE_JUHE = bool(config.API_KEY and config.API_KEY != 'your_api_key_here')

SEAT_NAMES = {
    'swz': '商务座',
    'zy': '一等座',
    'ze': '二等座',
    'rw': '软卧',
    'yw': '硬卧',
    'yz': '硬座',
    'wz': '无座',
    'gr': '高级软卧',
    'tz': '特等座',
    'srrb': '动卧',
}

SEAT_POSITIONS = {
    'swz': 32,
    'tz': 25,
    'zy': 31,
    'ze': 30,
    'gr': 21,
    'rw': 23,
    'yw': 28,
    'yz': 29,
    'wz': 26,
    'srrb': 33,
}

PRICE_RATES = {
    'G': {'商务座': 1.45, '特等座': 1.10, '一等座': 0.77, '二等座': 0.46, '无座': 0.46},
    'D': {'一等座': 0.37, '二等座': 0.31, '动卧': 0.55, '软卧': 0.45, '硬卧': 0.30, '无座': 0.31},
    'C': {'一等座': 0.37, '二等座': 0.31, '无座': 0.31},
    'Z': {'高级软卧': 0.65, '软卧': 0.33, '硬卧': 0.21, '硬座': 0.12, '无座': 0.12},
    'T': {'高级软卧': 0.65, '软卧': 0.33, '硬卧': 0.21, '硬座': 0.12, '无座': 0.12},
    'K': {'高级软卧': 0.65, '软卧': 0.33, '硬卧': 0.21, '硬座': 0.12, '无座': 0.12},
}

AVG_SPEED = {
    'G': 250,
    'D': 160,
    'C': 140,
    'Z': 90,
    'T': 85,
    'K': 75,
}

KNOWN_PRICES = {
    '北京南_上海虹桥': {'二等座': 553, '一等座': 933, '商务座': 1748},
    '北京南_南京南': {'二等座': 315, '一等座': 530, '商务座': 996},
    '北京南_杭州东': {'二等座': 264, '一等座': 447, '商务座': 838},
    '北京西_广州南': {'二等座': 862, '一等座': 1380, '商务座': 2724},
    '北京西_武汉': {'二等座': 519, '一等座': 876, '商务座': 1643},
    '北京西_成都东': {'二等座': 778, '一等座': 1246, '商务座': 2417},
    '北京西_西安北': {'二等座': 515, '一等座': 868, '商务座': 1627},
    '北京南_天津': {'二等座': 54, '一等座': 91},
    '北京西_郑州东': {'二等座': 309, '一等座': 521, '商务座': 977},
    '北京南_济南西': {'二等座': 184, '一等座': 310, '商务座': 580},
    '北京南_青岛': {'二等座': 336, '一等座': 565, '商务座': 1058},
    '北京朝阳_沈阳': {'二等座': 355, '一等座': 598, '商务座': 1120},
    '北京西_长沙南': {'二等座': 649, '一等座': 1098, '商务座': 2057},
    '北京西_石家庄': {'二等座': 128, '一等座': 215},
    '北京丰台_太原南': {'二等座': 257, '一等座': 432},
    '北京南_合肥南': {'二等座': 436, '一等座': 734, '商务座': 1375},
    '上海虹桥_南京南': {'二等座': 134, '一等座': 229, '商务座': 428},
    '上海虹桥_杭州东': {'二等座': 73, '一等座': 124, '商务座': 232},
    '上海_北京南': {'二等座': 553, '一等座': 933, '商务座': 1748},
    '广州南_长沙南': {'二等座': 314, '一等座': 528, '商务座': 996},
    '广州南_武汉': {'二等座': 463, '一等座': 738, '商务座': 1458},
    '成都东_重庆西': {'二等座': 154, '一等座': 256},
    '西安北_郑州东': {'二等座': 259, '一等座': 437, '商务座': 819},
}

_cached_cookies = None
_cookie_timestamp = 0
_COOKIE_TTL = 5 * 60


def _parse_seat_info(result_str):
    parts = result_str.split('|')
    seats = {}

    for key, pos in SEAT_POSITIONS.items():
        if pos < len(parts):
            val = parts[pos]
            if val and val != '' and val != '*':
                name = SEAT_NAMES.get(key, key)
                try:
                    seats[name] = int(val)
                except ValueError:
                    seats[name] = val

    return seats


def _parse_duration(duration):
    if not duration:
        return 0
    parts = duration.split(':')
    if len(parts) < 2:
        return 0
    try:
        return int(parts[0]) + int(parts[1]) / 60
    except ValueError:
        return 0


def _estimate_distance(duration_hours, train_prefix):
    speed = AVG_SPEED.get(train_prefix, 100)
    return duration_hours * speed


def estimate_prices(train):
    prefix = train['trainNo'][0] if train['trainNo'] else ''
    rates = PRICE_RATES.get(prefix)
    if not rates:
        return {}

    key = f"{train['fromStation']}_{train['toStation']}"
    known_price = KNOWN_PRICES.get(key)

    if known_price and prefix == 'G':
        prices = {}
        for seat_type in train['seats']:
            if seat_type in known_price:
                prices[seat_type] = known_price[seat_type]
        return prices

    reverse_key = f"{train['toStation']}_{train['fromStation']}"
    reverse_known = KNOWN_PRICES.get(reverse_key)
    if reverse_known and prefix == 'G':
        prices = {}
        for seat_type in train['seats']:
            if seat_type in reverse_known:
                prices[seat_type] = reverse_known[seat_type]
        return prices

    duration_hours = _parse_duration(train['duration'])
    if duration_hours <= 0:
        return {}

    distance = _estimate_distance(duration_hours, prefix)
    prices = {}

    for seat_type in train['seats']:
        if seat_type in rates:
            prices[seat_type] = round(distance * rates[seat_type])

    return prices


def _parse_12306_response(data):
    if not data or 'result' not in data or not isinstance(data['result'], list):
        return []

    code_to_name = get_code_to_name_map()

    trains = []
    for result_str in data['result']:
        parts = result_str.split('|')
        seats = _parse_seat_info(result_str)

        from_code = parts[6] if len(parts) > 6 else ''
        to_code = parts[7] if len(parts) > 7 else ''

        train = {
            'trainNo': parts[3] if len(parts) > 3 else '',
            'fromStation': code_to_name.get(from_code, from_code),
            'toStation': code_to_name.get(to_code, to_code),
            'startTime': parts[8] if len(parts) > 8 else '',
            'arriveTime': parts[9] if len(parts) > 9 else '',
            'duration': parts[10] if len(parts) > 10 else '',
            'seats': seats,
            'prices': {},
        }

        if not train['trainNo']:
            continue

        train['prices'] = estimate_prices(train)
        trains.append(train)

    return trains


def _get_12306_cookies():
    global _cached_cookies, _cookie_timestamp

    now = time.time()
    if _cached_cookies and now - _cookie_timestamp < _COOKIE_TTL:
        return _cached_cookies

    try:
        response = requests.get(INIT_URL, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }, timeout=15)

        cookies_dict = dict(response.cookies)
        if cookies_dict:
            cookies = '; '.join(f'{k}={v}' for k, v in cookies_dict.items())
            _cached_cookies = cookies
            _cookie_timestamp = now
            print('获取12306 Cookie成功')
            return cookies

        return ''
    except Exception as e:
        print(f'获取12306 Cookie失败: {e}')
        return ''


QUERY_ENDPOINTS = ['queryZ', 'queryA', 'queryG', 'query']

_COMMON_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': '*/*',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Referer': 'https://kyfw.12306.cn/otn/leftTicket/init',
    'X-Requested-With': 'XMLHttpRequest',
}


def query_12306(from_city, to_city, date):
    station_map = fetch_station_data()

    from_code = station_map.get(from_city)
    to_code = station_map.get(to_city)

    if not from_code:
        print(f'未找到出发城市站点代码: {from_city}')
        return None
    if not to_code:
        print(f'未找到目的城市站点代码: {to_city}')
        return None

    cookies = _get_12306_cookies()

    for endpoint in QUERY_ENDPOINTS:
        try:
            url = f'{API_12306_BASE}{endpoint}'
            headers = {**_COMMON_HEADERS, 'Cookie': cookies}
            params = {
                'leftTicketDTO.train_date': date,
                'leftTicketDTO.from_station': from_code,
                'leftTicketDTO.to_station': to_code,
                'purpose_codes': 'ADULT',
            }

            response = requests.get(url, params=params, headers=headers, timeout=15)
            data = response.json()

            if (data and data.get('httpstatus') == 200
                    and data.get('data') and data['data'].get('result')):
                trains = _parse_12306_response(data['data'])
                print(f'12306查询成功({endpoint}): {from_city}→{to_city} {date}, 共{len(trains)}趟车次')
                return trains

            if data and data.get('status') is False and data.get('c_url'):
                redirect_url = data['c_url']
                try:
                    redirect_response = requests.get(
                        f'{API_12306_BASE}{redirect_url}',
                        params=params,
                        headers=headers,
                        timeout=15,
                    )
                    redirect_data = redirect_response.json()
                    if (redirect_data and redirect_data.get('httpstatus') == 200
                            and redirect_data.get('data') and redirect_data['data'].get('result')):
                        trains = _parse_12306_response(redirect_data['data'])
                        print(f'12306重定向查询成功({redirect_url}): {from_city}→{to_city} {date}, 共{len(trains)}趟车次')
                        return trains
                except Exception as redirect_err:
                    print(f'12306重定向请求失败: {redirect_err}')
        except Exception as e:
            if hasattr(e, 'response') and e.response is not None and e.response.status_code != 404:
                print(f'12306端点{endpoint}请求失败: {e}')
            elif not hasattr(e, 'response'):
                print(f'12306端点{endpoint}请求失败: {e}')

    print('所有12306查询端点均失败')
    return None


def query_juhe(from_city, to_city, date):
    if not USE_JUHE:
        return None

    try:
        response = requests.get(JUHE_URL, params={
            'start': from_city,
            'end': to_city,
            'date': date,
            'key': config.API_KEY,
        }, headers={
            'Content-Type': 'application/x-www-form-urlencoded',
        }, timeout=10)

        result = response.json()
        if result.get('error_code') == 0 and result.get('result'):
            raw_list = result['result']
            if isinstance(raw_list, dict):
                raw_list = raw_list.get('list', [])
            if not isinstance(raw_list, list):
                raw_list = []

            if raw_list:
                trains = []
                for item in raw_list:
                    prices = {}
                    seats = {}
                    if item.get('items') and isinstance(item['items'], list):
                        for seat in item['items']:
                            if seat.get('name') and seat.get('price'):
                                try:
                                    prices[seat['name']] = int(seat['price'])
                                except (ValueError, TypeError):
                                    pass
                            if seat.get('name') and seat.get('number') is not None:
                                num = seat['number']
                                seats[seat['name']] = '有' if num == '' else (int(num) if str(num).isdigit() else 0)

                    trains.append({
                        'trainNo': item.get('train_no') or item.get('station_train_code', ''),
                        'fromStation': item.get('from_station_name', ''),
                        'toStation': item.get('to_station_name', ''),
                        'startTime': item.get('start_time', ''),
                        'arriveTime': item.get('arrive_time', ''),
                        'duration': item.get('lishi') or item.get('run_time', ''),
                        'prices': prices,
                        'seats': seats,
                    })
                return trains

        print(f"聚合数据返回错误: {result.get('reason', '未知错误')}")
        return None
    except Exception as e:
        print(f'聚合数据查询失败: {from_city}→{to_city} {e}')
        return None


def query_tickets(from_city, to_city, date):
    trains_12306 = query_12306(from_city, to_city, date)
    if trains_12306 and len(trains_12306) > 0:
        return {'code': 200, 'data': trains_12306}

    trains_juhe = query_juhe(from_city, to_city, date)
    if trains_juhe and len(trains_juhe) > 0:
        return {'code': 200, 'data': trains_juhe}

    return {'code': 200, 'data': []}


def query_tickets_with_prices(from_city, to_city, date):
    return query_tickets(from_city, to_city, date)
