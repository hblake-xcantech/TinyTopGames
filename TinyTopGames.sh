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
#
# Requirements:
#   - Python 3.x with pygame installed in venv
#   - games/ directory with game.py files
#

echo "🎮 Starting Tiny Top Games..."

# Move to script directory (safe if run from anywhere)
cd "$(dirname "$0")"

# Force using venv python if available
if [ -x "./venv/bin/python" ]; then
    PYTHON_CMD="./venv/bin/python"
else
    echo "❌ Error: venv not found or broken!"
    echo "Please run:"
    echo "  python3 -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi

# Check if all requirements are installed
echo "🔍 Checking dependencies..."
$PYTHON_CMD -c "import pygame, requests, dotenv" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📦 Installing missing dependencies..."
    $PYTHON_CMD -m pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "⚠️  Some packages failed to install. Trying alternative approach..."
        # Try installing without problematic packages first
        $PYTHON_CMD -m pip install pygame requests python-dotenv
        if [ $? -ne 0 ]; then
            echo "❌ Error: Failed to install core requirements!"
            echo "Please check your internet connection and try again."
            exit 1
        fi
        
        # Try quickdraw separately (might fail on old systems, but game can still work)
        echo "📦 Attempting to install quickdraw (may fail on old systems)..."
        $PYTHON_CMD -m pip install quickdraw
        if [ $? -ne 0 ]; then
            echo "⚠️  quickdraw failed to install - doodle_type game will not work"
            echo "But other games should still work fine!"
        fi
    fi
    echo "✅ Dependencies installed!"
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