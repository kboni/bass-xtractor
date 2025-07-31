#!/bin/bash
cd "$(dirname "$0")"
cd ..

# Check if we're on macOS and use the appropriate Python command
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS - try python3 first, then python
    if command -v python3 &> /dev/null; then
        python3 gui/extract_bass_gui.py
    elif command -v python &> /dev/null; then
        python gui/extract_bass_gui.py
    else
        echo "Error: Python not found. Please install Python 3.10.0"
        exit 1
    fi
else
    # Linux - use python3
    python3 gui/extract_bass_gui.py
fi 