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
      wx.showToast({ title: '查询失败，请重试', icon: 'none' });
    } finally {
      this.setData({ loading: false });
      wx.hideLoading();
    }
  },

  onSortChange(e) {
    const sortBy = e.currentTarget.dataset.sort;
    if (sortBy === this.data.sortBy) return;
    this.setData({ sortBy });
    const sorted = [...this.data.destinations];
    if (sortBy === 'price') {
      sorted.sort((a, b) => {
        if (a.minPrice === 0 && b.minPrice === 0) return b.totalSeats - a.totalSeats;
        if (a.minPrice === 0) return 1;
        if (b.minPrice === 0) return -1;
        return a.minPrice - b.minPrice;
      });
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
