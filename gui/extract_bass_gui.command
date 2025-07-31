#!/bin/bash
cd "$(dirname "$0")"
cd ..

# macOS-specific Python detection and execution
if command -v python3 &> /dev/null; then
    python3 gui/extract_bass_gui.py
elif command -v python &> /dev/null; then
    python gui/extract_bass_gui.py
else
    echo "Error: Python not found. Please install Python 3.10.0"
    echo "You can install it using Homebrew: brew install python@3.10"
    echo "Or download from: https://www.python.org/downloads/"
    read -p "Press Enter to exit..."
    exit 1
fi 