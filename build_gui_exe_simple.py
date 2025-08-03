#!/usr/bin/env python3
"""
Simple build script for creating Windows GUI executable
Excludes large ML libraries to avoid PyInstaller issues
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    try:
        import PyInstaller
        print("✓ PyInstaller is installed")
    except ImportError:
        print("✗ PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✓ PyInstaller installed successfully")
    
    # Check other required packages
    required_packages = ["pydub", "spleeter", "pytubefix"]
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package} is available")
        except ImportError:
            print(f"✗ {package} not found. Please install it first:")
            print(f"  pip install {package}")

def clean_build_dirs():
    """Clean previous build directories"""
    print("🧹 Cleaning previous build directories...")
    
    dirs_to_clean = ["build", "dist", "__pycache__"]
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"✓ Removed {dir_name}/")
    
    # Clean .spec files
    for spec_file in Path(".").glob("*.spec"):
        spec_file.unlink()
        print(f"✓ Removed {spec_file}")

def build_executable():
    """Build the GUI executable"""
    print("🔨 Building GUI executable...")
    
    # PyInstaller command - simplified to avoid ML library issues
    cmd = [
        "pyinstaller",
        "--onefile",  # Create a single executable
        "--windowed",  # Don't show console window
        "--name=BassExtractorGUI",  # Name of the executable
        "--add-data=extract_bass.py;.",  # Include the main script
        "--add-data=youtube_downloader.py;.",  # Include YouTube downloader
        "--add-data=mix_wavs.py;.",  # Include mixing script
        "--hidden-import=pydub",  # Include pydub
        "--hidden-import=pytubefix",  # Include pytubefix
        "--hidden-import=tkinter",  # Include tkinter
        "--hidden-import=threading",  # Include threading
        "--hidden-import=queue",  # Include queue
        "--hidden-import=pathlib",  # Include pathlib
        "--hidden-import=subprocess",  # Include subprocess
        "--hidden-import=shutil",  # Include shutil
        "--hidden-import=datetime",  # Include datetime
        "--hidden-import=logging",  # Include logging
        "--hidden-import=re",  # Include re
        "--hidden-import=urllib",  # Include urllib
        "--exclude-module=tensorflow",  # Exclude tensorflow (will be installed separately)
        "--exclude-module=spleeter",  # Exclude spleeter (will be installed separately)
        "--exclude-module=librosa",  # Exclude librosa (will be installed separately)
        "--exclude-module=soundfile",  # Exclude soundfile (will be installed separately)
        "--exclude-module=scipy",  # Exclude scipy (will be installed separately)
        "--exclude-module=numpy",  # Exclude numpy (will be installed separately)
        "--exclude-module=sklearn",  # Exclude sklearn (will be installed separately)
        "--exclude-module=yaml",  # Exclude yaml (will be installed separately)
        "--exclude-module=requests",  # Exclude requests (will be installed separately)
        "--exclude-module=tqdm",  # Exclude tqdm (will be installed separately)
        "--exclude-module=ffmpeg",  # Exclude ffmpeg (will be installed separately)
        "gui/extract_bass_gui.py"  # Main GUI script
    ]
    
    print("Running PyInstaller with command:")
    print(" ".join(cmd))
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✓ Build completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Build failed with error code {e.returncode}")
        print("Error output:")
        print(e.stderr)
        return False

def create_installer_script():
    """Create a comprehensive installer script"""
    print("📝 Creating installer script...")
    
    installer_content = """@echo off
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
"""
    
    with open("install_dependencies.bat", "w") as f:
        f.write(installer_content)
    
    print("✓ Created install_dependencies.bat")

def create_readme():
    """Create a comprehensive README for the executable"""
    print("📖 Creating executable README...")
    
    readme_content = """# Bass Extractor GUI - Executable

## IMPORTANT: Installation Required

This executable requires additional dependencies to be installed on your system.

## Installation Steps

### 1. Install Python 3.10.0
- Download from https://www.python.org/downloads/
- **IMPORTANT**: Check "Add Python to PATH" during installation
- Python 3.10.0 is required for Spleeter compatibility

### 2. Install FFmpeg
- Download from https://ffmpeg.org/download.html
- Extract to a folder (e.g., C:\\ffmpeg)
- Add the bin folder to your system PATH
- Or specify the path in the GUI settings

### 3. Install Python Dependencies
- **Run `install_dependencies.bat`** to install required packages
- This will install:
  - `pydub>=0.25.1` (audio processing)
  - `spleeter>=2.3.0` (audio separation - REQUIRED)
  - `pytubefix>=9.4.1` (YouTube downloads)

## Usage

