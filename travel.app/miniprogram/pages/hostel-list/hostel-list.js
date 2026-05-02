const http = require('../../utils/request');

Page({
  data: {
    city: '',
    avgPrice: 0,
    hostels: [],
    sortBy: 'price',
    typeFilter: '',
    loading: true,
  },

  onLoad(options) {
    const city = decodeURIComponent(options.city || '');
    this.setData({ city });
    wx.setNavigationBarTitle({ title: `${city}住宿推荐` });
    this.fetchHostels();
  },

  async fetchHostels() {
    wx.showLoading({ title: '加载中...' });
    try {
      const data = await http.get('/hostel/list', {
        city: this.data.city,
        sort_by: this.data.sortBy,
        type: this.data.typeFilter,
      });
      this.setData({
        avgPrice: data.avgPrice || 0,
        hostels: data.hostels || [],
      });
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
    this.fetchHostels();
  },

  onTypeFilter(e) {
    const type = e.currentTarget.dataset.type;
    const typeFilter = this.data.typeFilter === type ? '' : type;
    this.setData({ typeFilter });
    this.fetchHostels();
  },

  onRefresh() {
    this.setData({ loading: true });
    this.fetchHostels();
  },
});
