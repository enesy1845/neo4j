# encryption.py

"""
Şifreleme ve çözme işlemleri için kullanılan modüller.

Modüller:
    - Crypto.Cipher (AES): AES (Advanced Encryption Standard) algoritmasını kullanarak
      veriyi şifrelemek ve çözmek için kullanılır. AES, 16, 24 veya 32 bayt uzunluğunda
      anahtarlarla güvenli veri şifreleme sağlar.

    - base64: Şifrelenmiş ikili veriyi ASCII formatına dönüştürmek ve geri almak için
      kullanılır. Bu sayede şifrelenmiş veri, metin tabanlı formatlarda güvenli bir şekilde
      taşınabilir hale gelir.
"""
from Crypto.Cipher import AES
import base64

key = b'16_byte_key_here'  # 16 bayt uzunluğunda bir anahtar
iv = b'16_byte_iv_here '   # 16 bayt uzunluğunda bir IV

def pad(s):
    """
    Veriyi AES şifreleme için 16 baytlık bloklara tamamlayacak şekilde doldurur.

    AES algoritması, 16 baytlık (128-bit) bloklar halinde veri işlediği için verinin
    uzunluğu 16'nın katı olmalıdır. Bu işlev, girilen veriyi 16'nın katlarına 
    tamamlamak için eksik baytları doldurur. Eklenen her dolgu karakterinin sayısı,
    eklenmesi gereken bayt miktarını temsil eder.

    Args:
        s (str): 16 bayt uzunluğunda olmayan düz metin.

    Returns:
        str: Verinin sonunda dolgu karakterleri ile 16'nın katlarına tamamlanmış hali.

    Örnek:
        "hello" metni 16 baytlık bir bloğu doldurmak için ek karakterlere ihtiyaç
        duyduğunda, bu işlev veriyi `"hello\x03\x03\x03"` olarak döndürür.
        Burada "\x03", 3 baytlık dolgu yapıldığını gösterir.
    """
    padding_length = 16 - (len(s.encode('utf-8')) % 16)
    padding = chr(padding_length) * padding_length # eksik kalan sayının ASCII degerini alır ve verinin sonuna ascii değeri kadar ekler
    return s + padding

def unpad(s):
    """Doldurulmuş veriyi orijinal haline getirir."""
    padding_length = ord(s[-1])
    return s[:-padding_length]

def encrypt(data):
    """Veriyi AES ile şifreler."""
    data = pad(data)
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
    encrypted_bytes = base64.b64decode(data)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_bytes = cipher.decrypt(encrypted_bytes)
    return unpad(decrypted_bytes.decode('utf-8'))