1. **Run the executable**: Double-click `BassExtractorGUI.exe`
2. **Add files**: Use "Add Files" or "Add Folder" buttons
3. **Add YouTube URLs**: Enter YouTube URLs in the text area (one per line)
4. **Set output folder**: Choose where to save processed files
5. **Configure options**: Select desired output options
6. **Start processing**: Click "Start Processing"

## Features

- **Local file processing**: Add MP3 files or folders
- **YouTube download**: Download and process YouTube videos
- **Multiple output options**: Bass only, no vocals, no drums, no other
- **Progress tracking**: Real-time progress and logging
- **File organization**: Automatic DONE folder for processed files

## Troubleshooting

### Common Issues

**"No module named 'spleeter'"**
- Run `install_dependencies.bat`
- Make sure Python 3.10.0 is installed
- Try: `pip install spleeter>=2.3.0`

**"No module named 'pydub'"**
- Run `install_dependencies.bat`
- Try: `pip install pydub>=0.25.1`

**"No module named 'pytubefix'"**
- Run `install_dependencies.bat`
- Try: `pip install pytubefix>=9.4.1`

**FFmpeg errors**
- Make sure FFmpeg is installed and in PATH
- Or specify FFmpeg path in GUI settings

**YouTube download fails**
- Try updating pytubefix: `pip install --upgrade pytubefix`
- Check internet connection
- Try different YouTube videos

**Spleeter model download issues**
- First run may take time to download models
- Check internet connection
- Try running as administrator

### Debug Mode
- Use "Skip cleanup" option to preserve temporary files
- Check `error.log` for detailed error information
- Run from command line for console output

## Requirements

- **Windows 10/11**
- **Python 3.10.0** (required for Spleeter compatibility)
- **FFmpeg** (required for audio processing)
- **Internet connection** (for YouTube downloads and Spleeter models)

## File Structure

After installation, your system will have:
- `BassExtractorGUI.exe` - Main executable
- Python packages installed via pip
- Spleeter models downloaded automatically

## Legal Notice

- YouTube downloads are for personal use only
- Users must comply with YouTube's terms of service
- Users are responsible for respecting copyright laws

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Ensure all dependencies are installed
3. Try running `install_dependencies.bat` again
4. Check that Python 3.10.0 is installed and in PATH
"""
    
    with open("EXECUTABLE_README.txt", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print("✓ Created EXECUTABLE_README.txt")

def create_quick_start():
    """Create a quick start guide"""
    print("📋 Creating quick start guide...")
    
    quick_start_content = """QUICK START GUIDE
==================

1. INSTALL PYTHON 3.10.0
   - Download from: https://www.python.org/downloads/
   - IMPORTANT: Check "Add Python to PATH" during installation

2. INSTALL FFMPEG
   - Download from: https://ffmpeg.org/download.html
   - Extract to C:\\ffmpeg (or any folder)
   - Add C:\\ffmpeg\\bin to your system PATH

3. INSTALL DEPENDENCIES
   - Double-click: install_dependencies.bat
   - Wait for installation to complete

4. RUN THE GUI
   - Double-click: BassExtractorGUI.exe
   - Add files or YouTube URLs
   - Set output folder
   - Start processing!

TROUBLESHOOTING
===============

If you get "No module named 'spleeter'":
- Run install_dependencies.bat again
- Make sure Python 3.10.0 is installed

If you get FFmpeg errors:
- Make sure FFmpeg is installed and in PATH
- Or specify FFmpeg path in GUI settings

For more help, see EXECUTABLE_README.txt
"""
    
    with open("QUICK_START.txt", "w") as f:
        f.write(quick_start_content)
    
    print("✓ Created QUICK_START.txt")

def main():
    """Main build function"""
    print("🚀 Starting Bass Extractor GUI build process...")
    print("=" * 50)
    
    # Check dependencies
    check_dependencies()
    print()
    
    # Clean previous builds
    clean_build_dirs()
    print()
    
    # Build executable
    if build_executable():
        print()
        print("✅ Build completed successfully!")
        print()
        
        # Create additional files
        create_installer_script()
        create_readme()
        create_quick_start()
        
        print("📁 Build output:")
        print("  - dist/BassExtractorGUI.exe (main executable)")
        print("  - install_dependencies.bat (dependency installer)")
        print("  - EXECUTABLE_README.txt (detailed instructions)")
        print("  - QUICK_START.txt (quick start guide)")
        print()
        print("🎉 Ready to distribute!")
        print()
        print("⚠️  IMPORTANT: Users must run install_dependencies.bat first!")
        
    else:
        print("❌ Build failed. Please check the error messages above.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 