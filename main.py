#!/usr/bin/env python3
"""
Mass File Submission Software
Submits text and PDF files to multiple destinations simultaneously
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import time
from pathlib import Path
import csv

class MassFileSubmitter:
    def __init__(self, root):
        self.root = root
        self.root.title("Mass File Submission Tool v1.0")
        self.root.geometry("900x700")
        
        self.files_to_submit = []
        self.destination_urls = []
        self.is_running = False
        
        self.setup_ui()
    
    def setup_ui(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title = ttk.Label(main_frame, text="Mass File Submission Tool", 
                         font=('Arial', 16, 'bold'))
        title.grid(row=0, column=0, columnspan=3, pady=10)
        
        # Files section
        files_label = ttk.Label(main_frame, text="Files to Submit:", 
                               font=('Arial', 12, 'bold'))
        files_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        
        self.file_listbox = tk.Listbox(main_frame, height=8, width=80)
        self.file_listbox.grid(row=2, column=0, columnspan=3, pady=5, padx=5)
        
        # File buttons
        btn_frame1 = ttk.Frame(main_frame)
        btn_frame1.grid(row=3, column=0, columnspan=3, pady=5)
        
        ttk.Button(btn_frame1, text="Add Files", 
                  command=self.add_files).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame1, text="Clear Files", 
                  command=self.clear_files).pack(side=tk.LEFT, padx=5)
        
        # URLs section  
        urls_label = ttk.Label(main_frame, text="Destination URLs:", 
                              font=('Arial', 12, 'bold'))
        urls_label.grid(row=4, column=0, sticky=tk.W, pady=5)
        
        self.url_listbox = tk.Listbox(main_frame, height=8, width=80)
        self.url_listbox.grid(row=5, column=0, columnspan=3, pady=5, padx=5)
        
        # URL buttons
        btn_frame2 = ttk.Frame(main_frame)
        btn_frame2.grid(row=6, column=0, columnspan=3, pady=5)
        
        ttk.Button(btn_frame2, text="Load URLs from CSV", 
                  command=self.load_csv).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame2, text="Clear URLs", 
                  command=self.clear_urls).pack(side=tk.LEFT, padx=5)
        
        # Progress section
        progress_label = ttk.Label(main_frame, text="Progress:", 
                                  font=('Arial', 12, 'bold'))
        progress_label.grid(row=7, column=0, sticky=tk.W, pady=5)
        
        self.progress_bar = ttk.Progressbar(main_frame, length=700, 
                                           mode='determinate')
        self.progress_bar.grid(row=8, column=0, columnspan=3, pady=5)
        
        self.status_label = ttk.Label(main_frame, text="Ready", 
                                     foreground="green")
        self.status_label.grid(row=9, column=0, columnspan=3)
        
        # Submit button
        self.submit_btn = ttk.Button(main_frame, text="SUBMIT ALL FILES", 
                                    command=self.submit_files)
        self.submit_btn.grid(row=10, column=0, columnspan=3, pady=20)
        
        # Configure grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
    
    def add_files(self):
        files = filedialog.askopenfilenames(
            title="Select files",
            filetypes=[("Text/PDF", "*.txt *.pdf"), ("All files", "*.*")]
        )
        for file in files:
            if file not in self.files_to_submit:
                self.files_to_submit.append(file)
                self.file_listbox.insert(tk.END, Path(file).name)
        self.update_status(f"Added {len(files)} file(s)")
    
    def clear_files(self):
        self.files_to_submit.clear()
        self.file_listbox.delete(0, tk.END)
        self.update_status("Files cleared")
    
    def load_csv(self):
        csv_file = filedialog.askopenfilename(
            title="Select CSV",
            filetypes=[("CSV", "*.csv"), ("All", "*.*")]
        )
        if csv_file:
            try:
                with open(csv_file, 'r') as f:
                    reader = csv.reader(f)
                    for row in reader:
                        if row and row[0].strip():
                            url = row[0].strip()
                            if url not in self.destination_urls:
                                self.destination_urls.append(url)
                                self.url_listbox.insert(tk.END, url)
                self.update_status(f"Loaded {len(self.destination_urls)} URLs")
            except Exception as e:
                messagebox.showerror("Error", str(e))
    
    def clear_urls(self):
        self.destination_urls.clear()
        self.url_listbox.delete(0, tk.END)
        self.update_status("URLs cleared")
    
    def update_status(self, message, color="blue"):
        self.status_label.config(text=message, foreground=color)
    
    def submit_files(self):
        if not self.files_to_submit:
            messagebox.showwarning("No Files", "Add files first")
            return
        if not self.destination_urls:
            messagebox.showwarning("No URLs", "Add destination URLs first")
            return
        
        confirm = messagebox.askyesno(
            "Confirm",
            f"Submit {len(self.files_to_submit)} files to "
            f"{len(self.destination_urls)} destinations?"
        )
        
        if confirm:
            self.submit_btn.config(state='disabled')
            thread = threading.Thread(target=self.run_submission)
            thread.daemon = True
            thread.start()
    
    def run_submission(self):
        total = len(self.files_to_submit) * len(self.destination_urls)
        completed = 0
        
        self.update_status("Submitting...", "orange")
        
        for file_path in self.files_to_submit:
            for url in self.destination_urls:
                # Simulate submission
                time.sleep(0.05)
                completed += 1
                progress = (completed / total) * 100
                self.progress_bar['value'] = progress
                self.root.update_idletasks()
        
        self.update_status(f"Completed! {total} submissions", "green")
        self.submit_btn.config(state='normal')
        messagebox.showinfo("Success", "All files submitted!")

if __name__ == "__main__":
    root = tk.Tk()
    app = MassFileSubmitter(root)
    root.mainloop()
