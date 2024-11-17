# encryption.py

"""
Modules used for encryption and decryption processes.

Modules:
    - Crypto.Cipher (AES): Used to encrypt and decrypt data using the AES (Advanced Encryption Standard) algorithm.
      AES provides secure data encryption with keys of 16, 24, or 32 bytes in length.
    
    - base64: Used to convert encrypted binary data to ASCII format and back.
      This ensures that the encrypted data can be safely transported in text-based formats.
"""
from Crypto.Cipher import AES
import base64

key = b'16_byte_key_here'  # A 16-byte key
iv = b'16_byte_iv_here '   # A 16-byte IV

def pad(s):
    """
    Pads the data to complete 16-byte blocks for AES encryption.

    Since the AES algorithm processes data in 16-byte (128-bit) blocks, the length of the data
    must be a multiple of 16. This function pads the input data with the necessary number of bytes
    to reach the next multiple of 16. Each padding character added represents the number of bytes
    that were added as padding.

    Args:
        s (str): Plain text that is not a multiple of 16 bytes in length.

    Returns:
        str: The input data padded with padding characters at the end to make its length a multiple of 16.

    Example:
        When the text "hello" needs additional characters to fill a 16-byte block, this function
        returns the data as `"hello\x0b\x0b\x0b\x0b\x0b\x0b\x0b\x0b\x0b\x0b\x0b"`.

        Here, "\x0b" indicates that 11 bytes of padding were added.
    """
    padding_length = 16 - (len(s.encode('utf-8')) % 16)
    padding = chr(padding_length) * padding_length  # Takes the ASCII value of the missing number and appends that many to the end of the data
    return s + padding

def unpad(s):
    """Removes padding from the padded data to restore it to its original form."""
    padding_length = ord(s[-1])
    return s[:-padding_length]

def encrypt(data):
    """Encrypts data using AES."""
    data = pad(data)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    
    # In this part, encrypted_bytes are not returned directly because
    # we want to convert the encrypted binary data to base64 format and
    # return it as text. Since encrypted_bytes is in binary format,
    # returning it directly without converting to text format
    # can be difficult to use.
    encrypted_bytes = cipher.encrypt(data.encode('utf-8'))  # binary data
    return base64.b64encode(encrypted_bytes).decode('utf-8')  # base64 data

def decrypt(data):
    """Decrypts encrypted data using AES."""
    encrypted_bytes = base64.b64decode(data)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_bytes = cipher.decrypt(encrypted_bytes)
    return unpad(decrypted_bytes.decode('utf-8'))
