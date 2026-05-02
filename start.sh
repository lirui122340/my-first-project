#!/bin/bash
cd travel.app/server-python
exec gunicorn --bind 0.0.0.0:$PORT --timeout 120 app:app
