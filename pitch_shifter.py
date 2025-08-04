#!/usr/bin/env python3
"""
Pitch shifting utility for audio files.
Supports shifting by musical notes (C, D, E, F, G, A, B).
"""

import os
import subprocess
import tempfile
from pathlib import Path
from pydub import AudioSegment


# Musical note frequencies (A4 = 440Hz)
NOTE_FREQUENCIES = {
    'C': 261.63,  # C4
    'C#': 277.18,
    'D': 293.66,
    'D#': 311.13,
    'E': 329.63,
    'F': 349.23,
    'F#': 369.99,
    'G': 392.00,
    'G#': 415.30,
    'A': 440.00,
    'A#': 466.16,
    'B': 493.88
}

# Note names for display
NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']


def detect_key(audio_file):
    """
    Detect the key of an audio file using FFmpeg.
    This is a simplified approach - for more accurate key detection,
    you might want to use specialized libraries like librosa.
    
    Args:
        audio_file (str): Path to audio file
        
    Returns:
        str: Detected key (e.g., 'C', 'D', etc.) or None if detection fails
    """
    try:
        # Use FFmpeg to analyze the audio and get frequency information
        cmd = [
            'ffmpeg', '-i', audio_file, '-af', 
            'astats=metadata=1:reset=1,ametadata=print:key=lavfi.astats.Overall.RMS_level',
            '-f', 'null', '-'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        # This is a simplified approach - in practice, you'd want more sophisticated
        # key detection using FFT analysis or specialized libraries
        # For now, we'll return None to indicate no automatic detection
        return None
        
    except Exception as e:
        print(f"Warning: Could not detect key for {audio_file}: {e}")
        return None


def calculate_pitch_shift(from_note, to_note):
    """
    Calculate the pitch shift ratio between two musical notes.
    
    Args:
        from_note (str): Source note (e.g., 'C', 'D', etc.)
        to_note (str): Target note (e.g., 'C', 'D', etc.)
        
    Returns:
        float: Pitch shift ratio (1.0 = no change, 2.0 = octave up, 0.5 = octave down)
    """
    if from_note == to_note:
        return 1.0
    
    if from_note not in NOTE_FREQUENCIES or to_note not in NOTE_FREQUENCIES:
        print(f"Warning: Invalid notes '{from_note}' or '{to_note}'. Using no shift.")
        return 1.0
    
    from_freq = NOTE_FREQUENCIES[from_note]
    to_freq = NOTE_FREQUENCIES[to_note]
    
    return to_freq / from_freq


def shift_pitch_ffmpeg(input_file, output_file, pitch_ratio, ffmpeg_path=None):
    """
    Shift the pitch of an audio file using FFmpeg.
    
    Args:
        input_file (str): Path to input audio file
        output_file (str): Path to output audio file
        pitch_ratio (float): Pitch shift ratio (1.0 = no change)
        ffmpeg_path (str, optional): Path to FFmpeg executable
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Calculate the semitone shift
        # pitch_ratio = 2^(semitones/12)
        # semitones = 12 * log2(pitch_ratio)
        import math
        semitones = 12 * math.log2(pitch_ratio)
        
        # Build FFmpeg command
        ffmpeg_cmd = 'ffmpeg'
        if ffmpeg_path:
            ffmpeg_cmd = ffmpeg_path
        
        cmd = [
            ffmpeg_cmd, '-i', input_file,
            '-af', f'asetrate=44100*{pitch_ratio},aresample=44100',
            '-y', output_file
        ]
        
        # Run FFmpeg
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode != 0:
            print(f"FFmpeg error: {result.stderr}")
            return False
        
        return True
        
    except Exception as e:
        print(f"Error shifting pitch: {e}")
        return False


def shift_pitch_pydub(input_file, output_file, pitch_ratio):
    """
    Shift the pitch of an audio file using pydub.
    This is a fallback method if FFmpeg is not available.
    
    Args:
        input_file (str): Path to input audio file
        output_file (str): Path to output audio file
        pitch_ratio (float): Pitch shift ratio (1.0 = no change)
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Load audio
        audio = AudioSegment.from_file(input_file)
        
        # Apply pitch shift by changing the sample rate
        # This is a simplified approach - for better quality,
        # you'd want to use more sophisticated pitch shifting algorithms
        new_sample_rate = int(audio.frame_rate * pitch_ratio)
        shifted_audio = audio._spawn(audio.raw_data, overrides={'frame_rate': new_sample_rate})
        
        # Set the frame rate back to original
        shifted_audio = shifted_audio.set_frame_rate(audio.frame_rate)
        
        # Export
        shifted_audio.export(output_file, format='mp3')
        
        return True
        
    except Exception as e:
        print(f"Error shifting pitch with pydub: {e}")
        return False


def process_audio_with_pitch_shift(input_file, output_file, from_note, to_note, ffmpeg_path=None):
    """
    Process an audio file with pitch shifting from one note to another.
    
    Args:
        input_file (str): Path to input audio file
        output_file (str): Path to output audio file
        from_note (str): Source note (e.g., 'C', 'D', etc.)
        to_note (str): Target note (e.g., 'C', 'D', etc.)
        ffmpeg_path (str, optional): Path to FFmpeg executable
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Calculate pitch shift ratio
    pitch_ratio = calculate_pitch_shift(from_note, to_note)
    
    if pitch_ratio == 1.0:
        # No shift needed, just copy the file
        try:
            import shutil
            shutil.copy2(input_file, output_file)
            return True
        except Exception as e:
            print(f"Error copying file: {e}")
            return False
    
    # Try FFmpeg first (better quality)
    if shift_pitch_ffmpeg(input_file, output_file, pitch_ratio, ffmpeg_path):
        return True
    
    # Fallback to pydub
    print("FFmpeg not available, using pydub fallback...")
    return shift_pitch_pydub(input_file, output_file, pitch_ratio)


def get_note_names():
    """
    Get list of available note names for GUI.
    
    Returns:
        list: List of note names
    """
    return NOTE_NAMES.copy()


def validate_note(note):
    """
    Validate if a note name is valid.
    
    Args:
        note (str): Note name to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    return note in NOTE_FREQUENCIES


if __name__ == "__main__":
    # Test the pitch shifting functionality
    import sys
    
    if len(sys.argv) != 5:
        print("Usage: python pitch_shifter.py <input_file> <output_file> <from_note> <to_note>")
        print("Example: python pitch_shifter.py input.mp3 output.mp3 C D")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    from_note = sys.argv[3]
    to_note = sys.argv[4]
    
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        sys.exit(1)
    
    if not validate_note(from_note):
        print(f"Error: Invalid from_note '{from_note}'")
        sys.exit(1)
    
    if not validate_note(to_note):
        print(f"Error: Invalid to_note '{to_note}'")
        sys.exit(1)
    
    print(f"Shifting pitch from {from_note} to {to_note}...")
    
    if process_audio_with_pitch_shift(input_file, output_file, from_note, to_note):
        print("Pitch shifting completed successfully!")
    else:
        print("Pitch shifting failed!")
        sys.exit(1) 