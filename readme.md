# Endfield Market Tracker

A companion desktop application for Endfield that helps you make optimal trading decisions by analyzing in-game market prices.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows-blue.svg)
![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)

## What It Does

Endfield Market Tracker watches your game screen, reads market prices using computer vision, and tells you the most profitable trades to make each day.

**Key Features:**
- Automatically captures prices as you browse goods in-game
- Calculates absolute profit potential (Friend Price - Local Price)
- Ranks today's best trading opportunities
- Tracks price history over time to identify patterns
- Supports both Wuling and Valley regions
- Works entirely offline - no data leaves your computer

## How It Works

1. **Start the app** and click the "Start" button
2. **Browse your goods** in-game as normal
3. **Click "Stop"** when you're done
4. **View recommendations** - the app shows you which goods have the highest profit potential
5. **Check history** - see price trends over time to plan your strategy

The app uses screen capture and OCR (Optical Character Recognition) to read prices from your game window. It never attaches to the game process or modifies game files.

## Installation

### Requirements
- Windows 10 or 11
- Python 3.11 or higher (if running from source)
- Endfield running at 1920x1080 resolution (windowed or fullscreen)
- Decent CPU/GPU for OCR processing

### Download Pre-built Executable
1. Go to the [Releases](https://github.com/yourusername/endfield-market-tracker/releases) page
2. Download the latest `EndfieldMarketTracker.exe`
3. Run the executable

### Run from Source
```bash
# Clone the repository
git clone https://github.com/yourusername/endfield-market-tracker.git
cd endfield-market-tracker

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python src/main.py