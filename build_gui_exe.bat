@echo off
echo Building Bass Extractor GUI executable...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.10.0 first
    pause
    exit /b 1
)

REM Run the build script
python build_gui_exe.py

echo.
echo Build process completed!
pause 