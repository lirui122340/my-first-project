const ticketService = require('./ticket-service');
const cityMapping = require('../data/city-mapping');
const config = require('../config');

const cache = new Map();

function getCacheKey(fromCity, date) {
  return `${fromCity}_${date}`;
}

function getFromCache(key) {
  const entry = cache.get(key);
  if (entry && Date.now() - entry.timestamp < config.cacheTTL * 1000) {
    return entry.data;
  }
  cache.delete(key);
  return null;
}

function setCache(key, data) {
  cache.set(key, { data, timestamp: Date.now() });
}

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function batchQueryDestinations(fromCity, date) {
  const cacheKey = getCacheKey(fromCity, date);
  const cached = getFromCache(cacheKey);
  if (cached) return cached;

  const destinations = cityMapping[fromCity];
  if (!destinations || destinations.length === 0) {
    return { fromCity, date, destinations: [] };
  }

  const results = [];
  for (let i = 0; i < destinations.length; i += config.concurrencyLimit) {
    const batch = destinations.slice(i, i + config.concurrencyLimit);
    const promises = batch.map((toCity) =>
      ticketService.queryTickets(fromCity, toCity, date)
    );
    const batchResults = await Promise.all(promises);
    results.push(...batchResults);
    if (i + config.concurrencyLimit < destinations.length) {
      await delay(config.requestDelay);
    }
  }

  const aggregated = aggregateResults(fromCity, date, destinations, results);
  setCache(cacheKey, aggregated);
  return aggregated;
}

function aggregateResults(fromCity, date, destinations, results) {
  const destinationList = [];

  destinations.forEach((toCity, index) => {
    const result = results[index];
    if (!result || !result.data || result.data.length === 0) return;

    const trains = result.data;
    let totalSeats = 0;
    let minPrice = Infinity;
    let trainCount = trains.length;

    trains.forEach((train) => {
      if (train.seats) {
        Object.values(train.seats).forEach((seatInfo) => {
          const num = parseInt(seatInfo);
          if (!isNaN(num)) totalSeats += num;
        });
      }
      if (train.prices) {
        const prices = Object.values(train.prices).map((p) =>
          typeof p === 'string' ? parseInt(p) : p
        );
        const min = Math.min(...prices.filter((p) => !isNaN(p)));
        if (min < minPrice) minPrice = min;
      }
    });

    destinationList.push({
      city: toCity,
      totalSeats: totalSeats || 0,
      minPrice: minPrice === Infinity ? 0 : minPrice,
      trainCount,
    });
  });

  destinationList.sort((a, b) => b.totalSeats - a.totalSeats);

  return { fromCity, date, destinations: destinationList };
}

module.exports = { batchQueryDestinations };
