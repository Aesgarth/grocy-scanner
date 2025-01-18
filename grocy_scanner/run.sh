#!/bin/bash

echo "Starting Grocy Item Scanner Addon..."
echo "Initializing Flask server..."

# Start Flask server
#exec python3 /app/app.py
exec gunicorn -b 0.0.0.0:3456 app:app
