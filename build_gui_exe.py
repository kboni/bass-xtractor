#!/usr/bin/env python3
"""
Build script for creating Windows GUI executable
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
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",  # Create a single executable
        "--windowed",  # Don't show console window
        "--name=BassExtractorGUI",  # Name of the executable
        "--add-data=extract_bass.py;.",  # Include the main script
        "--add-data=youtube_downloader.py;.",  # Include YouTube downloader
        "--add-data=mix_wavs.py;.",  # Include mixing script
        "--hidden-import=pydub",  # Include pydub
        "--hidden-import=spleeter",  # Include spleeter
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
        "--hidden-import=tensorflow",  # Include tensorflow (required by spleeter)
        "--hidden-import=librosa",  # Include librosa (required by spleeter)
        "--hidden-import=soundfile",  # Include soundfile (required by spleeter)
        "--hidden-import=scipy",  # Include scipy (required by spleeter)
        "--hidden-import=numpy",  # Include numpy (required by spleeter)
        "--hidden-import=sklearn",  # Include sklearn (required by spleeter)
        "--hidden-import=yaml",  # Include yaml (required by spleeter)
        "--hidden-import=requests",  # Include requests (required by spleeter)
        "--hidden-import=tqdm",  # Include tqdm (required by spleeter)
        "--hidden-import=ffmpeg",  # Include ffmpeg (required by spleeter)
        "--collect-all=spleeter",  # Collect all spleeter files
        "--collect-all=tensorflow",  # Collect all tensorflow files
        "--collect-all=librosa",  # Collect all librosa files
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
    """Create a simple installer script"""
    print("📝 Creating installer script...")
    
    installer_content = """@echo off
echo Installing Bass Extractor GUI...
echo.

REM Check if Python 3.10 is installed
python --version 2>nul
if errorlevel 1 (
    echo Python is not installed or not in PATH
    echo Please install Python 3.10.0 first
    pause
    exit /b 1
)

REM Check Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Python version: %PYTHON_VERSION%

REM Install required packages (only if not already included in exe)
echo Installing required packages...
pip install pydub>=0.25.1
pip install pytubefix>=9.4.1

echo.
echo Installation complete!
echo You can now run BassExtractorGUI.exe
pause
"""
    
    with open("install_dependencies.bat", "w") as f:
        f.write(installer_content)
    
    print("✓ Created install_dependencies.bat")

def create_readme():
    """Create a README for the executable"""
    print("📖 Creating executable README...")
    
    readme_content = """# Bass Extractor GUI - Executable

## Installation

1. **Install Python 3.10.0** (required for Spleeter compatibility)
   - Download from https://www.python.org/downloads/
   - Make sure to check "Add Python to PATH" during installation

2. **Install FFmpeg** (required for audio processing)
   - Download from https://ffmpeg.org/download.html
   - Extract to a folder (e.g., C:\\ffmpeg)
   - Add the bin folder to your system PATH

3. **Install Dependencies** (optional - most are included in exe)
   - Run `install_dependencies.bat` to install remaining Python packages
   - Or manually install:
     ```
     pip install pydub>=0.25.1
     pip install pytubefix>=9.4.1
     ```

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

- **"No module named 'pydub'"**: Run `install_dependencies.bat`
- **"No module named 'pytubefix'"**: Run `install_dependencies.bat`
- **FFmpeg errors**: Make sure FFmpeg is installed and in PATH
- **YouTube download fails**: Try updating pytubefix: `pip install --upgrade pytubefix`
- **Large executable**: This is normal - it includes all required ML libraries

## Requirements

- Windows 10/11
- Python 3.10.0
- FFmpeg
- Internet connection (for YouTube downloads)

## Legal Notice

- YouTube downloads are for personal use only
- Users must comply with YouTube's terms of service
- Users are responsible for respecting copyright laws
"""
    
    with open("EXECUTABLE_README.txt", "w") as f:
        f.write(readme_content)
    
    print("✓ Created EXECUTABLE_README.txt")

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
        
        print("📁 Build output:")
        print("  - dist/BassExtractorGUI.exe (main executable)")
        print("  - install_dependencies.bat (dependency installer)")
        print("  - EXECUTABLE_README.txt (usage instructions)")
        print()
        print("🎉 Ready to distribute!")
        
    else:
        print("❌ Build failed. Please check the error messages above.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 