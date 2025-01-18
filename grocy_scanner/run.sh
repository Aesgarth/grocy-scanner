#!/bin/sh

echo "Starting Grocy Item Scanner Addon..."
echo "Initializing Flask server..."

# Start Flask server
exec python3 /app/app.py
