#!/bin/bash
set -e
echo "Starting Grocy Item Scanner Addon..."

# Ensure configuration directory exists
CONFIG_DIR="/data/config"
if [ ! -d "$CONFIG_DIR" ]; then
    mkdir -p "$CONFIG_DIR"
fi

# Start the application
echo "Starting FastAPI server..."
exec uvicorn main:app --host 0.0.0.0 --port 3456
