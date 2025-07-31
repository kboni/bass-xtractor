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

  # Export as MP3 to output folder
  import os
  os.makedirs(output_folder, exist_ok=True)
  mixed.export(os.path.join(output_folder, f"{song_name}[NOBASS].mp3"), format="mp3", bitrate="192k")

  # Move bass to output folder and rename
  bass_audio = AudioSegment.from_wav(bass_path)
  bass_audio.export(os.path.join(output_folder, f"{song_name}[BASSONLY].mp3"), format="mp3", bitrate="192k")
