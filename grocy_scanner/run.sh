#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Ensure the configuration directory exists
CONFIG_DIR="/data/config"
if [ ! -d "$CONFIG_DIR" ]; then
    mkdir -p "$CONFIG_DIR"
fi

# Start the main application
exec python3 /app/main.py
