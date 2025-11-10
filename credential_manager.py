# Credential storage for Mass File Submission Tool
# Stores API keys and login info securely using Fernet symmetric encryption.

import os
from cryptography.fernet import Fernet
import json

CREDENTIAL_FILE = "credentials.enc"
KEY_FILE = "credkey.key"

class CredentialManager:
    def __init__(self):
        self.key = None
        self.load_key()
        self.fernet = Fernet(self.key)

    def load_key(self):
        if not os.path.exists(KEY_FILE):
            self.key = Fernet.generate_key()
            with open(KEY_FILE, 'wb') as kf:
                kf.write(self.key)
        else:
            with open(KEY_FILE, 'rb') as kf:
                self.key = kf.read()

    def save_credentials(self, cred_dict):
        data = json.dumps(cred_dict).encode()
        encrypted = self.fernet.encrypt(data)
        with open(CREDENTIAL_FILE, 'wb') as cf:
            cf.write(encrypted)

    def load_credentials(self):
        if not os.path.exists(CREDENTIAL_FILE):
            return None
        with open(CREDENTIAL_FILE, 'rb') as cf:
            enc_data = cf.read()
        try:
            dec_data = self.fernet.decrypt(enc_data)
            return json.loads(dec_data.decode())
        except Exception:
            return None

# Usage example (to integrate in main.py submission logic):
# creds = CredentialManager()
# creds.save_credentials({'api_key':'123', 'platform':'Example'})
# loaded = creds.load_credentials()