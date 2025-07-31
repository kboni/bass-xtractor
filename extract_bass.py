#!/usr/bin/env python3
"""
Extract bass from audio files using command line interface.
"""

import argparse
import os
import sys
import subprocess
import shutil
from pathlib import Path
from pydub import AudioSegment
from mix_wavs import mix_wavs


def extract_bass_from_file(input_file, output_folder, nocleanup=False):
    """
    Extract bass from a single audio file using Spleeter.
    
    Args:
        input_file (str): Path to input audio file
        output_folder (str): Path to output folder
    """
    try:
        # Get the filename without extension
        input_path = Path(input_file)
        filename = input_path.stem
        
        print(f"Processing: {input_file}")
        
        # Create temp folder for Spleeter output
        temp_folder = "temp"
        os.makedirs(temp_folder, exist_ok=True)
        
        # Run Spleeter command
        print(f"Running Spleeter separation...")
        cmd = ["spleeter", "separate", "-o", temp_folder, "-p", "spleeter:4stems", input_file]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Spleeter error: {result.stderr}")
            return
        
        # Path to the separated files
        separated_folder = os.path.join(temp_folder, filename)
        bass_path = os.path.join(separated_folder, "bass.wav")
        drums_path = os.path.join(separated_folder, "drums.wav")
        vocals_path = os.path.join(separated_folder, "vocals.wav")
        other_path = os.path.join(separated_folder, "other.wav")
        
        # Check if all files exist
        if not all(os.path.exists(path) for path in [bass_path, drums_path, vocals_path, other_path]):
            print(f"Error: Not all separated files were created for {input_file}")
            return
        
        print(f"Separation completed. Mixing tracks...")
        
        # Use mix_wavs function to create the final outputs
        mix_wavs(bass_path, drums_path, vocals_path, other_path, filename, output_folder)
        
        print(f"Completed: {input_file}")
        print(f"  - {filename}[NOBASS].mp3 created in {output_folder}")
        print(f"  - {filename}[BASSONLY].mp3 created in {output_folder}")
        
        # Clean up temp files
        if not nocleanup:
            print("Cleaning up temporary files...")
            if os.path.exists(separated_folder):
                shutil.rmtree(separated_folder)
        else:
            print("Skipping cleanup - temporary files preserved")
        
    except Exception as e:
        print(f"Error processing {input_file}: {str(e)}")


def main():
    parser = argparse.ArgumentParser(
        description="Extract bass from audio files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  extract_bass --folder /path/to/music --output_folder /path/to/output
  extract_bass --file song1.mp3 --file song2.mp3 --output_folder /path/to/output
        """
    )
    
    # Add arguments
    parser.add_argument(
        '--folder',
        type=str,
        help='Folder containing MP3 files to process'
    )
    
    parser.add_argument(
        '--file',
        type=str,
        action='append',
        help='Individual MP3 file to process (can be used multiple times)'
    )
    
    parser.add_argument(
        '--output_folder',
        type=str,
        required=True,
        help='Output folder for processed files'
    )
    
    parser.add_argument(
        '--ffmpeg',
        type=str,
        help='Path to ffmpeg executable (if not in PATH)'
    )
    
    parser.add_argument(
        '--nocleanup',
        action='store_true',
        help='Skip cleanup of temporary files'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.folder and args.file:
        print("Error: Cannot use both --folder and --file arguments together.")
        print("If --folder is specified, all --file arguments will be ignored.")
        sys.exit(1)
    
    if not args.folder and not args.file:
        print("Error: Must specify either --folder or --file argument.")
        sys.exit(1)
    
    # Process files
    files_to_process = []
    
    if args.folder:
        # Process all MP3 files in the folder
        folder_path = Path(args.folder)
        if not folder_path.exists():
            print(f"Error: Folder '{args.folder}' does not exist.")
            sys.exit(1)
        
        # Find all MP3 files in the folder
        for file_path in folder_path.glob("*.mp3"):
            files_to_process.append(str(file_path))
        
        if not files_to_process:
            print(f"No MP3 files found in folder '{args.folder}'.")
            sys.exit(1)
        
        print(f"Found {len(files_to_process)} MP3 files in folder '{args.folder}'.")
    
    elif args.file:
        # Process individual files
        files_to_process = args.file
        
        # Check if all files exist
        for file_path in files_to_process:
            if not os.path.exists(file_path):
                print(f"Error: File '{file_path}' does not exist.")
                sys.exit(1)
        
        print(f"Processing {len(files_to_process)} individual files.")
    
    # Set FFmpeg path if provided
    if args.ffmpeg:
        AudioSegment.converter = args.ffmpeg
        print(f"Using FFmpeg from: {args.ffmpeg}")
    
    # Process each file
    print(f"Output folder: {args.output_folder}")
    print("Starting bass extraction...")
    
    for file_path in files_to_process:
        extract_bass_from_file(file_path, args.output_folder, args.nocleanup)
    
    print("Bass extraction completed!")


if __name__ == "__main__":
    main() 