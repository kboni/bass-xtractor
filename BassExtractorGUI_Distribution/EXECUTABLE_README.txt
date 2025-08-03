# Bass Extractor GUI - Executable

## IMPORTANT: Installation Required

This executable requires additional dependencies to be installed on your system.

## Installation Steps

### 1. Install Python 3.10.0
- Download from https://www.python.org/downloads/
- **IMPORTANT**: Check "Add Python to PATH" during installation
- Python 3.10.0 is required for Spleeter compatibility

### 2. Install FFmpeg
- Download from https://ffmpeg.org/download.html
- Extract to a folder (e.g., C:\ffmpeg)
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
