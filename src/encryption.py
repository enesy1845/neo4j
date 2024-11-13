# encryption.py

from Crypto.Cipher import AES
import base64

key = b'16_byte_key_here'  # 16 bayt uzunluğunda bir anahtar
iv = b'16_byte_iv_here '   # 16 bayt uzunluğunda bir IV

def pad(s):
    """Veriyi 16'nın katları olacak şekilde doldurur."""
    padding_length = 16 - (len(s.encode('utf-8')) % 16)
    padding = chr(padding_length) * padding_length
    return s + padding

def unpad(s):
    """Doldurulmuş veriyi orijinal haline getirir."""
    padding_length = ord(s[-1])
    return s[:-padding_length]

def encrypt(data):
    """Veriyi AES ile şifreler."""
    data = pad(data)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted_bytes = cipher.encrypt(data.encode('utf-8'))
    return base64.b64encode(encrypted_bytes).decode('utf-8')

def decrypt(data):
    """Şifrelenmiş veriyi AES ile çözer."""
    encrypted_bytes = base64.b64decode(data)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_bytes = cipher.decrypt(encrypted_bytes)
    return unpad(decrypted_bytes.decode('utf-8'))
