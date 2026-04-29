module.exports = {
  port: process.env.PORT || 3000,
  apiKey: process.env.API_KEY || '',
  cacheTTL: parseInt(process.env.CACHE_TTL) || 300,
  concurrencyLimit: 5,
  requestDelay: 500,
};
