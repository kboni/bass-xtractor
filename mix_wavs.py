from pydub import AudioSegment

# (Make sure FFmpeg is installed and on your PATH,
# or set AudioSegment.converter = "/full/path/to/ffmpeg")

# Load your files
def mix_wavs(bass_path, drums_path, vocals_path, other_path, song_name, output_folder, novocals=False, nodrums=False, noother=False, bassonly=False):
  bass   = AudioSegment.from_wav(bass_path)
  drums   = AudioSegment.from_wav(drums_path)
  vocals  = AudioSegment.from_wav(vocals_path)
  other   = AudioSegment.from_wav(other_path)

  # The basic behaviour is to remove the bass from the original track
  # Pad to same length
  max_len_nobass = max(len(drums), len(vocals), len(other))
  drums_nobass  = drums + AudioSegment.silent(max_len_nobass - len(drums))
  vocals_nobass = vocals + AudioSegment.silent(max_len_nobass - len(vocals))
  other_nobass  = other + AudioSegment.silent(max_len_nobass - len(other))

  # Overlay
  mixed_nobass = drums_nobass.overlay(vocals_nobass).overlay(other_nobass)

  # Export NOBASS version (drums + vocals + other)
  # Create subfolders
  import os
  nobass_folder = os.path.join(output_folder, "NOBASS")
  os.makedirs(nobass_folder, exist_ok=True)

  # Export NOBASS version (drums + vocals + other)
  mixed_nobass.export(os.path.join(nobass_folder, f"{song_name}.mp3"), format="mp3", bitrate="192k")

  if bassonly:
    bassonly_folder = os.path.join(output_folder, "BASSONLY")
    os.makedirs(bassonly_folder, exist_ok=True)
    bass.export(os.path.join(bassonly_folder, f"{song_name}.mp3"), format="mp3", bitrate="192k")

  if novocals:
    max_len_novocals = max(len(drums), len(bass), len(other))
    drums_novocals  = drums + AudioSegment.silent(max_len_novocals - len(drums))
    bass_novocals = bass + AudioSegment.silent(max_len_novocals - len(bass))
    other_novocals  = other + AudioSegment.silent(max_len_novocals - len(other))

    mixed_novocals = drums_novocals.overlay(bass_novocals).overlay(other_novocals)# Overlay

    novocals_folder = os.path.join(output_folder, "NOVOCALS")
    os.makedirs(novocals_folder, exist_ok=True)
    mixed_novocals.export(os.path.join(novocals_folder, f"{song_name}.mp3"), format="mp3", bitrate="192k")

  if nodrums:
    max_len_nodrums = max(len(bass), len(vocals), len(other))
    bass_nodrums = bass + AudioSegment.silent(max_len_nodrums - len(bass))
    vocals_nodrums = vocals + AudioSegment.silent(max_len_nodrums - len(vocals))
    other_nodrums  = other + AudioSegment.silent(max_len_nodrums - len(other))

    mixed_nodrums = bass_nodrums.overlay(vocals_nodrums).overlay(other_nodrums) 

    nodrums_folder = os.path.join(output_folder, "NODRUMS")
    os.makedirs(nodrums_folder, exist_ok=True)
    mixed_nodrums.export(os.path.join(nodrums_folder, f"{song_name}.mp3"), format="mp3", bitrate="192k")

  if noother: 
    max_len_noother = max(len(bass), len(vocals), len(drums))
    bass_noother = bass + AudioSegment.silent(max_len_noother - len(bass))
    vocals_noother = vocals + AudioSegment.silent(max_len_noother - len(vocals))
    drums_noother = drums + AudioSegment.silent(max_len_noother - len(drums))

    mixed_noother = bass_noother.overlay(vocals_noother).overlay(drums_noother) 

    noother_folder = os.path.join(output_folder, "NOOTHER")
    os.makedirs(noother_folder, exist_ok=True)
    mixed_noother.export(os.path.join(noother_folder, f"{song_name}.mp3"), format="mp3", bitrate="192k")
  
