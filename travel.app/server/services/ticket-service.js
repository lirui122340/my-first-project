const axios = require('axios');
const config = require('../config');
const { fetchStationData, getCodeToNameMap } = require('./station-service');

const JUHE_URL = 'https://apis.juhe.cn/fapigw/train/query';
const API_12306_BASE = 'https://kyfw.12306.cn/otn/leftTicket/';
const INIT_URL = 'https://kyfw.12306.cn/otn/leftTicket/init';

const USE_JUHE = config.apiKey && config.apiKey !== 'your_api_key_here';

const SEAT_NAMES = {
  swz: '商务座',
  zy: '一等座',
  ze: '二等座',
  rw: '软卧',
  yw: '硬卧',
  yz: '硬座',
  wz: '无座',
  gr: '高级软卧',
  tz: '特等座',
  srrb: '动卧',
};

const SEAT_POSITIONS = {
  swz: 32,
  tz: 25,
  zy: 31,
  ze: 30,
  gr: 21,
  rw: 23,
  yw: 28,
  yz: 29,
  wz: 26,
  srrb: 33,
};

const PRICE_RATES = {
  G: { '商务座': 1.45, '特等座': 1.10, '一等座': 0.77, '二等座': 0.46, '无座': 0.46 },
  D: { '一等座': 0.37, '二等座': 0.31, '动卧': 0.55, '软卧': 0.45, '硬卧': 0.30, '无座': 0.31 },
  C: { '一等座': 0.37, '二等座': 0.31, '无座': 0.31 },
  Z: { '高级软卧': 0.65, '软卧': 0.33, '硬卧': 0.21, '硬座': 0.12, '无座': 0.12 },
  T: { '高级软卧': 0.65, '软卧': 0.33, '硬卧': 0.21, '硬座': 0.12, '无座': 0.12 },
  K: { '高级软卧': 0.65, '软卧': 0.33, '硬卧': 0.21, '硬座': 0.12, '无座': 0.12 },
};

const AVG_SPEED = {
  G: 250,
  D: 160,
  C: 140,
  Z: 90,
  T: 85,
  K: 75,
};

const KNOWN_PRICES = {
  '北京南_上海虹桥': { '二等座': 553, '一等座': 933, '商务座': 1748 },
  '北京南_南京南': { '二等座': 315, '一等座': 530, '商务座': 996 },
  '北京南_杭州东': { '二等座': 264, '一等座': 447, '商务座': 838 },
  '北京西_广州南': { '二等座': 862, '一等座': 1380, '商务座': 2724 },
  '北京西_武汉': { '二等座': 519, '一等座': 876, '商务座': 1643 },
  '北京西_成都东': { '二等座': 778, '一等座': 1246, '商务座': 2417 },
  '北京西_西安北': { '二等座': 515, '一等座': 868, '商务座': 1627 },
  '北京南_天津': { '二等座': 54, '一等座': 91 },
  '北京西_郑州东': { '二等座': 309, '一等座': 521, '商务座': 977 },
  '北京南_济南西': { '二等座': 184, '一等座': 310, '商务座': 580 },
  '北京南_青岛': { '二等座': 336, '一等座': 565, '商务座': 1058 },
  '北京朝阳_沈阳': { '二等座': 355, '一等座': 598, '商务座': 1120 },
  '北京西_长沙南': { '二等座': 649, '一等座': 1098, '商务座': 2057 },
  '北京西_石家庄': { '二等座': 128, '一等座': 215 },
  '北京丰台_太原南': { '二等座': 257, '一等座': 432 },
  '北京南_合肥南': { '二等座': 436, '一等座': 734, '商务座': 1375 },
  '上海虹桥_南京南': { '二等座': 134, '一等座': 229, '商务座': 428 },
  '上海虹桥_杭州东': { '二等座': 73, '一等座': 124, '商务座': 232 },
  '上海_北京南': { '二等座': 553, '一等座': 933, '商务座': 1748 },
  '广州南_长沙南': { '二等座': 314, '一等座': 528, '商务座': 996 },
  '广州南_武汉': { '二等座': 463, '一等座': 738, '商务座': 1458 },
  '成都东_重庆西': { '二等座': 154, '一等座': 256 },
  '西安北_郑州东': { '二等座': 259, '一等座': 437, '商务座': 819 },
};

