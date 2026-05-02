import os

PORT = int(os.environ.get('PORT', 3000))
API_KEY = os.environ.get('API_KEY', '')
CACHE_TTL = int(os.environ.get('CACHE_TTL', 300))
CONCURRENCY_LIMIT = 5
REQUEST_DELAY = 0.8
