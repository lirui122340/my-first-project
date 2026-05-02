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
    const batchResults = await Promise.allSettled(promises);
    batchResults.forEach((r, idx) => {
      if (r.status === 'fulfilled' && r.value && r.value.data) {
        results.push({ city: batch[idx], trains: r.value.data });
      } else {
        results.push({ city: batch[idx], trains: [] });
      }
    });
    if (i + config.concurrencyLimit < destinations.length) {
      await delay(config.requestDelay);
    }
  }

  const aggregated = aggregateResults(fromCity, date, results);
  setCache(cacheKey, aggregated);
  return aggregated;
}

function aggregateResults(fromCity, date, results) {
  const destinationList = [];

  results.forEach(({ city, trains }) => {
    if (!trains || trains.length === 0) return;

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
        const validPrices = prices.filter((p) => !isNaN(p) && p > 0);
        if (validPrices.length > 0) {
          const min = Math.min(...validPrices);
          if (min < minPrice) minPrice = min;
        }
      }
    });

    if (minPrice === Infinity) {
      const cheapestTrain = findCheapestTrainByDuration(trains);
      minPrice = cheapestTrain;
    }

    destinationList.push({
      city,
      totalSeats: totalSeats || 0,
      minPrice: minPrice === Infinity ? 0 : minPrice,
      trainCount,
    });
  });

  destinationList.sort((a, b) => b.totalSeats - a.totalSeats);

  return { fromCity, date, destinations: destinationList };
}

function findCheapestTrainByDuration(trains) {
  let minPrice = Infinity;
  trains.forEach((train) => {
    if (!train.duration) return;
    const parts = train.duration.split(':');
    if (parts.length < 2) return;
    const hours = parseInt(parts[0]) + parseInt(parts[1]) / 60;
    if (isNaN(hours)) return;

    const prefix = train.trainNo.charAt(0);
    let estimatedPrice;
    if (prefix === 'G') {
      estimatedPrice = Math.round(hours * 115);
    } else if (prefix === 'D') {
      estimatedPrice = Math.round(hours * 50);
    } else if (prefix === 'C') {
      estimatedPrice = Math.round(hours * 50);
    } else {
      estimatedPrice = Math.round(hours * 15);
    }

    if (estimatedPrice < minPrice) minPrice = estimatedPrice;
  });
  return minPrice;
}

module.exports = { batchQueryDestinations };
