import time
import requests

STATION_URL = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js'

_station_map = None
_code_to_name_map = None
_last_fetch_time = 0
_CACHE_DURATION = 24 * 60 * 60

FALLBACK_STATIONS = {
    '北京': 'BJP', '北京南': 'VNP', '北京西': 'BXP', '北京北': 'VAP', '北京东': 'BOP', '北京朝阳': 'VQP',
    '上海': 'SHH', '上海虹桥': 'AOH', '上海南': 'SNH', '上海西': 'SXH',
    '广州': 'GZQ', '广州南': 'IZQ', '广州东': 'GGQ', '广州北': 'GBQ',
    '深圳': 'SZQ', '深圳北': 'IOQ', '深圳东': 'BJQ',
    '成都': 'CDW', '成都东': 'ICW', '成都南': 'CNW',
    '杭州': 'HZH', '杭州东': 'HGH', '杭州南': 'XAH',
    '武汉': 'WHN', '武汉站': 'WHB', '汉口': 'HKN', '武昌': 'WCN',
    '西安': 'XAY', '西安北': 'EAY',
    '南京': 'NJH', '南京南': 'NKH', '南京东': 'NDH',
    '重庆': 'CQW', '重庆北': 'CUW', '重庆西': 'CXW',
    '长沙': 'CSQ', '长沙南': 'CWQ',
    '天津': 'TJP', '天津南': 'TIP', '天津西': 'TXP',
    '郑州': 'ZZF', '郑州东': 'ZAF', '郑州西': 'ZXF',
    '济南': 'JNK', '济南西': 'JGK', '济南东': 'DNK',
    '青岛': 'QDK', '青岛北': 'QHK', '青岛西': 'QXK',
    '沈阳': 'SYT', '沈阳北': 'SBT', '沈阳南': 'SOT',
    '大连': 'DLT', '大连北': 'DFT',
    '哈尔滨': 'HBB', '哈尔滨西': 'VAB', '哈尔滨北': 'VBB',
    '长春': 'CCT', '长春西': 'CRT',
    '石家庄': 'SJP', '石家庄北': 'VVP',
    '太原': 'TYV', '太原南': 'TNV',
    '合肥': 'HFH', '合肥南': 'ENH',
    '福州': 'FZS', '福州南': 'FNS',
    '厦门': 'XMS', '厦门北': 'XKS', '厦门高崎': 'XBS',
    '昆明': 'KMM', '昆明南': 'KOM',
    '贵阳': 'GIW', '贵阳北': 'KNW',
    '南宁': 'NNZ', '南宁东': 'NDZ',
    '兰州': 'LZJ', '兰州西': 'LXJ',
    '银川': 'YCJ',
    '西宁': 'XNO',
    '呼和浩特': 'HHC', '呼和浩特东': 'NDC',
    '乌鲁木齐': 'WAR', '乌鲁木齐南': 'WNR',
    '南昌': 'NXG', '南昌西': 'NXN',
    '苏州': 'SZH', '苏州北': 'OHH', '苏州园区': 'KAH',
    '无锡': 'WXH', '无锡东': 'WTH', '无锡新区': 'WHH',
    '常州': 'CZH', '常州北': 'CBH',
    '徐州': 'XCH', '徐州东': 'XUH',
    '镇江': 'ZJH', '镇江南': 'ZEH',
    '保定': 'BDP', '唐山': 'TSP', '秦皇岛': 'QTP',
    '株洲': 'ZZQ', '洛阳': 'LYF', '开封': 'KFF',
    '桂林': 'GLW', '柳州': 'LZZ',
    '海口': 'HKQ', '珠海': 'ZHQ',
}


def fetch_station_data():
    global _station_map, _code_to_name_map, _last_fetch_time

    now = time.time()
    if _station_map and now - _last_fetch_time < _CACHE_DURATION:
        return _station_map

    try:
        response = requests.get(STATION_URL, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        })
        text = response.text
        matches = text.split('@')
        name_map = {}
        code_map = {}

        for item in matches:
            if not item:
                continue
            parts = item.split('|')
            if len(parts) >= 3:
                name = parts[1]
                code = parts[2]
                if name and code:
                    if name not in name_map:
                        name_map[name] = code
                    code_map[code] = name

        _station_map = name_map
        _code_to_name_map = code_map
        _last_fetch_time = now
        print(f'站点数据加载完成，共 {len(name_map)} 个站点')
        return _station_map
    except Exception as e:
        print(f'获取12306站点数据失败: {e}')
        if _station_map:
            return _station_map
        return FALLBACK_STATIONS


def get_code_to_name_map():
    if _code_to_name_map:
        return _code_to_name_map
    return {}