function parseSeatInfo(resultStr) {
  const parts = resultStr.split('|');
  const seats = {};

  for (const [key, pos] of Object.entries(SEAT_POSITIONS)) {
    if (pos < parts.length) {
      const val = parts[pos];
      if (val && val !== '' && val !== '*') {
        const name = SEAT_NAMES[key] || key;
        const num = parseInt(val);
        seats[name] = isNaN(num) ? val : num;
      }
    }
  }

  return seats;
}

function parseDuration(duration) {
  if (!duration) return 0;
  const parts = duration.split(':');
  if (parts.length < 2) return 0;
  return parseInt(parts[0]) + parseInt(parts[1]) / 60;
}

function estimateDistance(durationHours, trainPrefix) {
  const speed = AVG_SPEED[trainPrefix] || 100;
  return durationHours * speed;
}

function estimatePrices(train) {
  const prefix = train.trainNo.charAt(0);
  const rates = PRICE_RATES[prefix];
  if (!rates) return {};

  const key = `${train.fromStation}_${train.toStation}`;
  const knownPrice = KNOWN_PRICES[key];

  if (knownPrice && prefix === 'G') {
    const prices = {};
    for (const [seatType, count] of Object.entries(train.seats)) {
      if (knownPrice[seatType]) {
        prices[seatType] = knownPrice[seatType];
      }
    }
    return prices;
  }

  const reverseKey = `${train.toStation}_${train.fromStation}`;
  const reverseKnown = KNOWN_PRICES[reverseKey];
  if (reverseKnown && prefix === 'G') {
    const prices = {};
    for (const [seatType, count] of Object.entries(train.seats)) {
      if (reverseKnown[seatType]) {
        prices[seatType] = reverseKnown[seatType];
      }
    }
    return prices;
  }

  const durationHours = parseDuration(train.duration);
  if (durationHours <= 0) return {};

  const distance = estimateDistance(durationHours, prefix);
  const prices = {};

  for (const [seatType, count] of Object.entries(train.seats)) {
    if (rates[seatType]) {
      prices[seatType] = Math.round(distance * rates[seatType]);
    }
  }

  return prices;
}

function parse12306Response(data) {
  if (!data || !data.result || !Array.isArray(data.result)) {
    return [];
  }

  const codeToName = getCodeToNameMap();

  return data.result.map((resultStr) => {
    const parts = resultStr.split('|');
    const seats = parseSeatInfo(resultStr);

    const fromCode = parts[6] || '';
    const toCode = parts[7] || '';

    const train = {
      trainNo: parts[3] || '',
      fromStation: codeToName[fromCode] || fromCode,
      toStation: codeToName[toCode] || toCode,
      startTime: parts[8] || '',
      arriveTime: parts[9] || '',
      duration: parts[10] || '',
      seats,
      prices: {},
    };

    train.prices = estimatePrices(train);

    return train;
  }).filter((train) => train.trainNo !== '');
}

let cachedCookies = null;
let cookieTimestamp = 0;
const COOKIE_TTL = 5 * 60 * 1000;

async function get12306Cookies() {
  const now = Date.now();
  if (cachedCookies && now - cookieTimestamp < COOKIE_TTL) {
    return cachedCookies;
  }

  try {
    const response = await axios.get(INIT_URL, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
      },
      timeout: 15000,
    });

    const setCookies = response.headers['set-cookie'];
    if (setCookies) {
      const cookies = setCookies.map((c) => c.split(';')[0]).join('; ');
      cachedCookies = cookies;
      cookieTimestamp = now;
      console.log('获取12306 Cookie成功');
      return cookies;
    }

    return '';
  } catch (error) {
    console.error('获取12306 Cookie失败:', error.message);
    return '';
  }
}

const QUERY_ENDPOINTS = ['queryZ', 'queryA', 'queryG', 'query'];

