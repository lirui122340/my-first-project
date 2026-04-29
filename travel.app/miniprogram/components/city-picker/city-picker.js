const { hotCities, allCities } = require('../../utils/city-data');

Component({
  properties: {},

  data: {
    hotCities,
    allCities,
    letters: Object.keys(allCities).sort(),
    searchText: '',
    searchResults: [],
  },

  methods: {
    onSearchInput(e) {
      const searchText = e.detail.value.trim();
      this.setData({ searchText });
      if (!searchText) {
        this.setData({ searchResults: [] });
        return;
      }
      const results = [];
      Object.values(allCities).forEach((cities) => {
        cities.forEach((city) => {
          if (city.includes(searchText)) {
            results.push(city);
          }
        });
      });
      this.setData({ searchResults: results });
    },

    onHotCityTap(e) {
      const city = e.currentTarget.dataset.city;
      this.triggerEvent('confirm', { city });
    },

    onCityTap(e) {
      const city = e.currentTarget.dataset.city;
      this.triggerEvent('confirm', { city });
    },

    onLetterTap(e) {
      const letter = e.currentTarget.dataset.letter;
      const query = this.createSelectorQuery();
      query.select(`#letter-${letter}`).boundingClientRect();
      query.selectViewport().scrollOffset();
      query.exec((res) => {
        if (res[0]) {
          wx.pageScrollTo({
            scrollTop: res[1].scrollTop + res[0].top - 100,
          });
        }
      });
    },

    onCancel() {
      this.triggerEvent('cancel');
    },
  },
});
