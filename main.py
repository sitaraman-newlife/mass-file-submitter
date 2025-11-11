import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time
from pathlib import Path
import csv
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import random
import json
import base64
from cryptography.fernet import Fernet

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.242 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15",
    # Add more user agents if needed!
]

CRED_FILE = "site_creds.enc"
KEY_FILE = "key.key"

def generate_key():
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(key)
    return key

def load_key():
    if not Path(KEY_FILE).exists():
        return generate_key()
    with open(KEY_FILE, "rb") as f:
        return f.read()

def encrypt_data(data, key):
    f = Fernet(key)
    enc = f.encrypt(data.encode())
    return enc

def decrypt_data(data, key):
    f = Fernet(key)
    dec = f.decrypt(data)
    return dec.decode()

def save_creds(creds):
    key = load_key()
    data = json.dumps(creds)
    enc_data = encrypt_data(data, key)
    with open(CRED_FILE, "wb") as f:
        f.write(enc_data)

def load_creds():
    if not Path(CRED_FILE).exists():
        return {}
    key = load_key()
    with open(CRED_FILE, "rb") as f:
        enc_data = f.read()
    try:
        dec_data = decrypt_data(enc_data, key)
        return json.loads(dec_data)
    except Exception:
        return {}

class MassFileSubmitter:
    def __init__(self, root):
        self.root = root
        self.root.title("Mass File Submission Tool v1.0")
        self.root.geometry("900x700")

        self.files_to_submit = []
        self.destination_urls = []
        self.is_running = False

        # Map: url -> (user, pass, headers, api_key)
        self.site_creds = load_creds()

        self.setup_ui()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        title = ttk.Label(main_frame, text="Mass File Submission Tool",
                         font=('Arial', 16, 'bold'))
        title.grid(row=0, column=0, columnspan=4, pady=10)

        files_label = ttk.Label(main_frame, text="Files to Submit:",
                               font=('Arial', 12, 'bold'))
        files_label.grid(row=1, column=0, sticky=tk.W, pady=5)

        self.file_listbox = tk.Listbox(main_frame, height=8, width=80)
        self.file_listbox.grid(row=2, column=0, columnspan=4, pady=5, padx=5)

        btn_frame1 = ttk.Frame(main_frame)
        btn_frame1.grid(row=3, column=0, columnspan=4, pady=5)
        ttk.Button(btn_frame1, text="Add Files",
                  command=self.add_files).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame1, text="Clear Files",
                  command=self.clear_files).pack(side=tk.LEFT, padx=5)

        urls_label = ttk.Label(main_frame, text="Destination URLs:",
                              font=('Arial', 12, 'bold'))
        urls_label.grid(row=4, column=0, sticky=tk.W, pady=5)

        self.url_listbox = tk.Listbox(main_frame, height=8, width=80)
        self.url_listbox.grid(row=5, column=0, columnspan=4, pady=5, padx=5)

        btn_frame2 = ttk.Frame(main_frame)
        btn_frame2.grid(row=6, column=0, columnspan=4, pady=5)
        ttk.Button(btn_frame2, text="Load URLs from CSV",
                  command=self.load_csv).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame2, text="Clear URLs",
                  command=self.clear_urls).pack(side=tk.LEFT, padx=5)

        # Credential Button
        ttk.Button(main_frame, text="Manage Credentials", command=self.open_cred_manager).grid(row=7, column=0, columnspan=2, pady=5)

        progress_label = ttk.Label(main_frame, text="Progress:",
                                  font=('Arial', 12, 'bold'))
        progress_label.grid(row=8, column=0, sticky=tk.W, pady=5)

        self.progress_bar = ttk.Progressbar(main_frame, length=700,
                                           mode='determinate')
        self.progress_bar.grid(row=9, column=0, columnspan=4, pady=5)

        self.status_label = ttk.Label(main_frame, text="Ready",
                                     foreground="green")
        self.status_label.grid(row=10, column=0, columnspan=4)

        self.output_text = tk.Text(main_frame, height=12, width=80, state="disabled")
        self.output_text.grid(row=11, column=0, columnspan=4, pady=5)

        self.submit_btn = ttk.Button(main_frame, text="SUBMIT ALL FILES",
                                    command=self.submit_files)
        self.submit_btn.grid(row=12, column=0, columnspan=4, pady=20)

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)

    def log_output(self, msg):
        self.output_text.config(state="normal")
        self.output_text.insert(tk.END, msg + "\n")
        self.output_text.config(state="disabled")
        self.output_text.see(tk.END)

    def add_files(self):
        files = filedialog.askopenfilenames(
            title="Select files",
            filetypes=[("Text and PDF", "*.txt *.pdf"), ("All files", "*.*")]
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

    def open_cred_manager(self):
        cred_win = tk.Toplevel(self.root)
        cred_win.title("Site Credentials")
        cred_win.geometry("600x400")

        url_label = tk.Label(cred_win, text="Destination URL")
        url_label.pack()
        url_entry = tk.Entry(cred_win, width=80)
        url_entry.pack()

        user_label = tk.Label(cred_win, text="Username (optional):")
        user_label.pack()
        user_entry = tk.Entry(cred_win, width=40)
        user_entry.pack()

        pass_label = tk.Label(cred_win, text="Password (optional):")
        pass_label.pack()
        pass_entry = tk.Entry(cred_win, show="*", width=40)
        pass_entry.pack()

        api_label = tk.Label(cred_win, text="API Key/Token (optional):")
        api_label.pack()
        api_entry = tk.Entry(cred_win, width=40)
        api_entry.pack()

        head_label = tk.Label(cred_win, text="Custom Headers (as JSON):")
        head_label.pack()
        head_entry = tk.Entry(cred_win, width=80)
        head_entry.pack()

        def save_this_cred():
            url = url_entry.get().strip()
            if not url:
                messagebox.showerror("Error", "URL is required")
                return
            cred = {
                "user": user_entry.get().strip(),
                "pass": pass_entry.get().strip(),
                "api_key": api_entry.get().strip(),
                "headers": {},
            }
            try:
                cred["headers"] = json.loads(head_entry.get().strip() or "{}").
            except Exception as e:
                messagebox.showerror("Error", f"Header JSON invalid: {e}")
                return
            self.site_creds[url] = cred
            save_creds(self.site_creds)
            messagebox.showinfo("Saved", f"Credentials saved for {url}")
            cred_win.destroy()

        save_button = tk.Button(cred_win, text="Save", command=save_this_cred)
        save_button.pack(pady=16)

        tk.Label(cred_win, text="--- Existing URLs ---").pack(pady=4)
        for u in self.site_creds:
            tk.Label(cred_win, text=u).pack()

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
            threading.Thread(target=self.run_submission, daemon=True).start()

    def run_submission(self):
        total = len(self.files_to_submit) * len(self.destination_urls)
        max_workers = min(20, len(self.destination_urls))  # Adjustable parallelism
        completed = 0
        results = []
        self.update_status("Submitting...", "orange")
        self.progress_bar['value'] = 0
        self.log_output("---- Batch submission started ----")
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_map = {}
            for file_path in self.files_to_submit:
                for url in self.destination_urls:
                    future = executor.submit(self.submit_file_to_url, file_path, url)
                    future_map[future] = (file_path, url)
            for future in as_completed(future_map):
                file_path, url = future_map[future]
                success, code, msg = future.result()
                completed += 1
                self.progress_bar['value'] = (completed / total) * 100
                status_str = f"[{'SUCCESS' if success else 'FAIL'}] {Path(file_path).name} → {url} ({code}): {msg}"
                self.log_output(status_str)
                self.root.update_idletasks()
                results.append((file_path, url, success, code, msg))
        summary = f"Completed! {completed} submissions."
        self.update_status(summary, "green")
        self.log_output("---- Batch finished ----")
        self.submit_btn.config(state='normal')
        messagebox.showinfo("Success", summary)

    def submit_file_to_url(self, file_path, url):
        cred = self.site_creds.get(url, {})
        user_agent = random.choice(USER_AGENTS)
        headers = cred.get("headers", {}).copy() if cred else {}
        headers["User-Agent"] = user_agent
        if cred.get("api_key"):
            headers["Authorization"] = f"Bearer {cred['api_key']}"
        try_count = 0
        max_retry = 4
        while try_count < max_retry:
            try:
                with open(file_path, "rb") as f:
                    files = {'file': (Path(file_path).name, f)}
                    auth = None
                    if cred.get("user") and cred.get("pass"):
                        auth = (cred["user"], cred["pass"])
                    resp = requests.post(url, files=files, headers=headers, auth=auth, timeout=10)
                if 200 <= resp.status_code < 300:
                    return True, resp.status_code, "OK"
                else:
                    time.sleep(2 ** try_count)  # exponential backoff
            except Exception as e:
                time.sleep(2 ** try_count)
            try_count += 1
        # Get last error code if possible
        code = resp.status_code if "resp" in locals() else "?"
        return False, code, "Failed after retries"

if __name__ == "__main__":
    root = tk.Tk()
    app = MassFileSubmitter(root)
    root.mainloop()