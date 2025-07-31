#!/usr/bin/env python3
"""
Extract bass from audio files using command line interface.
"""

import argparse
import os
import sys
import shutil
import logging
from pathlib import Path
from pydub import AudioSegment
from mix_wavs import mix_wavs
from spleeter.separator import Separator


def extract_bass_from_file(input_file, output_folder, nocleanup=False):
    """
    Extract bass from a single audio file using Spleeter.
    
    Args:
        input_file (str): Path to input audio file
        output_folder (str): Path to output folder
        nocleanup (bool): Whether to skip cleanup of temporary files
    """
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('error.log'),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)
    
    try:
        # Get the filename without extension
        input_path = Path(input_file)
        filename = input_path.stem
        
        logger.info(f"Processing: {input_file}")
        
        # Create temp folder for Spleeter output
        temp_folder = "bass_extractor_temp"
        os.makedirs(temp_folder, exist_ok=True)
        
        # Initialize Spleeter separator with error handling
        logger.info(f"Initializing Spleeter separator...")
        try:
            separator = Separator('spleeter:4stems')
            logger.info("Spleeter separator initialized successfully")
        except Exception as e:
            error_msg = f"Failed to initialize Spleeter separator: {str(e)}"
            logger.error(error_msg)
            print(f"Error: {error_msg}")
            return
        
        # Perform separation using Spleeter API
        logger.info(f"Running Spleeter separation...")
        try:
            separator.separate_to_file(input_file, temp_folder)
            logger.info("Spleeter separation completed successfully")
        except Exception as e:
            error_msg = f"Failed to perform Spleeter separation for {input_file}: {str(e)}"
            logger.error(error_msg)
            print(f"Error: {error_msg}")
            return
        
        # Path to the separated files
        separated_folder = os.path.join(temp_folder, filename)
        bass_path = os.path.join(separated_folder, "bass.wav")
        drums_path = os.path.join(separated_folder, "drums.wav")
        vocals_path = os.path.join(separated_folder, "vocals.wav")
        other_path = os.path.join(separated_folder, "other.wav")
        
        # Check if all files exist
        missing_files = []
        for path, name in [(bass_path, "bass.wav"), (drums_path, "drums.wav"), 
                          (vocals_path, "vocals.wav"), (other_path, "other.wav")]:
            if not os.path.exists(path):
                missing_files.append(name)
        
        if missing_files:
            error_msg = f"Missing separated files for {input_file}: {', '.join(missing_files)}"
            logger.error(error_msg)
            print(f"Error: {error_msg}")
            return
        
        logger.info(f"Separation completed. Mixing tracks...")
        
        # Use mix_wavs function to create the final outputs
        try:
            mix_wavs(bass_path, drums_path, vocals_path, other_path, filename, output_folder)
            logger.info(f"Successfully created output files for {input_file}")
        except Exception as e:
            error_msg = f"Failed to create output files for {input_file}: {str(e)}"
            logger.error(error_msg)
            print(f"Error: {error_msg}")
            return
        
        print(f"Completed: {input_file}")
        print(f"  - {filename}[NOBASS].mp3 created in {output_folder}")
        print(f"  - {filename}[BASSONLY].mp3 created in {output_folder}")
        
        # Clean up temp files
        if not nocleanup:
            logger.info("Cleaning up temporary files...")
            try:
                if os.path.exists(separated_folder):
                    shutil.rmtree(separated_folder)
                    logger.info("Temporary files cleaned up successfully")
            except Exception as e:
                error_msg = f"Failed to clean up temporary files: {str(e)}"
                logger.error(error_msg)
                print(f"Warning: {error_msg}")
        else:
            logger.info("Skipping cleanup - temporary files preserved")
        
    except Exception as e:
        error_msg = f"Unexpected error processing {input_file}: {str(e)}"
        logger.error(error_msg)
        print(f"Error: {error_msg}")


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
    
    # Setup logging for main process
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('error.log'),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)
    
    successful_files = 0
    failed_files = 0
    
    for file_path in files_to_process:
        try:
            extract_bass_from_file(file_path, args.output_folder, args.nocleanup)
            successful_files += 1
        except Exception as e:
            error_msg = f"Failed to process {file_path}: {str(e)}"
            logger.error(error_msg)
            failed_files += 1
    
    # Summary
    logger.info(f"Processing completed. Successful: {successful_files}, Failed: {failed_files}")
    print(f"Bass extraction completed! Successful: {successful_files}, Failed: {failed_files}")
    
    if failed_files > 0:
        print(f"Check error.log for detailed error information.")


if __name__ == "__main__":
    main() 