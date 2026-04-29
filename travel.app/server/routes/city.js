const express = require('express');
const router = express.Router();
const cityData = require('../data/cities');

router.get('/list', (req, res) => {
  res.json({ code: 0, data: cityData });
});

router.get('/destinations', (req, res) => {
  const { from_city } = req.query;
  const cityMapping = require('../data/city-mapping');
  const destinations = cityMapping[from_city] || [];
  res.json({ code: 0, data: { fromCity: from_city, destinations } });
});

module.exports = router;
