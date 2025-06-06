#encryption of logs using Fernet (AES-based)

from cryptography.fernet import Fernet
import os

KEY_FILE = "secret.key"  #path where encryption key is stored

#generate new encryption key and save it
def generate_key():
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(key)

#only create the key if it doesn't exist
def generate_key_if_missing():
    if not os.path.exists(KEY_FILE):
        generate_key()

#load the saved key from disk
def load_key():
    if not os.path.exists(KEY_FILE):
        raise FileNotFoundError("Key file not found")
    return open(KEY_FILE, "rb").read()

#encrypt a file in place
def encrypt_file(filepath):
    try:
        key = load_key()
        fernet = Fernet(key)

        #read file contents
        with open(filepath, "rb") as file:
            original = file.read()

        #encrypt and overwrite
        encrypted = fernet.encrypt(original)
        with open(filepath, "wb") as encrypted_file:
            encrypted_file.write(encrypted)

        print(f"[ENCRYPTED] {filepath}")

    except Exception as e:
        print(f"[ERROR] Failed to encrypt {filepath}: {e}")
