#!/bin/bash

# TinyTopGames auto updater and runner

echo "==== TinyTopGames ===="
echo "Pulling latest updates..."
git pull

# Check for venv, create if missing
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing requirements..."
pip install -r requirements.txt

echo "Running game!"
python main.py
