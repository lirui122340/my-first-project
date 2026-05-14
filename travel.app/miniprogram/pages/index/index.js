Page({
  data: {
    fromCity: '',
    date: '',
    today: '',
    showCityPicker: false,// 控制城市选择弹窗是否显示（false=隐藏）
  },

  onLoad() {
    const now = new Date();
    const today = this.formatDate(now);
    this.setData({ date: today, today });
  },

  formatDate(date) {
    const y = date.getFullYear();
    const m = String(date.getMonth() + 1).padStart(2, '0');
    const d = String(date.getDate()).padStart(2, '0');
    return `${y}-${m}-${d}`;
  },

  onCityTap() {
    this.setData({ showCityPicker: true });
  },

  onCityConfirm(e) {
    const city = e.detail.city;
    this.setData({ fromCity: city, showCityPicker: false });
  },

  onCityCancel() {
    this.setData({ showCityPicker: false });
  },

  onDateChange(e) {
    this.setData({ date: e.detail.value });
  },

  onSearch() {
    if (!this.data.fromCity) {
      wx.showToast({ title: '请选择出发城市', icon: 'none' });
      return;
    }
    const app = getApp();
    app.globalData.fromCity = this.data.fromCity;
    app.globalData.date = this.data.date;
    wx.navigateTo({
      url: `/pages/city-list/city-list?fromCity=${encodeURIComponent(this.data.fromCity)}&date=${this.data.date}`,
    });
  },
});
