function request(url, method, data) {
  const app = getApp();
  return new Promise((resolve, reject) => {
    wx.request({
      url: app.globalData.baseUrl + url,
      method: method || 'GET',
      data: data || {},
      header: {
        'content-type': 'application/json',
      },
      success(res) {
        if (res.statusCode === 200 && res.data.code === 0) {
          resolve(res.data.data);
        } else {
          reject(res.data || { code: -1, message: '请求失败' });
        }
      },
      fail(err) {
        console.error('请求失败:', url, err);
        reject(err);
      },
    });
  });
}

function get(url, data) {
  return request(url, 'GET', data);
}

function post(url, data) {
  return request(url, 'POST', data);
}

module.exports = { get, post };
