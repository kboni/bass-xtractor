# Bass Extractor

A Python script to extract bass from audio files using command line interface. **This project is based on [Spleeter](https://github.com/deezer/spleeter)**, an open-source audio separation library by Deezer.

## Installation

### Python Version Requirement

This project requires Python 3.10.0. Spleeter is not compatible with higher Python versions.

#### Using pyenv (Recommended)

1. Install pyenv:
   - **Windows**: Download from [pyenv-win](https://github.com/pyenv-win/pyenv-win)
   - **macOS/Linux**: `brew install pyenv` or follow [pyenv installation guide](https://github.com/pyenv/pyenv#installation)

2. Install Python 3.10.0:
   ```bash
   pyenv install 3.10.0
   pyenv global 3.10.0 # or pyenv local 3.10.0 to apply only to current folder and subfolders
   ```

3. Verify the installation:
   ```bash
   python --version
   # Should output: Python 3.10.0
   ```

### Dependencies

1. Install required Python packages:
   ```bash
   pip install pydub
   ```

2. Install Spleeter:
   ```bash
   pip install spleeter
   ```

   **Note**: This project uses and relies on [Spleeter](https://github.com/deezer/spleeter) for audio separation. Visit their GitHub page for more information about the tool and its capabilities.

### FFmpeg Installation

FFmpeg is required for audio processing. Installation depends on your operating system:

#### Windows
1. Download FFmpeg from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
2. Extract to a folder (e.g., `C:\ffmpeg`)
3. Add the `bin` folder to your system PATH, OR
4. Use the `--ffmpeg` argument to specify the path to ffmpeg.exe

**Note**: If you encounter issues installing Spleeter on Windows even after manual FFmpeg installation, try:
```bash
pip uninstall ffmpeg
pip uninstall ffmpeg-python
pip install ffmpeg-python
```

#### macOS
```bash
brew install ffmpeg
```

#### Linux
```bash
sudo apt update
sudo apt install ffmpeg
```

## Usage

The script can be called in several ways:

### Using the Python script directly:
```bash
python extract_bass.py --folder /path/to/music --output_folder /path/to/output
python extract_bass.py --file song1.mp3 --file song2.mp3 --output_folder /path/to/output
```

### Using the batch file (Windows):
```bash
extract_bass.bat --folder /path/to/music --output_folder /path/to/output
extract_bass.bat --file song1.mp3 --file song2.mp3 --output_folder /path/to/output
```

### Using the shell script (Unix/Linux/macOS):
```bash
./extract_bass.sh --folder /path/to/music --output_folder /path/to/output
./extract_bass.sh --file song1.mp3 --file song2.mp3 --output_folder /path/to/output
```

## Arguments

- `--folder folder_name`: Process all MP3 files in the specified folder
- `--file file_name`: Process individual MP3 files (can be used multiple times)
- `--output_folder`: Required. Specify the output folder for processed files
- `--ffmpeg path`: Optional. Path to ffmpeg executable (if not in PATH)
- `--nocleanup`: Optional. Skip cleanup of temporary files (useful for debugging)

## Rules

- If `--folder` is specified, all `--file` arguments will be ignored
- You must specify either `--folder` or `--file` (or multiple `--file` arguments)
- The `--output_folder` argument is always required

## Examples

```bash
# Process all MP3 files in a folder
extract_bass --folder ./music --output_folder ./output

# Process individual files
extract_bass --file song1.mp3 --file song2.mp3 --output_folder ./output

# Process multiple individual files
extract_bass --file track1.mp3 --file track2.mp3 --file track3.mp3 --output_folder ./processed

# Specify FFmpeg path (Windows example)
extract_bass --folder ./music --output_folder ./output --ffmpeg "C:\ffmpeg\bin\ffmpeg.exe"

# Specify FFmpeg path (macOS/Linux example)
extract_bass --file song.mp3 --output_folder ./output --ffmpeg "/usr/local/bin/ffmpeg"

# Skip cleanup to preserve temporary files (useful for debugging)
extract_bass --folder ./music --output_folder ./output --nocleanup
```

## Output

For each input file, the script will create two output files in the specified output folder:

1. `{original_filename}[NOBASS].mp3` - The original song without bass (drums + vocals + other instruments mixed together)
2. `{original_filename}[BASSONLY].mp3` - Only the bass track extracted from the original song

## How it works

1. Uses Spleeter to separate the audio into 4 stems: bass, drums, vocals, and other
2. Mixes drums, vocals, and other together to create the "no bass" version
3. Extracts the bass track separately
4. Exports both files in MP3 format to the output folder
5. Cleans up temporary files automatically 