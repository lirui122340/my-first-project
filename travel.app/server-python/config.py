import os

PORT = int(os.environ.get('PORT', 3000))
API_KEY = os.environ.get('API_KEY', '')
CACHE_TTL = int(os.environ.get('CACHE_TTL', 300))
CONCURRENCY_LIMIT = 5
REQUEST_DELAY = 0.8

DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = int(os.environ.get('DB_PORT', 5432))
DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
DB_NAME = os.environ.get('DB_NAME', 'travel_app')
