# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['gui\\extract_bass_gui.py'],
    pathex=[],
    binaries=[],
    datas=[('extract_bass.py', '.'), ('youtube_downloader.py', '.'), ('mix_wavs.py', '.')],
    hiddenimports=['pydub', 'pytubefix', 'tkinter', 'threading', 'queue', 'pathlib', 'subprocess', 'shutil', 'datetime', 'logging', 're', 'urllib'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tensorflow', 'spleeter', 'librosa', 'soundfile', 'scipy', 'numpy', 'sklearn', 'yaml', 'requests', 'tqdm', 'ffmpeg'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='BassExtractorGUI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
