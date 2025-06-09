#!/bin/bash
#
# Tiny Top Games Launcher
# =======================
#
# Simple shell script to launch the main menu.
# This is the main entry point for users.
#
# Usage:
#   ./TinyTopGames.sh
#   bash TinyTopGames.sh
#
# Requirements:
#   - Python 3.x with pygame installed
#   - games/ directory with game.py files
#

echo "🎮 Starting Tiny Top Games..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "❌ Error: Python not found!"
        echo "Please install Python 3.x and try again."
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

# Check if pygame is installed
$PYTHON_CMD -c "import pygame" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Error: pygame not found!"
    echo "Please install pygame with: pip install pygame"
    exit 1
fi

# Check if games directory exists
if [ ! -d "games" ]; then
    echo "❌ Error: games/ directory not found!"
    echo "Please make sure you're running this from the TinyTopGames directory."
    exit 1
fi

# Launch main menu
echo "🚀 Launching main menu..."
$PYTHON_CMD main_menu.py

echo "👋 Thanks for playing Tiny Top Games!"
