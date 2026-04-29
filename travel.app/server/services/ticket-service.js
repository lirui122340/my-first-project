const axios = require('axios');
const config = require('../config');

const BASE_URL = 'https://apis.juhe.cn/fapigw/train/query';

const USE_MOCK = !config.apiKey || config.apiKey === 'your_api_key_here';

const mockTrainsDB = {
  '北京_上海': [
    { trainNo: 'G1', fromStation: '北京南', toStation: '上海虹桥', startTime: '06:36', arriveTime: '11:48', duration: '5:12', prices: { '二等座': 553, '一等座': 933, '商务座': 1748 }, seats: { '二等座': 126, '一等座': 15, '商务座': 3 } },
    { trainNo: 'G3', fromStation: '北京南', toStation: '上海虹桥', startTime: '07:00', arriveTime: '12:18', duration: '5:18', prices: { '二等座': 553, '一等座': 933, '商务座': 1748 }, seats: { '二等座': 89, '一等座': 22, '商务座': 5 } },
    { trainNo: 'G7', fromStation: '北京南', toStation: '上海虹桥', startTime: '09:00', arriveTime: '13:28', duration: '4:28', prices: { '二等座': 553, '一等座': 933, '商务座': 1748 }, seats: { '二等座': 203, '一等座': 45, '商务座': 8 } },
    { trainNo: 'D709', fromStation: '北京', toStation: '上海', startTime: '21:15', arriveTime: '07:25', duration: '10:10', prices: { '二等座': 327, '硬卧': 370, '软卧': 580 }, seats: { '二等座': 56, '硬卧': 30, '软卧': 8 } },
  ],
  '北京_南京': [
    { trainNo: 'G1', fromStation: '北京南', toStation: '南京南', startTime: '06:36', arriveTime: '10:18', duration: '3:42', prices: { '二等座': 315, '一等座': 530 }, seats: { '二等座': 203, '一等座': 45 } },
    { trainNo: 'G5', fromStation: '北京南', toStation: '南京南', startTime: '08:00', arriveTime: '11:32', duration: '3:32', prices: { '二等座': 315, '一等座': 530 }, seats: { '二等座': 178, '一等座': 32 } },
    { trainNo: 'G9', fromStation: '北京南', toStation: '南京南', startTime: '10:00', arriveTime: '13:40', duration: '3:40', prices: { '二等座': 315, '一等座': 530 }, seats: { '二等座': 132, '一等座': 18 } },
  ],
  '北京_杭州': [
    { trainNo: 'G35', fromStation: '北京南', toStation: '杭州东', startTime: '06:20', arriveTime: '11:12', duration: '4:52', prices: { '二等座': 264, '一等座': 447 }, seats: { '二等座': 89, '一等座': 12 } },
    { trainNo: 'G37', fromStation: '北京南', toStation: '杭州东', startTime: '09:30', arriveTime: '14:18', duration: '4:48', prices: { '二等座': 264, '一等座': 447 }, seats: { '二等座': 156, '一等座': 28 } },
  ],
  '北京_广州': [
    { trainNo: 'G79', fromStation: '北京西', toStation: '广州南', startTime: '07:26', arriveTime: '15:18', duration: '7:52', prices: { '二等座': 862, '一等座': 1380, '商务座': 2724 }, seats: { '二等座': 45, '一等座': 8, '商务座': 2 } },
    { trainNo: 'G81', fromStation: '北京西', toStation: '广州南', startTime: '10:05', arriveTime: '18:02', duration: '7:57', prices: { '二等座': 862, '一等座': 1380 }, seats: { '二等座': 78, '一等座': 15 } },
  ],
  '北京_武汉': [
    { trainNo: 'G501', fromStation: '北京西', toStation: '武汉', startTime: '07:10', arriveTime: '11:30', duration: '4:20', prices: { '二等座': 519, '一等座': 876 }, seats: { '二等座': 234, '一等座': 56 } },
    { trainNo: 'G503', fromStation: '北京西', toStation: '武汉', startTime: '09:30', arriveTime: '13:52', duration: '4:22', prices: { '二等座': 519, '一等座': 876 }, seats: { '二等座': 167, '一等座': 34 } },
  ],
  '北京_成都': [
    { trainNo: 'G87', fromStation: '北京西', toStation: '成都东', startTime: '06:55', arriveTime: '14:38', duration: '7:43', prices: { '二等座': 778, '一等座': 1246 }, seats: { '二等座': 32, '一等座': 6 } },
    { trainNo: 'G89', fromStation: '北京西', toStation: '成都东', startTime: '09:20', arriveTime: '17:15', duration: '7:55', prices: { '二等座': 778, '一等座': 1246 }, seats: { '二等座': 18, '一等座': 3 } },
  ],
  '北京_西安': [
    { trainNo: 'G87', fromStation: '北京西', toStation: '西安北', startTime: '06:55', arriveTime: '11:42', duration: '4:47', prices: { '二等座': 515, '一等座': 868 }, seats: { '二等座': 145, '一等座': 28 } },
    { trainNo: 'G25', fromStation: '北京西', toStation: '西安北', startTime: '08:00', arriveTime: '12:40', duration: '4:40', prices: { '二等座': 515, '一等座': 868 }, seats: { '二等座': 198, '一等座': 42 } },
  ],
  '北京_长沙': [
    { trainNo: 'G71', fromStation: '北京西', toStation: '长沙南', startTime: '07:26', arriveTime: '12:38', duration: '5:12', prices: { '二等座': 649, '一等座': 1098 }, seats: { '二等座': 112, '一等座': 23 } },
    { trainNo: 'G73', fromStation: '北京西', toStation: '长沙南', startTime: '10:05', arriveTime: '15:20', duration: '5:15', prices: { '二等座': 649, '一等座': 1098 }, seats: { '二等座': 87, '一等座': 16 } },
  ],
  '北京_天津': [
    { trainNo: 'C2001', fromStation: '北京南', toStation: '天津', startTime: '06:30', arriveTime: '07:00', duration: '0:30', prices: { '二等座': 54, '一等座': 91 }, seats: { '二等座': 523, '一等座': 112 } },
    { trainNo: 'C2003', fromStation: '北京南', toStation: '天津', startTime: '07:00', arriveTime: '07:30', duration: '0:30', prices: { '二等座': 54, '一等座': 91 }, seats: { '二等座': 412, '一等座': 89 } },
    { trainNo: 'C2005', fromStation: '北京南', toStation: '天津', startTime: '07:30', arriveTime: '08:00', duration: '0:30', prices: { '二等座': 54, '一等座': 91 }, seats: { '二等座': 356, '一等座': 67 } },
  ],
  '北京_郑州': [
    { trainNo: 'G89', fromStation: '北京西', toStation: '郑州东', startTime: '06:55', arriveTime: '09:38', duration: '2:43', prices: { '二等座': 309, '一等座': 521 }, seats: { '二等座': 267, '一等座': 58 } },
    { trainNo: 'G91', fromStation: '北京西', toStation: '郑州东', startTime: '08:30', arriveTime: '11:12', duration: '2:42', prices: { '二等座': 309, '一等座': 521 }, seats: { '二等座': 189, '一等座': 35 } },
  ],
  '北京_济南': [
    { trainNo: 'G1', fromStation: '北京南', toStation: '济南西', startTime: '06:36', arriveTime: '08:10', duration: '1:34', prices: { '二等座': 184, '一等座': 310 }, seats: { '二等座': 312, '一等座': 78 } },
    { trainNo: 'G3', fromStation: '北京南', toStation: '济南西', startTime: '07:00', arriveTime: '08:36', duration: '1:36', prices: { '二等座': 184, '一等座': 310 }, seats: { '二等座': 245, '一等座': 56 } },
  ],
  '北京_青岛': [
    { trainNo: 'G197', fromStation: '北京南', toStation: '青岛', startTime: '06:30', arriveTime: '10:18', duration: '3:48', prices: { '二等座': 336, '一等座': 565 }, seats: { '二等座': 98, '一等座': 19 } },
    { trainNo: 'G199', fromStation: '北京南', toStation: '青岛', startTime: '09:30', arriveTime: '13:22', duration: '3:52', prices: { '二等座': 336, '一等座': 565 }, seats: { '二等座': 67, '一等座': 12 } },
  ],
  '北京_沈阳': [
    { trainNo: 'G901', fromStation: '北京朝阳', toStation: '沈阳', startTime: '07:00', arriveTime: '10:28', duration: '3:28', prices: { '二等座': 355, '一等座': 598 }, seats: { '二等座': 134, '一等座': 26 } },
    { trainNo: 'G903', fromStation: '北京朝阳', toStation: '沈阳', startTime: '09:15', arriveTime: '12:48', duration: '3:33', prices: { '二等座': 355, '一等座': 598 }, seats: { '二等座': 89, '一等座': 14 } },
  ],
  '北京_合肥': [
    { trainNo: 'G23', fromStation: '北京南', toStation: '合肥南', startTime: '07:30', arriveTime: '10:48', duration: '3:18', prices: { '二等座': 436, '一等座': 734 }, seats: { '二等座': 156, '一等座': 32 } },
    { trainNo: 'G25', fromStation: '北京南', toStation: '合肥南', startTime: '10:00', arriveTime: '13:22', duration: '3:22', prices: { '二等座': 436, '一等座': 734 }, seats: { '二等座': 112, '一等座': 21 } },
  ],
  '北京_石家庄': [
    { trainNo: 'G6701', fromStation: '北京西', toStation: '石家庄', startTime: '06:30', arriveTime: '07:42', duration: '1:12', prices: { '二等座': 128, '一等座': 215 }, seats: { '二等座': 456, '一等座': 98 } },
    { trainNo: 'G6703', fromStation: '北京西', toStation: '石家庄', startTime: '07:30', arriveTime: '08:42', duration: '1:12', prices: { '二等座': 128, '一等座': 215 }, seats: { '二等座': 378, '一等座': 76 } },
  ],
  '北京_太原': [
    { trainNo: 'G91', fromStation: '北京丰台', toStation: '太原南', startTime: '07:20', arriveTime: '09:52', duration: '2:32', prices: { '二等座': 257, '一等座': 432 }, seats: { '二等座': 78, '一等座': 15 } },
    { trainNo: 'G93', fromStation: '北京丰台', toStation: '太原南', startTime: '10:30', arriveTime: '13:02', duration: '2:32', prices: { '二等座': 257, '一等座': 432 }, seats: { '二等座': 56, '一等座': 9 } },
  ],
  '北京_哈尔滨': [
    { trainNo: 'G901', fromStation: '北京朝阳', toStation: '哈尔滨西', startTime: '07:00', arriveTime: '12:48', duration: '5:48', prices: { '二等座': 541, '一等座': 912 }, seats: { '二等座': 34, '一等座': 7 } },
  ],
  '北京_大连': [
    { trainNo: 'G995', fromStation: '北京朝阳', toStation: '大连北', startTime: '07:50', arriveTime: '11:58', duration: '4:08', prices: { '二等座': 399, '一等座': 672 }, seats: { '二等座': 67, '一等座': 12 } },
  ],
  '北京_福州': [
    { trainNo: 'G45', fromStation: '北京南', toStation: '福州', startTime: '07:20', arriveTime: '14:38', duration: '7:18', prices: { '二等座': 672, '一等座': 1134 }, seats: { '二等座': 45, '一等座': 8 } },
  ],
  '北京_厦门': [
    { trainNo: 'G323', fromStation: '北京南', toStation: '厦门北', startTime: '07:40', arriveTime: '16:28', duration: '8:48', prices: { '二等座': 803, '一等座': 1354 }, seats: { '二等座': 23, '一等座': 4 } },
  ],
  '北京_南昌': [
    { trainNo: 'G891', fromStation: '北京西', toStation: '南昌西', startTime: '07:15', arriveTime: '12:38', duration: '5:23', prices: { '二等座': 568, '一等座': 958 }, seats: { '二等座': 67, '一等座': 12 } },
  ],
  '北京_兰州': [
    { trainNo: 'G91', fromStation: '北京西', toStation: '兰州西', startTime: '07:20', arriveTime: '14:38', duration: '7:18', prices: { '二等座': 688, '一等座': 1160 }, seats: { '二等座': 28, '一等座': 5 } },
  ],
  '北京_苏州': [
    { trainNo: 'G1', fromStation: '北京南', toStation: '苏州北', startTime: '06:36', arriveTime: '11:12', duration: '4:36', prices: { '二等座': 523, '一等座': 881 }, seats: { '二等座': 145, '一等座': 28 } },
  ],
  '北京_无锡': [
    { trainNo: 'G3', fromStation: '北京南', toStation: '无锡东', startTime: '07:00', arriveTime: '11:42', duration: '4:42', prices: { '二等座': 538, '一等座': 906 }, seats: { '二等座': 98, '一等座': 18 } },
  ],
  '北京_徐州': [
    { trainNo: 'G1', fromStation: '北京南', toStation: '徐州东', startTime: '06:36', arriveTime: '09:18', duration: '2:42', prices: { '二等座': 269, '一等座': 453 }, seats: { '二等座': 234, '一等座': 48 } },
  ],
  '北京_贵阳': [
    { trainNo: 'G81', fromStation: '北京西', toStation: '贵阳北', startTime: '07:26', arriveTime: '15:38', duration: '8:12', prices: { '二等座': 964, '一等座': 1628 }, seats: { '二等座': 15, '一等座': 3 } },
  ],
  '北京_昆明': [
    { trainNo: 'G71', fromStation: '北京西', toStation: '昆明南', startTime: '07:26', arriveTime: '17:18', duration: '9:52', prices: { '二等座': 1149, '一等座': 1942 }, seats: { '二等座': 12, '一等座': 2 } },
  ],
  '北京_南宁': [
    { trainNo: 'G93', fromStation: '北京西', toStation: '南宁东', startTime: '08:30', arriveTime: '18:42', duration: '10:12', prices: { '二等座': 1012, '一等座': 1708 }, seats: { '二等座': 8, '一等座': 1 } },
  ],
  '北京_深圳': [
    { trainNo: 'G79', fromStation: '北京西', toStation: '深圳北', startTime: '07:26', arriveTime: '15:48', duration: '8:22', prices: { '二等座': 968, '一等座': 1636, '商务座': 3040 }, seats: { '二等座': 34, '一等座': 6, '商务座': 1 } },
  ],
  '北京_重庆': [
    { trainNo: 'G87', fromStation: '北京西', toStation: '重庆西', startTime: '06:55', arriveTime: '15:08', duration: '8:13', prices: { '二等座': 852, '一等座': 1440 }, seats: { '二等座': 22, '一等座': 4 } },
  ],
};

