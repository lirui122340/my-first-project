const http = require('../../utils/request');

Page({
  data: {
    fromCity: '',
    toCity: '',
    date: '',
    direct: null,
    recommendations: [],
    allTransfers: [],
    loading: true,
    showAll: false,
  },

  onLoad(options) {
    const fromCity = decodeURIComponent(options.fromCity || '');
    const toCity = decodeURIComponent(options.toCity || '');
    const date = options.date || '';
    this.setData({ fromCity, toCity, date });
    wx.setNavigationBarTitle({ title: `${fromCity} → ${toCity} 省钱路线` });
    this.fetchRoutes();
  },

  async fetchRoutes() {
    wx.showLoading({ title: '查询中转路线...' });
    try {
      const data = await http.get('/route/transfer', {
        from_city: this.data.fromCity,
        to_city: this.data.toCity,
        date: this.data.date,
      });
      this.setData({
        direct: data.direct || null,
        recommendations: data.recommendations || [],
        allTransfers: data.transfers || [],
      });
    } catch (err) {
      wx.showToast({ title: '查询失败，请重试', icon: 'none' });
    } finally {
      this.setData({ loading: false });
      wx.hideLoading();
    }
  },

  onToggleShow() {
    this.setData({ showAll: !this.data.showAll });
  },

  onRefresh() {
    this.setData({ loading: true });
    this.fetchRoutes();
  },
});
