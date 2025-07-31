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


class BassExtractorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Bass Extractor GUI")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Configure style for better appearance
        self.style = ttk.Style()
        
        # Use appropriate theme for macOS
        if platform.system() == "Darwin":  # macOS
            self.style.theme_use('aqua')
        else:
            self.style.theme_use('clam')
        
        # Variables
        self.input_files = []
        self.output_folder = tk.StringVar()
        self.ffmpeg_path = tk.StringVar()
        self.no_cleanup = tk.BooleanVar()
        
        # Message queue for thread communication
        self.message_queue = queue.Queue()
        
        self.create_widgets()
        self.setup_message_handling()
    
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Bass Extractor", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Input section
        input_frame = ttk.LabelFrame(main_frame, text="Input Files", padding="10")
        input_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        input_frame.columnconfigure(1, weight=1)
        
        # File selection
        ttk.Label(input_frame, text="Input Files:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        # File listbox
        self.file_listbox = tk.Listbox(input_frame, height=6, selectmode=tk.EXTENDED)
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
        
        # Output section
        output_frame = ttk.LabelFrame(main_frame, text="Output Settings", padding="10")
        output_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        output_frame.columnconfigure(1, weight=1)
        
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
        
        # Progress section
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="10")
        progress_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress_var = tk.StringVar(value="Ready")
        ttk.Label(progress_frame, textvariable=self.progress_var).grid(row=0, column=0, sticky=tk.W)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # Log section
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding="10")
        log_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=(10, 0))
        
        self.start_button = ttk.Button(button_frame, text="Start Processing", command=self.start_processing)
        self.start_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop_processing, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
    
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
        count = len(self.input_files)
        self.status_var.set(f"Ready - {count} file(s) selected")
    
    def start_processing(self):
        """Start the processing thread"""
        if not self.input_files:
            messagebox.showwarning("Warning", "Please select input files first!")
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
            total_files = len(self.input_files)
            
            for i, file_path in enumerate(self.input_files, 1):
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
                    
                    # Extract bass
                    extract_bass_from_file(file_path, self.output_folder.get(), self.no_cleanup.get())
                    
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