const http = require('../../utils/request');

Page({
  data: {
    fromCity: '',
    date: '',
    destinations: [],
    sortBy: 'seats',
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
    wx.showLoading({ title: '查询中...' });
    try {
      const data = await http.get('/ticket/destinations', {
        from_city: this.data.fromCity,
        date: this.data.date,
        sort_by: this.data.sortBy,
      });
      this.setData({ destinations: data.destinations || [] });
    } catch (err) {
      console.error('查询可直达城市失败:', err);
      wx.showToast({ title: '查询失败，请重试', icon: 'none' });
    } finally {
      this.setData({ loading: false });
      wx.hideLoading();
    }
  },

  onSortChange(e) {
    const sortBy = e.currentTarget.dataset.sort;
    this.setData({ sortBy });
    const sorted = [...this.data.destinations];
    if (sortBy === 'price') {
      sorted.sort((a, b) => a.minPrice - b.minPrice);
    } else {
      sorted.sort((a, b) => b.totalSeats - a.totalSeats);
    }
    this.setData({ destinations: sorted });
  },

  onCityTap(e) {
    const city = e.currentTarget.dataset.city;
    wx.navigateTo({
      url: `/pages/ticket-list/ticket-list?fromCity=${encodeURIComponent(this.data.fromCity)}&toCity=${encodeURIComponent(city)}&date=${this.data.date}`,
    });
  },

  onRefresh() {
    this.setData({ loading: true, destinations: [] });
    this.fetchDestinations();
  },
});
