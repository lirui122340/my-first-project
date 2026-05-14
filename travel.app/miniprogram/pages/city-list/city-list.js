const http = require('../../utils/request');

Page({
  data: {
    fromCity: '',
    date: '',
    destinations: [],
    loading: true,
  },

  onLoad(options) {
    const fromCity = decodeURIComponent(options.fromCity || '');
    const date = options.date || '';
    this.setData({ fromCity, date });
    wx.setNavigationBarTitle({ title: `${fromCity}出发` });
    this.fetchDestinations();
  },

  async fetchDestinations() {
    wx.showLoading({ title: '加载中...' });
    try {
      const data = await http.get('/ticket/quick-destinations', {
        from_city: this.data.fromCity,
      });
      this.setData({ destinations: data.destinations || [] });
    } catch (err) {
      wx.showToast({ title: '加载失败，请重试', icon: 'none' });
    } finally {
      this.setData({ loading: false });
      wx.hideLoading();
    }
  },

  onCityTap(e) {
    const city = e.currentTarget.dataset.city;
    wx.navigateTo({
      url: `/pages/ticket-list/ticket-list?fromCity=${encodeURIComponent(this.data.fromCity)}&toCity=${encodeURIComponent(city)}&date=${this.data.date}`,
    });
  },

  onHostelTap(e) {
    const city = e.currentTarget.dataset.city;
    wx.navigateTo({
      url: `/pages/hostel-list/hostel-list?city=${encodeURIComponent(city)}`,
    });
  },

  onRefresh() {
    this.setData({ loading: true, destinations: [] });
    this.fetchDestinations();
  },
});