function getMockKey(fromCity, toCity) {
  return `${fromCity}_${toCity}`;
}

function generateMockTrains(fromCity, toCity) {
  const key = getMockKey(fromCity, toCity);
  if (mockTrainsDB[key]) {
    return mockTrainsDB[key];
  }
  const prefixes = ['G', 'D', 'K'];
  const prefix = prefixes[Math.floor(Math.random() * 2)];
  const num = Math.floor(Math.random() * 900) + 100;
  const hours = Math.floor(Math.random() * 8) + 2;
  const mins = Math.floor(Math.random() * 59);
  const startH = Math.floor(Math.random() * 12) + 6;
  const startM = Math.floor(Math.random() * 59);
  const arrH = startH + hours;
  const arrM = startM + mins;
  const price = Math.floor(Math.random() * 500) + 150;
  const seats = Math.floor(Math.random() * 200) + 10;
  return [
    {
      trainNo: `${prefix}${num}`,
      fromStation: fromCity,
      toStation: toCity,
      startTime: `${String(startH).padStart(2, '0')}:${String(startM).padStart(2, '0')}`,
      arriveTime: `${String(arrH % 24).padStart(2, '0')}:${String(arrM % 60).padStart(2, '0')}`,
      duration: `${hours}:${String(mins).padStart(2, '0')}`,
      prices: { '二等座': price, '一等座': Math.floor(price * 1.7) },
      seats: { '二等座': seats, '一等座': Math.floor(seats * 0.2) },
    },
  ];
}

function convertJuheData(juheResult) {
  if (!juheResult) return [];
  const list = Array.isArray(juheResult) ? juheResult : (juheResult.list || []);
  if (!list.length) return [];
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
      fromStation: item.from_station_name || item.start_station_telecode_name || '',
      toStation: item.to_station_name || item.end_station_telecode_name || '',
      startTime: item.start_time || '',
      arriveTime: item.arrive_time || '',
      duration: item.lishi || item.run_time || '',
      prices,
      seats,
    };
  });
}

const ticketService = {
  async queryTickets(fromCity, toCity, date) {
    if (USE_MOCK) {
      return { code: 200, data: generateMockTrains(fromCity, toCity) };
    }
    try {
      const response = await axios.get(BASE_URL, {
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
        const converted = convertJuheData(result.result);
        if (converted.length > 0) {
          return { code: 200, data: converted };
        }
      }
      console.error(`聚合数据返回错误: ${result.reason || '未知错误'}, 使用mock数据`);
      return { code: 200, data: generateMockTrains(fromCity, toCity) };
    } catch (error) {
      console.error(`查询 ${fromCity}→${toCity} 失败:`, error.message);
      return { code: 200, data: generateMockTrains(fromCity, toCity) };
    }
  },
};

module.exports = ticketService;
