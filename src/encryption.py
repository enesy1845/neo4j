# encryption.py

from Crypto.Cipher import AES
import base64
import os
import json
#Bu sadece bir örnek. Buraya güçlü bir şifre eklememiz gerekiyor.
key = b'16_byte_key_here'  # 16 bayt uzunluğunda bir anahtar  
iv = b'16_byte_iv_here '   # 16 bayt uzunluğunda bir IV

def pad(s):
    """Veriyi 16'nın katları olacak şekilde doldurur."""
    padding_length = 16 - (len(s.encode('utf-8')) % 16)
    padding = chr(padding_length) * padding_length # eksik kalan sayının ASCII degerini alır ve verinin sonuna ascii değeri kadar ekler
    return s + padding

def unpad(s):
    """Doldurulmuş veriyi PKCS#7 standardına göre orijinal haline getirir."""
    padding_length = ord(s[-1])  # Dolgu karakterinin sayısal değerini al
    if s[-padding_length:] == chr(padding_length) * padding_length:
        return s[:-padding_length]  # Dolguyu kaldırarak veriyi döndür
    else:
        return s  # Dolgu yoksa veriyi olduğu gibi döndür

def encrypt(data):
    """Veriyi AES ile şifreler."""
    data = pad(data) # veriyi 16 bayt uzunluğunda doldurur
    cipher = AES.new(key, AES.MODE_CBC, iv)
    
    #Bu kısımda, encrypted_bytes doğrudan döndürülmüyor çünkü 
    #şifrelenmiş veriyi base64 formatına çevirip bir metin olarak 
    # döndürmek istiyoruz. encrypted_bytes ikili (binary) bir veri 
    # formatında olduğu için, bu veriyi metin formatına çevirmeden 
    # doğrudan döndürmek kullanım açısından zor olabilir.
    encrypted_bytes = cipher.encrypt(data.encode('utf-8')) #binary veri
    return base64.b64encode(encrypted_bytes).decode('utf-8') #base64 veri	

def decrypt(data):
    """Şifrelenmiş veriyi AES ile çözer."""
    encrypted_bytes = base64.b64decode(data)#binary veriye çevirir
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_bytes = cipher.decrypt(encrypted_bytes)
    return unpad(decrypted_bytes.decode('utf-8'))
