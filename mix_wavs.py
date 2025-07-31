from pydub import AudioSegment

# (Make sure FFmpeg is installed and on your PATH,
# or set AudioSegment.converter = "/full/path/to/ffmpeg")

# Load your files
def mix_wavs(bass_path, drums_path, vocals_path, other_path, song_name, output_folder):
  drums   = AudioSegment.from_wav(drums_path)
  vocals  = AudioSegment.from_wav(vocals_path)
  other   = AudioSegment.from_wav(other_path)

  # Pad to same length
  max_len = max(len(drums), len(vocals), len(other))
  drums  += AudioSegment.silent(max_len - len(drums))
  vocals += AudioSegment.silent(max_len - len(vocals))
  other  += AudioSegment.silent(max_len - len(other))

  # Overlay
  mixed = drums.overlay(vocals).overlay(other)

  # Create subfolders
  import os
  nobass_folder = os.path.join(output_folder, "NOBASS")
  bassonly_folder = os.path.join(output_folder, "BASSONLY")
  os.makedirs(nobass_folder, exist_ok=True)
  os.makedirs(bassonly_folder, exist_ok=True)

  # Export NOBASS version (drums + vocals + other)
  mixed.export(os.path.join(nobass_folder, f"{song_name}.mp3"), format="mp3", bitrate="192k")

  # Export BASSONLY version (bass only)
  bass_audio = AudioSegment.from_wav(bass_path)
  bass_audio.export(os.path.join(bassonly_folder, f"{song_name}.mp3"), format="mp3", bitrate="192k")
