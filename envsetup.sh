#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status

if [ -d "/mnt/LOFAR0" ]; then
  export TMPDIR="/mnt/LOFAR0/tmp"
  export PIP_CACHE_DIR="$TMPDIR/pip-cache"
  mkdir -p "$TMPDIR"
  mkdir -p "$PIP_CACHE_DIR"
fi

# Create the virtual environment only if it does not exist
if [ ! -d "venv" ]; then
  echo "Creating virtual environment..."
  python3.12 -m venv venv
fi

# Activate the virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies from requirements.txt
echo "Installing dependencies..."
pip3.12 install -r requirements.txt

echo "Setup complete. Virtual environment is ready."
