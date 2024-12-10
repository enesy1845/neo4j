# encryption.py

"""
Modules used for encryption and decryption processes.

Modules:
    - Crypto.Cipher (AES): Used to encrypt and decrypt data using the AES (Advanced Encryption Standard) algorithm.
      AES provides secure data encryption with keys of 16, 24, or 32 bytes in length.

    - base64: Used to convert encrypted binary data to ASCII format and back.
      This ensures that the encrypted data can be safely transported in text-based formats.

    - os: Used to access environment variables for encryption key and IV.

    - dotenv: Used to load environment variables from a .env file.

    - Crypto.Util.Padding: Used for standardized padding and unpadding of data.
"""

import os
from Crypto.Cipher import AES
import base64
from dotenv import load_dotenv,find_dotenv
from Crypto.Util.Padding import pad, unpad  # Import standardized padding functions

# Load environment variables from .env file
try:
    dotenv_path = find_dotenv()
    if dotenv_path:
        load_dotenv(dotenv_path)
    else:
        print("`.env` dosyası bulunamadı.")
except Exception as e:
    print(f"Hata: {e}")

# Fetch key and IV from environment variables
key_b64 = os.getenv('AES_KEY')
iv_b64 = os.getenv('AES_IV')

if not key_b64 or not iv_b64:
    raise ValueError("AES_KEY and AES_IV must be set as environment variables.")

try:
    # Decode the Base64-encoded key and IV
    key = base64.b64decode(key_b64)
    iv = base64.b64decode(iv_b64)
except base64.binascii.Error as e:
    raise ValueError("AES_KEY and AES_IV must be valid Base64-encoded strings.") from e

# Validate key and IV lengths
if len(key) not in (16, 24, 32):
    raise ValueError("AES_KEY must be either 16, 24, or 32 bytes long after decoding.")
if len(iv) != 16:
    raise ValueError("AES_IV must be 16 bytes long after decoding.")

def encrypt(data):
    """Encrypts data using AES."""
    data_bytes = data.encode('utf-8')  # Convert string to bytes
    padded_data = pad(data_bytes, AES.block_size)  # Apply PKCS7 padding
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted_bytes = cipher.encrypt(padded_data)
    return base64.b64encode(encrypted_bytes).decode('utf-8')  # Return Base64-encoded string

def decrypt(data):
    """Decrypts encrypted data using AES."""
    try:
        encrypted_bytes = base64.b64decode(data)
    except base64.binascii.Error as e:
        raise ValueError("Invalid Base64-encoded data.") from e

    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_padded = cipher.decrypt(encrypted_bytes)
    try:
        decrypted_bytes = unpad(decrypted_padded, AES.block_size)  # Remove PKCS7 padding
    except ValueError as e:
        raise ValueError("Incorrect padding. Possibly wrong AES_KEY or AES_IV.") from e

    try:
        return decrypted_bytes.decode('utf-8')  # Convert bytes back to string
    except UnicodeDecodeError as e:
        raise ValueError("Decrypted data is not valid UTF-8.") from e
