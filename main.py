import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import requests
import threading
import time
from pathlib import Path
from cryptography.fernet import Fernet

class MassFileSubmitter:
    def __init__(self, root):
        self.root = root
        self.root.title("Mass File Submitter")
        self.root.geometry("950x850")

        self.credentials = []
        self.current_cred_index = 0
        self.files_to_submit = []
        self.is_running = False
        self.delay_seconds = 2
        self.max_retries = 3

        self.setup_ui()

    def setup_ui(self):
        # Create a canvas with scrollbar
        canvas = tk.Canvas(self.root)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, padding="10")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Enable mousewheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Now use scrollable_frame instead of main_frame
        main_frame = scrollable_frame
        # --- Credentials Section ---
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
                try:
                    cred["headers"] = json.loads(head_entry.get().strip() or "{}")
                except Exception:
                    messagebox.showerror("Input Error", "Invalid JSON in Headers")
                    return
                self.credentials.append(cred)
                self.update_cred_list()
                url_entry.delete(0, tk.END)
                user_entry.delete(0, tk.END)
                pass_entry.delete(0, tk.END)
                head_entry.delete(0, tk.END)
            else:
                messagebox.showwarning("Input Error", "Please fill all required fields")

        ttk.Button(cred_frame, text="Add Credential", command=add_credential).grid(row=4, column=1, pady=5)
        ttk.Button(cred_frame, text="Save Credentials", command=self.save_credentials).grid(row=5, column=0, pady=5)
        ttk.Button(cred_frame, text="Load Credentials", command=self.load_credentials).grid(row=5, column=1, pady=5)
        ttk.Button(cred_frame, text="Clear Credentials", command=self.clear_credentials).grid(row=6, column=0, columnspan=2, pady=5)

        list_frame = ttk.Frame(main_frame)
        list_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        self.cred_listbox = tk.Listbox(list_frame, height=4)
        self.cred_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E))
        list_frame.columnconfigure(0, weight=1)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.cred_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.cred_listbox.config(yscrollcommand=scrollbar.set)

        # --- Files Section ---
        files_frame = ttk.LabelFrame(main_frame, text="Files to Submit", padding="10")
        files_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        def select_files():
            files = filedialog.askopenfilenames()
            if files:
                self.files_to_submit.extend(files)
                self.update_file_list()
        ttk.Button(files_frame, text="Select Files", command=select_files).grid(row=0, column=0, pady=5)
        ttk.Button(files_frame, text="Clear Files", command=self.clear_files).grid(row=0, column=1, padx=5)
        self.file_listbox = tk.Listbox(files_frame, height=4)
        self.file_listbox.grid(row=1, column=0, sticky=(tk.W, tk.E))
        files_frame.columnconfigure(0, weight=1)
        file_scrollbar = ttk.Scrollbar(files_frame, orient=tk.VERTICAL, command=self.file_listbox.yview)
        file_scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.file_listbox.config(yscrollcommand=file_scrollbar.set)

        # --- Anti-throttle options ---
        throttle_frame = ttk.LabelFrame(main_frame, text="Anti-Throttle & Retry Config", padding="10")
        throttle_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        ttk.Label(throttle_frame, text="Delay between submissions (seconds):").grid(row=0, column=0, sticky=tk.W)
        delay_spin = tk.Spinbox(throttle_frame, from_=1, to=30, width=5)
        delay_spin.grid(row=0, column=1, sticky=(tk.W), padx=5)
        delay_spin.delete(0, tk.END)
        delay_spin.insert(0, str(self.delay_seconds))
        ttk.Label(throttle_frame, text="Max retries per file:").grid(row=0, column=2, sticky=tk.W)
        retry_spin = tk.Spinbox(throttle_frame, from_=1, to=10, width=5)
        retry_spin.grid(row=0, column=3, sticky=(tk.W), padx=5)
        retry_spin.delete(0, tk.END)
        retry_spin.insert(0, str(self.max_retries))
        def update_throttle_settings():
            self.delay_seconds = int(delay_spin.get())
            self.max_retries = int(retry_spin.get())
        ttk.Button(throttle_frame, text="Set", command=update_throttle_settings).grid(row=0, column=4, padx=5)

        self.progress_label = ttk.Label(main_frame, text="Ready")
        self.progress_label.grid(row=4, column=0, columnspan=2, pady=5)
        self.progress_bar = ttk.Progressbar(main_frame, mode='determinate')
        self.progress_bar.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        self.status_label = ttk.Label(main_frame, text="")
        self.status_label.grid(row=6, column=0, columnspan=2, pady=5)

        output_frame = ttk.LabelFrame(main_frame, text="Output Log", padding="10")
        output_frame.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        main_frame.rowconfigure(7, weight=1)
        self.output_text = tk.Text(output_frame, height=8, wrap=tk.WORD)
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        output_scrollbar = ttk.Scrollbar(output_frame, orient=tk.VERTICAL, command=self.output_text.yview)
        output_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.output_text.config(yscrollcommand=output_scrollbar.set)

        # --- Status label for last file status ---
        self.last_status_label = ttk.Label(main_frame, text="Last file status:")
        self.last_status_label.grid(row=8, column=0, columnspan=2, pady=5)

        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=9, column=0, columnspan=2, pady=10)
        self.submit_button = ttk.Button(button_frame, text="Start Submission", command=self.start_submission)
        self.submit_button.pack(pady=5)
        
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

    def update_last_status(self, message):
        self.last_status_label.config(text=f"Last file status: {message}")

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
                for attempt in range(self.max_retries):
                    if not self.is_running:
                        break
                    success = self.submit_file(cred, file_path)
                    if success:
                        break
                    else:
                        self.log_output(f"Retrying {os.path.basename(file_path)}, attempt {attempt + 1}")
                        self.update_last_status(f"Retrying {os.path.basename(file_path)}, attempt {attempt + 1}")
                        time.sleep(self.delay_seconds)
                completed += 1
                progress = (completed / total) * 100
                self.progress_bar['value'] = progress
                self.status_label.config(text=f"Progress: {completed}/{total} submissions completed")
                self.root.update_idletasks()
                time.sleep(self.delay_seconds)
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
                result = f"✓ Success: {os.path.basename(file_path)}"
                self.log_output(result)
                self.update_last_status(result)
                return True
            else:
                result = f"✗ Failed: {os.path.basename(file_path)} - Status {response.status_code}"
                self.log_output(result)
                self.update_last_status(result)
                return False
        except Exception as e:
            result = f"✗ Error: {os.path.basename(file_path)} - {str(e)}"
            self.log_output(result)
            self.update_last_status(result)
            return False

    def save_credentials(self):
        key_file = Path("key.key")
        cred_file = Path("credentials.dat")
        key = None
        if key_file.exists():
            key = key_file.read_bytes()
        else:
            key = Fernet.generate_key()
            key_file.write_bytes(key)
        f = Fernet(key)
        encrypted_data = f.encrypt(json.dumps(self.credentials).encode())
        cred_file.write_bytes(encrypted_data)
        messagebox.showinfo('Credentials', 'Credentials saved securely.')

    def load_credentials(self):
        try:
            key_file = Path("key.key")
            cred_file = Path("credentials.dat")
            if not key_file.exists() or not cred_file.exists():
                raise Exception("Saved credentials file not found.")
            key = key_file.read_bytes()
            f = Fernet(key)
            encrypted_data = cred_file.read_bytes()
            decrypted_data = f.decrypt(encrypted_data)
            self.credentials = json.loads(decrypted_data.decode())
            self.update_cred_list()
            messagebox.showinfo('Credentials', 'Credentials loaded successfully.')
        except Exception as e:
            messagebox.showerror('Error', f'Failed to load credentials: {str(e)}')

    def clear_files(self):
        self.files_to_submit.clear()
        self.update_file_list()
        self.update_last_status("File list cleared.")

    def clear_credentials(self):
        self.credentials.clear()
        self.update_cred_list()
        self.update_last_status("Credential list cleared.")

if __name__ == "__main__":
    root = tk.Tk()
    app = MassFileSubmitter(root)
    root.mainloop()
