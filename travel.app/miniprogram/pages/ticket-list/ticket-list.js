const http = require('../../utils/request');

Page({
  data: {
    fromCity: '',
    toCity: '',
    date: '',
    fromStation: '',
    toStation: '',
    tickets: [],
    trainType: 'all',
    loading: true,
  },

  onLoad(options) {
    const fromCity = decodeURIComponent(options.fromCity || '');
    const toCity = decodeURIComponent(options.toCity || '');
    const date = options.date || '';
    this.setData({ fromCity, toCity, date });
    wx.setNavigationBarTitle({ title: `${fromCity} → ${toCity}` });
    this.fetchTrains();
  },

  async fetchTrains() {
    wx.showLoading({ title: '查询中...' });
    try {
      const data = await http.get('/ticket/trains', {
        from_city: this.data.fromCity,
        to_city: this.data.toCity,
        date: this.data.date,
        train_type: this.data.trainType,
      });
      this.setData({
        tickets: data.tickets || [],
        fromStation: data.fromStation || '',
        toStation: data.toStation || '',
      });
    } catch (err) {
      console.error('查询车次详情失败:', err);
      wx.showToast({ title: '查询失败，请重试', icon: 'none' });
    } finally {
      this.setData({ loading: false });
      wx.hideLoading();
    }
  },

  onTrainTypeChange(e) {
    const trainType = e.currentTarget.dataset.type;
    this.setData({ trainType, loading: true });
    this.fetchTrains();
  },
});
