#!/usr/bin/env python3
"""
YouTube downloader module for Bass Extractor GUI.
Downloads YouTube videos as MP3 files using pytubefix.
"""

import os
import re
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import urlparse, parse_qs
import logging

try:
    from pytubefix import YouTube
    PYTUBE_AVAILABLE = True
except ImportError:
    PYTUBE_AVAILABLE = False

logger = logging.getLogger(__name__)


def is_valid_youtube_url(url):
    """
    Check if the URL is a valid YouTube URL.
    
    Args:
        url (str): URL to check
        
    Returns:
        bool: True if valid YouTube URL, False otherwise
    """
    if not url or not isinstance(url, str):
        return False
    
    # YouTube URL patterns
    patterns = [
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=[\w-]+',
        r'(?:https?://)?(?:www\.)?youtu\.be/[\w-]+',
        r'(?:https?://)?(?:www\.)?youtube\.com/embed/[\w-]+',
        r'(?:https?://)?(?:www\.)?youtube\.com/v/[\w-]+',
    ]
    
    for pattern in patterns:
        if re.match(pattern, url.strip()):
            return True
    
    return False


def extract_video_id(url):
    """
    Extract video ID from YouTube URL.
    
    Args:
        url (str): YouTube URL
        
    Returns:
        str: Video ID or None if not found
    """
    if not is_valid_youtube_url(url):
        return None
    
    # Handle youtu.be URLs
    if 'youtu.be' in url:
        return url.split('/')[-1].split('?')[0]
    
    # Handle youtube.com URLs
    parsed_url = urlparse(url)
    if parsed_url.hostname in ['www.youtube.com', 'youtube.com']:
        if parsed_url.path == '/watch':
            query_params = parse_qs(parsed_url.query)
            return query_params.get('v', [None])[0]
        elif parsed_url.path.startswith('/embed/'):
            return parsed_url.path.split('/')[-1]
        elif parsed_url.path.startswith('/v/'):
            return parsed_url.path.split('/')[-1]
    
    return None


def sanitize_filename(filename):
    """
    Sanitize filename for filesystem compatibility.
    
    Args:
        filename (str): Original filename
        
    Returns:
        str: Sanitized filename
    """
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Remove leading/trailing spaces and dots
    filename = filename.strip(' .')
    
    # Limit length
    if len(filename) > 200:
        filename = filename[:200]
    
    return filename


def download_youtube_as_mp3(url, output_folder, ffmpeg_path=None):
    """
    Download YouTube video as MP3 file.
    
    Args:
        url (str): YouTube URL
        output_folder (str): Output folder path
        ffmpeg_path (str, optional): Path to FFmpeg executable
        
    Returns:
        str: Path to downloaded MP3 file or None if failed
    """
    if not PYTUBE_AVAILABLE:
        raise ImportError("pytube is not installed. Please install it with: pip install pytube")
    
    try:
        # Create output folder if it doesn't exist
        os.makedirs(output_folder, exist_ok=True)
        
        # Download video
        logger.info(f"Downloading YouTube video: {url}")
        yt = YouTube(url)
        
        # Get video title and sanitize it
        video_title = sanitize_filename(yt.title)
        logger.info(f"Video title: {video_title}")
        
        # Get the best audio stream
        audio_stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()
        
        if not audio_stream:
            raise Exception("No audio stream found")
        
        # Download to temporary file
        temp_file = audio_stream.download(output_path=tempfile.gettempdir())
        logger.info(f"Downloaded to temporary file: {temp_file}")
        
        # Convert to MP3 using FFmpeg
        output_file = os.path.join(output_folder, f"{video_title}.mp3")
        
        # Use provided FFmpeg path or system FFmpeg
        ffmpeg_cmd = ffmpeg_path if ffmpeg_path else "ffmpeg"
        
        # Convert to MP3
        cmd = [
            ffmpeg_cmd,
            '-i', temp_file,
            '-vn',  # No video
            '-acodec', 'mp3',
            '-ab', '192k',  # Bitrate
            '-ar', '44100',  # Sample rate
            '-y',  # Overwrite output file
            output_file
        ]
        
        logger.info(f"Converting to MP3: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Clean up temporary file
        try:
            os.remove(temp_file)
        except:
            pass
        
        if result.returncode != 0:
            raise Exception(f"FFmpeg conversion failed: {result.stderr}")
        
        logger.info(f"Successfully downloaded and converted: {output_file}")
        return output_file
        
    except Exception as e:
        logger.error(f"Error downloading YouTube video {url}: {str(e)}")
        raise


def download_multiple_youtube_urls(urls, output_folder, ffmpeg_path=None):
    """
    Download multiple YouTube URLs as MP3 files.
    
    Args:
        urls (list): List of YouTube URLs
        output_folder (str): Output folder path
        ffmpeg_path (str, optional): Path to FFmpeg executable
        
    Returns:
        list: List of paths to downloaded MP3 files
    """
    downloaded_files = []
    
    for i, url in enumerate(urls, 1):
        try:
            logger.info(f"Processing YouTube URL {i}/{len(urls)}: {url}")
            mp3_file = download_youtube_as_mp3(url.strip(), output_folder, ffmpeg_path)
            if mp3_file:
                downloaded_files.append(mp3_file)
        except Exception as e:
            logger.error(f"Failed to download {url}: {str(e)}")
            continue
    
    return downloaded_files


def validate_youtube_urls(urls):
    """
    Validate a list of YouTube URLs.
    
    Args:
        urls (list): List of URLs to validate
        
    Returns:
        tuple: (valid_urls, invalid_urls)
    """
    valid_urls = []
    invalid_urls = []
    
    for url in urls:
        url = url.strip()
        if url and is_valid_youtube_url(url):
            valid_urls.append(url)
        else:
            invalid_urls.append(url)
    
    return valid_urls, invalid_urls


if __name__ == "__main__":
    # Test the module
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python youtube_downloader.py <youtube_url> <output_folder>")
        sys.exit(1)
    
    url = sys.argv[1]
    output_folder = sys.argv[2]
    
    try:
        result = download_youtube_as_mp3(url, output_folder)
        print(f"Successfully downloaded: {result}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1) 