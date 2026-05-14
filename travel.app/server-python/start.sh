#!/bin/sh
PORT=${PORT:-3000}
echo "Starting server on port $PORT"
exec gunicorn app:app --bind 0.0.0.0:$PORT --timeout 120