async function query12306(fromCity, toCity, date) {
  const stationMap = await fetchStationData();

  const fromCode = stationMap[fromCity];
  const toCode = stationMap[toCity];

  if (!fromCode) {
    console.error(`未找到出发城市站点代码: ${fromCity}`);
    return null;
  }
  if (!toCode) {
    console.error(`未找到目的城市站点代码: ${toCity}`);
    return null;
  }

  const cookies = await get12306Cookies();

  for (const endpoint of QUERY_ENDPOINTS) {
    try {
      const url = `${API_12306_BASE}${endpoint}`;
      const response = await axios.get(url, {
        params: {
          'leftTicketDTO.train_date': date,
          'leftTicketDTO.from_station': fromCode,
          'leftTicketDTO.to_station': toCode,
          'purpose_codes': 'ADULT',
        },
        headers: {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
          'Accept': '*/*',
          'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
          'Referer': 'https://kyfw.12306.cn/otn/leftTicket/init',
          'Cookie': cookies,
          'X-Requested-With': 'XMLHttpRequest',
        },
        timeout: 15000,
      });

      if (response.data && response.data.httpstatus === 200 && response.data.data && response.data.data.result) {
        const trains = parse12306Response(response.data.data);
        console.log(`12306查询成功(${endpoint}): ${fromCity}→${toCity} ${date}, 共${trains.length}趟车次`);
        return trains;
      }

      if (response.data && response.data.status === false && response.data.c_url) {
        const redirectUrl = response.data.c_url;
        try {
          const redirectResponse = await axios.get(`${API_12306_BASE}${redirectUrl}`, {
            params: {
              'leftTicketDTO.train_date': date,
              'leftTicketDTO.from_station': fromCode,
              'leftTicketDTO.to_station': toCode,
              'purpose_codes': 'ADULT',
            },
            headers: {
              'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
              'Accept': '*/*',
              'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
              'Referer': 'https://kyfw.12306.cn/otn/leftTicket/init',
              'Cookie': cookies,
              'X-Requested-With': 'XMLHttpRequest',
            },
            timeout: 15000,
          });

          if (redirectResponse.data && redirectResponse.data.httpstatus === 200 && redirectResponse.data.data && redirectResponse.data.data.result) {
            const trains = parse12306Response(redirectResponse.data.data);
            console.log(`12306重定向查询成功(${redirectUrl}): ${fromCity}→${toCity} ${date}, 共${trains.length}趟车次`);
            return trains;
          }
        } catch (redirectErr) {
          console.error(`12306重定向请求失败:`, redirectErr.message);
        }
      }
    } catch (error) {
      if (error.response && error.response.status !== 404) {
        console.error(`12306端点${endpoint}请求失败:`, error.message);
      }
    }
  }

  console.error('所有12306查询端点均失败');
  return null;
}

async function queryJuhe(fromCity, toCity, date) {
  if (!USE_JUHE) return null;

  try {
    const response = await axios.get(JUHE_URL, {
      params: {
        start: fromCity,
        end: toCity,
        date: date,
        key: config.apiKey,
      },
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      timeout: 10000,
    });
    const result = response.data;
    if (result.error_code === 0 && result.result) {
      const list = Array.isArray(result.result) ? result.result : (result.result.list || []);
      if (list.length > 0) {
        return list.map((item) => {
          const prices = {};
          const seats = {};
          if (item.items && Array.isArray(item.items)) {
            item.items.forEach((seat) => {
              if (seat.name && seat.price) {
                prices[seat.name] = parseInt(seat.price) || 0;
              }
              if (seat.name && seat.number !== undefined) {
                seats[seat.name] = seat.number === '' ? '有' : (parseInt(seat.number) || 0);
              }
            });
          }
          return {
            trainNo: item.train_no || item.station_train_code || '',
            fromStation: item.from_station_name || '',
            toStation: item.to_station_name || '',
            startTime: item.start_time || '',
            arriveTime: item.arrive_time || '',
            duration: item.lishi || item.run_time || '',
            prices,
            seats,
          };
        });
      }
    }
    console.error(`聚合数据返回错误: ${result.reason || '未知错误'}`);
    return null;
  } catch (error) {
    console.error(`聚合数据查询失败: ${fromCity}→${toCity}`, error.message);
    return null;
  }
}

const ticketService = {
  async queryTickets(fromCity, toCity, date) {
    const trains12306 = await query12306(fromCity, toCity, date);
    if (trains12306 && trains12306.length > 0) {
      return { code: 200, data: trains12306 };
    }

    const trainsJuhe = await queryJuhe(fromCity, toCity, date);
    if (trainsJuhe && trainsJuhe.length > 0) {
      return { code: 200, data: trainsJuhe };
    }

    return { code: 200, data: [] };
  },

  async queryTicketsWithPrices(fromCity, toCity, date) {
    return await this.queryTickets(fromCity, toCity, date);
  },
};

module.exports = ticketService;
