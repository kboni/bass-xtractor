#!/usr/bin/env python3
"""
GUI for Bass Extractor - A graphical interface for extracting bass from audio files.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import sys
import platform
from pathlib import Path
import subprocess
import queue
import time

# Import the extract_bass functionality
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from extract_bass import extract_bass_from_file

# Import YouTube downloader
try:
    from youtube_downloader import (
        is_valid_youtube_url, 
        download_multiple_youtube_urls, 
        validate_youtube_urls
    )
    YOUTUBE_AVAILABLE = True
except ImportError:
    YOUTUBE_AVAILABLE = False

# Import pitch shifting functionality
try:
    from pitch_shifter import get_note_names, validate_note
    PITCH_SHIFT_AVAILABLE = True
    NOTE_NAMES = get_note_names()
except ImportError:
    PITCH_SHIFT_AVAILABLE = False
    NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']


class BassExtractorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Bass Xtractor GUI")
        self.root.geometry("730x700")  # Slightly larger default size
        self.root.resizable(True, True)
        self.root.minsize(730, 500) # Set minimum window size
        self.root.maxsize(730, 800) 
        
        # Bind cleanup on window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Configure style for better appearance
        self.style = ttk.Style()
        
        # Use appropriate theme for macOS
        if platform.system() == "Darwin":  # macOS
            self.style.theme_use('aqua')
        else:
            self.style.theme_use('clam')
        
        # Variables
        self.input_files = []
        self.youtube_urls = []
        self.output_folder = tk.StringVar()
        self.ffmpeg_path = tk.StringVar()
        self.no_cleanup = tk.BooleanVar()
        
        # Pitch shift variables
        self.input_pitch = tk.StringVar(value="C")
        self.output_pitch = tk.StringVar(value="C")
        self.enable_pitch_shift = tk.BooleanVar()
        
        # Message queue for thread communication
        self.message_queue = queue.Queue()
        
        self.create_widgets()
        self.setup_message_handling()
    
    def create_widgets(self):
        # Create a canvas with scrollbar
        canvas = tk.Canvas(self.root)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Bind mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Store the mousewheel function for cleanup
        self._on_mousewheel = _on_mousewheel
        
        # Configure grid weights for better space utilization
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=0)  # Scrollbar takes minimal space
        self.root.rowconfigure(0, weight=1)
        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Configure canvas to expand properly
        canvas.configure(width=800)  # Set a reasonable default width
        
        # Bind resize event to update canvas width
        def on_resize(event):
            canvas.configure(width=event.width - 20)  # Account for scrollbar width
        
        self.root.bind('<Configure>', on_resize)
        
        # Main frame inside scrollable frame
        main_frame = ttk.Frame(scrollable_frame, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure main frame grid weights for better space utilization
        main_frame.columnconfigure(0, weight=0)  # Labels
        main_frame.columnconfigure(1, weight=1)  # Input fields
        main_frame.columnconfigure(2, weight=0)  # Buttons
        main_frame.rowconfigure(5, weight=1)     # Log section
        
        # Title
        title_label = ttk.Label(main_frame, text="Bass Extractor", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Input section
        input_frame = ttk.LabelFrame(main_frame, text="Input Files & YouTube URLs", padding="10")
        input_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        input_frame.columnconfigure(0, weight=0)  # Labels
        input_frame.columnconfigure(1, weight=1)  # Input fields
        input_frame.columnconfigure(2, weight=0)  # Scrollbars
        
        # File selection
        ttk.Label(input_frame, text="Input Files:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        # File listbox
        self.file_listbox = tk.Listbox(input_frame, height=4, selectmode=tk.EXTENDED)
        self.file_listbox.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Scrollbar for file listbox
        file_scrollbar = ttk.Scrollbar(input_frame, orient=tk.VERTICAL, command=self.file_listbox.yview)
        file_scrollbar.grid(row=1, column=2, sticky=(tk.N, tk.S))
        self.file_listbox.configure(yscrollcommand=file_scrollbar.set)
        
        # File buttons frame
        file_buttons_frame = ttk.Frame(input_frame)
        file_buttons_frame.grid(row=2, column=0, columnspan=3, pady=(5, 0))
        
        ttk.Button(file_buttons_frame, text="Add Files", command=self.add_files).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(file_buttons_frame, text="Add Folder", command=self.add_folder).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(file_buttons_frame, text="Remove Selected", command=self.remove_files).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(file_buttons_frame, text="Clear All", command=self.clear_files).pack(side=tk.LEFT)
        
        # YouTube URLs section
        ttk.Label(input_frame, text="YouTube URLs:").grid(row=3, column=0, sticky=tk.W, pady=(10, 5))
        
        # YouTube URL text area
        self.youtube_text = scrolledtext.ScrolledText(input_frame, height=4, wrap=tk.WORD)
        self.youtube_text.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # YouTube buttons frame
        youtube_buttons_frame = ttk.Frame(input_frame)
        youtube_buttons_frame.grid(row=5, column=0, columnspan=3, pady=(5, 0))
        
        if YOUTUBE_AVAILABLE:
            ttk.Button(youtube_buttons_frame, text="Add YouTube URLs", command=self.add_youtube_urls).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(youtube_buttons_frame, text="Clear YouTube URLs", command=self.clear_youtube_urls).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Label(youtube_buttons_frame, text="(One URL per line)").pack(side=tk.LEFT, padx=(10, 0))
        else:
                                ttk.Label(youtube_buttons_frame, text="YouTube support not available. Install pytubefix: pip install pytubefix",
                     foreground="red").pack(side=tk.LEFT)
        
        # Output section
        output_frame = ttk.LabelFrame(main_frame, text="Output Settings", padding="10")
        output_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        output_frame.columnconfigure(0, weight=0)  # Labels
        output_frame.columnconfigure(1, weight=1)  # Input fields
        output_frame.columnconfigure(2, weight=0)  # Buttons
        
        # Output folder
        ttk.Label(output_frame, text="Output Folder:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        output_entry = ttk.Entry(output_frame, textvariable=self.output_folder)
        output_entry.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        ttk.Button(output_frame, text="Browse", command=self.browse_output_folder).grid(row=1, column=2, padx=(5, 0))
        
        # FFmpeg path
        ttk.Label(output_frame, text="FFmpeg Path (optional):").grid(row=2, column=0, sticky=tk.W, pady=(10, 5))
        ffmpeg_entry = ttk.Entry(output_frame, textvariable=self.ffmpeg_path)
        ffmpeg_entry.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        ttk.Button(output_frame, text="Browse", command=self.browse_ffmpeg).grid(row=3, column=2, padx=(5, 0))
        
        # Options
        options_frame = ttk.Frame(output_frame)
        options_frame.grid(row=4, column=0, columnspan=3, pady=(10, 0))
        
        ttk.Checkbutton(options_frame, text="Skip cleanup (preserve temporary files)", 
                       variable=self.no_cleanup).pack(anchor=tk.W)
        
        # Additional options frame
        additional_options_frame = ttk.LabelFrame(main_frame, text="Output Options", padding="10")
        additional_options_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Create a frame for checkboxes with better layout
        checkbox_frame = ttk.Frame(additional_options_frame)
        checkbox_frame.pack(fill=tk.X, expand=True)
        
        # First row of checkboxes
        row1_frame = ttk.Frame(checkbox_frame)
        row1_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.bassonly_var = tk.BooleanVar()
        ttk.Checkbutton(row1_frame, text="Bass Only (save to BASSONLY folder)", 
                       variable=self.bassonly_var).pack(side=tk.LEFT, padx=(0, 20))
        
        self.novocals_var = tk.BooleanVar()
        ttk.Checkbutton(row1_frame, text="No Vocals (save to NOVOCALS folder)", 
                       variable=self.novocals_var).pack(side=tk.LEFT, padx=(0, 20))
        
        # Second row of checkboxes
        row2_frame = ttk.Frame(checkbox_frame)
        row2_frame.pack(fill=tk.X)
        
        self.nodrums_var = tk.BooleanVar()
        ttk.Checkbutton(row2_frame, text="No Drums (save to NODRUMS folder)", 
                       variable=self.nodrums_var).pack(side=tk.LEFT, padx=(0, 20))
        
        self.noother_var = tk.BooleanVar()
        ttk.Checkbutton(row2_frame, text="No Other (save to NOOTHER folder)", 
                       variable=self.noother_var).pack(side=tk.LEFT, padx=(0, 20))
        
        # Pitch shift options frame
        pitch_shift_frame = ttk.LabelFrame(main_frame, text="Pitch Shift Options", padding="10")
        pitch_shift_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        pitch_shift_frame.columnconfigure(0, weight=0)  # Labels
        pitch_shift_frame.columnconfigure(1, weight=1)  # Dropdowns
        pitch_shift_frame.columnconfigure(2, weight=0)  # Spacing
        
        # Enable pitch shift checkbox
        ttk.Checkbutton(pitch_shift_frame, text="Enable Pitch Shifting", 
                       variable=self.enable_pitch_shift).grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))
        
        # Input pitch selection
        ttk.Label(pitch_shift_frame, text="Input Pitch:").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        input_pitch_combo = ttk.Combobox(pitch_shift_frame, textvariable=self.input_pitch, values=NOTE_NAMES, state="readonly", width=10)
        input_pitch_combo.grid(row=2, column=0, sticky=tk.W, pady=(0, 10))
        
        # Output pitch selection
        ttk.Label(pitch_shift_frame, text="Output Pitch:").grid(row=1, column=1, sticky=tk.W, padx=(20, 0), pady=(0, 5))
        output_pitch_combo = ttk.Combobox(pitch_shift_frame, textvariable=self.output_pitch, values=NOTE_NAMES, state="readonly", width=10)
        output_pitch_combo.grid(row=2, column=1, sticky=tk.W, padx=(20, 0), pady=(0, 10))
        
        # Pitch shift info
        if PITCH_SHIFT_AVAILABLE:
            ttk.Label(pitch_shift_frame, text="Shifts all tracks from input pitch to output pitch", 
                     foreground="gray").grid(row=3, column=0, columnspan=3, sticky=tk.W)
        else:
            ttk.Label(pitch_shift_frame, text="Pitch shifting not available", 
                     foreground="red").grid(row=3, column=0, columnspan=3, sticky=tk.W)
        
        # Progress section
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="10")
        progress_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        progress_frame.columnconfigure(0, weight=1)
        progress_frame.rowconfigure(1, weight=0)
        
        self.progress_var = tk.StringVar(value="Ready")
        ttk.Label(progress_frame, textvariable=self.progress_var).grid(row=0, column=0, sticky=tk.W)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # Log section
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding="10")
        log_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=3, pady=(10, 0))
        
        self.start_button = ttk.Button(button_frame, text="Start Processing", command=self.start_processing)
        self.start_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop_processing, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def setup_message_handling(self):
        """Setup message handling for thread communication"""
        self.check_message_queue()
    
    def check_message_queue(self):
        """Check for messages from the processing thread"""
        try:
            while True:
                message = self.message_queue.get_nowait()
                self.handle_message(message)
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.check_message_queue)
    
    def handle_message(self, message):
        """Handle messages from the processing thread"""
        if message['type'] == 'log':
            self.log_text.insert(tk.END, message['text'] + '\n')
            self.log_text.see(tk.END)
        elif message['type'] == 'progress':
            self.progress_var.set(message['text'])
        elif message['type'] == 'status':
            self.status_var.set(message['text'])
        elif message['type'] == 'complete':
            self.progress_bar.stop()
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.progress_var.set("Processing completed!")
            messagebox.showinfo("Complete", "Bass extraction completed successfully!")
        elif message['type'] == 'error':
            self.progress_bar.stop()
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.progress_var.set("Error occurred!")
            messagebox.showerror("Error", message['text'])
    
    def add_files(self):
        """Add individual files"""
        files = filedialog.askopenfilenames(
            title="Select MP3 files",
            filetypes=[("MP3 files", "*.mp3"), ("All files", "*.*")]
        )
        for file in files:
            if file not in self.input_files:
                self.input_files.append(file)
                self.file_listbox.insert(tk.END, os.path.basename(file))
        self.update_status()
    
    def add_folder(self):
        """Add all MP3 files from a folder"""
        folder = filedialog.askdirectory(title="Select folder containing MP3 files")
        if folder:
            mp3_files = list(Path(folder).glob("*.mp3"))
            for file in mp3_files:
                file_str = str(file)
                if file_str not in self.input_files:
                    self.input_files.append(file_str)
                    self.file_listbox.insert(tk.END, os.path.basename(file_str))
            self.update_status()
    
    def remove_files(self):
        """Remove selected files from the list"""
        selected_indices = self.file_listbox.curselection()
        for index in reversed(selected_indices):
            self.file_listbox.delete(index)
            del self.input_files[index]
        self.update_status()
    
    def clear_files(self):
        """Clear all files from the list"""
        self.input_files.clear()
        self.file_listbox.delete(0, tk.END)
        self.update_status()
    
    def add_youtube_urls(self):
        """Add YouTube URLs from the text area"""
        if not YOUTUBE_AVAILABLE:
            messagebox.showerror("Error", "YouTube support not available. Please install pytubefix: pip install pytubefix")
            return
        
        # Get URLs from text area
        urls_text = self.youtube_text.get(1.0, tk.END).strip()
        if not urls_text:
            messagebox.showwarning("Warning", "Please enter YouTube URLs first!")
            return
        
        # Split by lines and filter empty lines
        urls = [url.strip() for url in urls_text.split('\n') if url.strip()]
        
        # Validate URLs
        valid_urls, invalid_urls = validate_youtube_urls(urls)
        
        if invalid_urls:
            invalid_list = '\n'.join(invalid_urls[:5])  # Show first 5 invalid URLs
            if len(invalid_urls) > 5:
                invalid_list += f"\n... and {len(invalid_urls) - 5} more"
            messagebox.showwarning("Warning", f"Some URLs are invalid:\n{invalid_list}")
        
        if not valid_urls:
            messagebox.showwarning("Warning", "No valid YouTube URLs found!")
            return
        
        # Add valid URLs to the list
        for url in valid_urls:
            if url not in self.youtube_urls:
                self.youtube_urls.append(url)
        
        # Update the text area to show only valid URLs
        self.youtube_text.delete(1.0, tk.END)
        self.youtube_text.insert(1.0, '\n'.join(self.youtube_urls))
        
        self.update_status()
        messagebox.showinfo("Success", f"Added {len(valid_urls)} valid YouTube URLs")
    
    def clear_youtube_urls(self):
        """Clear all YouTube URLs"""
        self.youtube_urls.clear()
        self.youtube_text.delete(1.0, tk.END)
        self.update_status()
    
    def browse_output_folder(self):
        """Browse for output folder"""
        folder = filedialog.askdirectory(title="Select output folder")
        if folder:
            self.output_folder.set(folder)
    
    def browse_ffmpeg(self):
        """Browse for FFmpeg executable"""
        # Set appropriate file types based on platform
        if platform.system() == "Darwin":  # macOS
            filetypes = [("Executable files", "*"), ("All files", "*.*")]
        elif platform.system() == "Windows":
            filetypes = [("Executable files", "*.exe"), ("All files", "*.*")]
        else:  # Linux
            filetypes = [("Executable files", "*"), ("All files", "*.*")]
        
        file = filedialog.askopenfilename(
            title="Select FFmpeg executable",
            filetypes=filetypes
        )
        if file:
            self.ffmpeg_path.set(file)
    
    def update_status(self):
        """Update status bar with file count"""
        file_count = len(self.input_files)
        youtube_count = len(self.youtube_urls)
        total_count = file_count + youtube_count
        
        if file_count > 0 and youtube_count > 0:
            self.status_var.set(f"Ready - {file_count} file(s) + {youtube_count} YouTube URL(s) selected")
        elif file_count > 0:
            self.status_var.set(f"Ready - {file_count} file(s) selected")
        elif youtube_count > 0:
            self.status_var.set(f"Ready - {youtube_count} YouTube URL(s) selected")
        else:
            self.status_var.set("Ready - No files or URLs selected")
    
    def cleanup(self):
        """Clean up event bindings"""
        if hasattr(self, '_on_mousewheel'):
            self.root.unbind_all("<MouseWheel>")
    
    def on_closing(self):
        """Handle window closing"""
        self.cleanup()
        self.root.destroy()
    
    def start_processing(self):
        """Start the processing thread"""
        if not self.input_files and not self.youtube_urls:
            messagebox.showwarning("Warning", "Please select input files or YouTube URLs first!")
            return
        
        if not self.output_folder.get():
            messagebox.showwarning("Warning", "Please select an output folder!")
            return
        
        # Clear log
        self.log_text.delete(1.0, tk.END)
        
        # Start processing thread
        self.processing_thread = threading.Thread(target=self.process_files)
        self.processing_thread.daemon = True
        self.processing_thread.start()
        
        # Update UI
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.progress_bar.start()
        self.progress_var.set("Processing...")
    
    def stop_processing(self):
        """Stop the processing (placeholder for future implementation)"""
        self.progress_var.set("Stopping...")
        # TODO: Implement proper thread stopping mechanism
    
    def process_files(self):
        """Process files in a separate thread"""
        try:
            all_files = self.input_files.copy()
            youtube_download_success = False
            
            # Download YouTube videos if any
            if self.youtube_urls and YOUTUBE_AVAILABLE:
                self.message_queue.put({
                    'type': 'log',
                    'text': f"Starting YouTube download for {len(self.youtube_urls)} URLs..."
                })
                
                self.message_queue.put({
                    'type': 'progress',
                    'text': f"Downloading {len(self.youtube_urls)} YouTube video(s)..."
                })
                
                try:
                    # Download YouTube videos
                    downloaded_files = download_multiple_youtube_urls(
                        self.youtube_urls, 
                        self.output_folder.get(), 
                        self.ffmpeg_path.get() if self.ffmpeg_path.get() else None
                    )
                    
                    self.message_queue.put({
                        'type': 'log',
                        'text': f"Download completed. Got {len(downloaded_files)} files: {downloaded_files}"
                    })
                    
                    # Add downloaded files to the processing list
                    all_files.extend(downloaded_files)
                    youtube_download_success = True
                    
                    self.message_queue.put({
                        'type': 'log',
                        'text': f"✓ Downloaded {len(downloaded_files)} YouTube video(s)"
                    })
                    
                except Exception as e:
                    error_msg = str(e)
                    self.message_queue.put({
                        'type': 'log',
                        'text': f"✗ Error downloading YouTube videos: {error_msg}"
                    })
                    
                    # Check if it's a pytubefix issue
                    if "HTTP Error 400" in error_msg or "Bad Request" in error_msg:
                        self.message_queue.put({
                            'type': 'log',
                            'text': "💡 Tip: Try updating pytubefix: pip install --upgrade pytubefix"
                        })
                    
                    self.message_queue.put({
                        'type': 'log',
                        'text': "⚠️ Continuing with local files only (if any)"
                    })
                    # Continue with local files only
            elif self.youtube_urls and not YOUTUBE_AVAILABLE:
                self.message_queue.put({
                    'type': 'log',
                    'text': f"⚠️ YouTube URLs provided ({len(self.youtube_urls)}) but pytube not available. Skipping YouTube downloads."
                })
            
            # Process all files (local + downloaded)
            total_files = len(all_files)
            
            # Debug logging
            self.message_queue.put({
                'type': 'log',
                'text': f"Debug: {len(self.input_files)} local files, {len(self.youtube_urls)} YouTube URLs, {total_files} total files to process"
            })
            
            # Check if we have anything to process
            if total_files == 0:
                if self.youtube_urls and not youtube_download_success:
                    self.message_queue.put({
                        'type': 'error',
                        'text': "YouTube download failed and no local files provided. No files to process."
                    })
                elif self.youtube_urls and youtube_download_success:
                    self.message_queue.put({
                        'type': 'error',
                        'text': "YouTube download completed but no files were downloaded. No files to process."
                    })
                else:
                    self.message_queue.put({
                        'type': 'error',
                        'text': "No files to process"
                    })
                return
            
            for i, file_path in enumerate(all_files, 1):
                # Check if processing was stopped
                if hasattr(self, 'stop_processing_flag') and self.stop_processing_flag:
                    break
                
                # Update progress
                self.message_queue.put({
                    'type': 'progress',
                    'text': f"Processing file {i}/{total_files}: {os.path.basename(file_path)}"
                })
                
                # Process the file
                try:
                    # Set FFmpeg path if provided
                    if self.ffmpeg_path.get():
                        from pydub import AudioSegment
                        AudioSegment.converter = self.ffmpeg_path.get()
                    
                    # Get pitch shift parameters
                    input_pitch = None
                    output_pitch = None
                    if self.enable_pitch_shift.get() and PITCH_SHIFT_AVAILABLE:
                        input_pitch = self.input_pitch.get()
                        output_pitch = self.output_pitch.get()
                    
                    # Extract bass
                    extract_bass_from_file(file_path, self.output_folder.get(), self.no_cleanup.get(), 
                                        self.novocals_var.get(), self.nodrums_var.get(), self.noother_var.get(), 
                                        self.bassonly_var.get(), input_pitch, output_pitch, 
                                        self.ffmpeg_path.get() if self.ffmpeg_path.get() else None)
                    
                    self.message_queue.put({
                        'type': 'log',
                        'text': f"✓ Completed: {os.path.basename(file_path)}"
                    })
                    
                except Exception as e:
                    self.message_queue.put({
                        'type': 'log',
                        'text': f"✗ Error processing {os.path.basename(file_path)}: {str(e)}"
                    })
            
            # Complete
            self.message_queue.put({'type': 'complete'})
            
        except Exception as e:
            self.message_queue.put({
                'type': 'error',
                'text': f"Processing error: {str(e)}"
            })


def main():
    """Main function to run the GUI"""
    root = tk.Tk()
    
    # macOS specific configurations
    if platform.system() == "Darwin":
        # Set the dock icon (optional)
        try:
            root.tk.call('wm', 'iconphoto', root._w, tk.PhotoImage(file='icon.png'))
        except:
            pass  # Icon file not found, continue without it
        
        # Ensure the window appears above other windows initially
        root.lift()
        root.attributes('-topmost', True)
        root.after_idle(root.attributes, '-topmost', False)
    
    app = BassExtractorGUI(root)
    
    # Center the window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()


if __name__ == "__main__":
    main() 