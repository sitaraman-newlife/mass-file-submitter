import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import requests
from pathlib import Path
import threading

class MassFileSubmitter:
    def __init__(self, root):
        self.root = root
        self.root.title("Mass File Submitter")
        self.root.geometry("900x750")
        
        # Data storage
        self.credentials = []
        self.current_cred_index = 0
        self.files_to_submit = []
        self.is_running = False
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main container with scrollbar
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Credentials section
        cred_frame = ttk.LabelFrame(main_frame, text="Credentials", padding="10")
        cred_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(cred_frame, text="URL:").grid(row=0, column=0, sticky=tk.W)
        url_entry = ttk.Entry(cred_frame, width=50)
        url_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(cred_frame, text="Username:").grid(row=1, column=0, sticky=tk.W)
        user_entry = ttk.Entry(cred_frame, width=50)
        user_entry.grid(row=1, column=1, padx=5)
        
        ttk.Label(cred_frame, text="Password:").grid(row=2, column=0, sticky=tk.W)
        pass_entry = ttk.Entry(cred_frame, width=50, show="*")
        pass_entry.grid(row=2, column=1, padx=5)
        
        ttk.Label(cred_frame, text="Headers (JSON):").grid(row=3, column=0, sticky=tk.W)
        head_entry = ttk.Entry(cred_frame, width=50)
        head_entry.grid(row=3, column=1, padx=5)
        
        def add_credential():
            if url_entry.get() and user_entry.get() and pass_entry.get():
                cred = {
                    "url": url_entry.get(),
                    "username": user_entry.get(),
                    "password": pass_entry.get()
                }
                cred["headers"] = json.loads(head_entry.get().strip() or "{}")
                self.credentials.append(cred)
                self.update_cred_list()
                url_entry.delete(0, tk.END)
                user_entry.delete(0, tk.END)
                pass_entry.delete(0, tk.END)
                head_entry.delete(0, tk.END)
            else:
                messagebox.showwarning("Input Error", "Please fill all required fields")
        
        ttk.Button(cred_frame, text="Add Credential", command=add_credential).grid(row=4, column=1, pady=5)
        
        # Credentials list
        list_frame = ttk.Frame(main_frame)
        list_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.cred_listbox = tk.Listbox(list_frame, height=4)
        self.cred_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E))
        list_frame.columnconfigure(0, weight=1)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.cred_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.cred_listbox.config(yscrollcommand=scrollbar.set)
        
        # Files section
        files_frame = ttk.LabelFrame(main_frame, text="Files to Submit", padding="10")
        files_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        def select_files():
            files = filedialog.askopenfilenames()
            if files:
                self.files_to_submit.extend(files)
                self.update_file_list()
        
        ttk.Button(files_frame, text="Select Files", command=select_files).grid(row=0, column=0, pady=5)
        
        self.file_listbox = tk.Listbox(files_frame, height=4)
        self.file_listbox.grid(row=1, column=0, sticky=(tk.W, tk.E))
        files_frame.columnconfigure(0, weight=1)
        
        file_scrollbar = ttk.Scrollbar(files_frame, orient=tk.VERTICAL, command=self.file_listbox.yview)
        file_scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.file_listbox.config(yscrollcommand=file_scrollbar.set)
        
        # Progress section
        self.progress_label = ttk.Label(main_frame, text="Ready")
        self.progress_label.grid(row=3, column=0, columnspan=2, pady=5)
        
        self.progress_bar = ttk.Progressbar(main_frame, mode='determinate')
        self.progress_bar.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.status_label = ttk.Label(main_frame, text="")
        self.status_label.grid(row=5, column=0, columnspan=2, pady=5)
        
        # Output section
        output_frame = ttk.LabelFrame(main_frame, text="Output Log", padding="10")
        output_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        main_frame.rowconfigure(6, weight=1)
        
        self.output_text = tk.Text(output_frame, height=6, wrap=tk.WORD)
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        
        output_scrollbar = ttk.Scrollbar(output_frame, orient=tk.VERTICAL, command=self.output_text.yview)
        output_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.output_text.config(yscrollcommand=output_scrollbar.set)
        
        # Submit button - now more visible with better positioning
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=10)
        
        self.submit_button = ttk.Button(button_frame, text="Start Submission", command=self.start_submission)
        self.submit_button.pack(pady=5)
        
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
    
    def update_cred_list(self):
        self.cred_listbox.delete(0, tk.END)
        for i, cred in enumerate(self.credentials):
            self.cred_listbox.insert(tk.END, f"{i+1}. {cred['username']} - {cred['url']}")
    
    def update_file_list(self):
        self.file_listbox.delete(0, tk.END)
        for file in self.files_to_submit:
            self.file_listbox.insert(tk.END, os.path.basename(file))
    
    def log_output(self, message):
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.see(tk.END)
    
    def start_submission(self):
        if not self.credentials:
            messagebox.showerror("Error", "No credentials added")
            return
        
        if not self.files_to_submit:
            messagebox.showerror("Error", "No files selected")
            return
        
        self.is_running = True
        self.submit_button.config(state='disabled', text="Submitting...")
        
        thread = threading.Thread(target=self.process_submissions)
        thread.start()
    
    def process_submissions(self):
        total = len(self.credentials) * len(self.files_to_submit)
        completed = 0
        
        for cred in self.credentials:
            for file_path in self.files_to_submit:
                if not self.is_running:
                    break
                
                self.submit_file(cred, file_path)
                completed += 1
                
                progress = (completed / total) * 100
                self.progress_bar['value'] = progress
                self.status_label.config(text=f"Progress: {completed}/{total} submissions completed")
                self.root.update_idletasks()
        
        self.submit_button.config(state='normal', text="Start Submission")
        self.is_running = False
        messagebox.showinfo("Complete", "All submissions processed!")
    
    def submit_file(self, cred, file_path):
        try:
            self.log_output(f"Submitting {os.path.basename(file_path)} to {cred['url']}...")
            
            with open(file_path, 'rb') as f:
                files = {'file': f}
                data = {
                    'username': cred['username'],
                    'password': cred['password']
                }
                
                response = requests.post(
                    cred['url'],
                    files=files,
                    data=data,
                    headers=cred.get('headers', {}),
                    timeout=30
                )
                
                if response.status_code == 200:
                    self.log_output(f"✓ Success: {os.path.basename(file_path)}")
                else:
                    self.log_output(f"✗ Failed: {os.path.basename(file_path)} - Status {response.status_code}")
        
        except Exception as e:
            self.log_output(f"✗ Error: {os.path.basename(file_path)} - {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = MassFileSubmitter(root)
    root.mainloop()
