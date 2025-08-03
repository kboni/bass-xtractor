@echo off
echo ========================================
echo Bass Extractor GUI - Dependency Installer
echo ========================================
echo.

REM Check if Python 3.10 is installed
python --version 2>nul
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.10.0 first:
    echo 1. Download from https://www.python.org/downloads/
    echo 2. Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

REM Check Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Python version: %PYTHON_VERSION%

REM Check if it's Python 3.10
echo %PYTHON_VERSION% | findstr "3.10" >nul
if errorlevel 1 (
    echo WARNING: Python 3.10.0 is recommended for Spleeter compatibility
    echo Current version: %PYTHON_VERSION%
    echo.
    echo Continue anyway? (y/n)
    set /p choice=
    if /i not "%choice%"=="y" exit /b 1
)

echo.
echo Installing required packages...
echo.

REM Install pydub
echo Installing pydub...
pip install pydub>=0.25.1
if errorlevel 1 (
    echo ERROR: Failed to install pydub
    pause
    exit /b 1
)

REM Install spleeter
echo.
echo Installing spleeter (this may take a while)...
pip install spleeter>=2.3.0
if errorlevel 1 (
    echo ERROR: Failed to install spleeter
    echo This is required for audio separation
    pause
    exit /b 1
)

REM Install pytubefix
echo.
echo Installing pytubefix...
pip install pytubefix>=9.4.1
if errorlevel 1 (
    echo ERROR: Failed to install pytubefix
    pause
    exit /b 1
)

echo.
echo ========================================
echo Installation completed successfully!
echo ========================================
echo.
echo You can now run BassExtractorGUI.exe
echo.
echo Note: The first time you run the GUI, Spleeter will download
echo its models automatically (this may take a few minutes).
echo.
pause
