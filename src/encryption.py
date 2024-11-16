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

"""
AES şifreleme işlemi için anahtar (key) ve IV (Initialization Vector) gereklidir.

Args:
    key (bytes): AES algoritmasında kullanılan şifreleme anahtarı. AES, 16 byte (128 bit),
        24 byte (192 bit) veya 32 byte (256 bit) uzunluğunda anahtarlarla çalışabilir.
        Güvenlik için anahtarın rastgele ve güçlü bir şekilde oluşturulmuş olması önemlidir.

    iv (bytes): Initialization Vector (IV), şifreleme algoritmasının CBC gibi modlarında
        her şifreleme işlemi için farklı bir başlangıç değeri sağlar. Bu, aynı anahtar
        kullanılsa bile her şifrelemenin farklı sonuç üretmesini garanti eder. IV'nin de
        16 byte uzunluğunda olması gerekir ve güvenli bir rastgelelik sağlanmalıdır.

Not:
    AES şifrelemesinde hem `key` hem de `iv` güvenliğin temel unsurlarıdır. Anahtar,
    veriyi şifreleyen temel bileşen olup veri güvenliğini sağlar. IV ise, aynı anahtarla
    yapılan tekrar şifrelemelerde bile benzersiz şifreli metin üretir.
"""
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
    padding = chr(padding_length) * padding_length
    return s + padding

def unpad(s):
    """
    Doldurulmuş veriyi orijinal haline getirir.

    AES şifrelemesi için veriye eklenen dolgu karakterlerini kaldırır ve orijinal metni
    elde eder. Doldurma sırasında kullanılan karakterler, dolgu miktarını belirttiği 
    için, bu karakterler kaldırılarak veri orijinal haliyle döndürülür.

    Args:
        s (str): Dolgu karakterleri eklenmiş metin.

    Returns:
        str: Orijinal metin (dolgu karakterleri olmadan).

    Örnek:
        `"hello\x03\x03\x03"` şeklinde dolgu yapılmış bir metin verildiğinde, bu işlev 
        dolgu karakterlerini kaldırarak `"hello"` olarak döndürür.
    """
    padding_length = ord(s[-1])
    return s[:-padding_length]

def encrypt(data):
    """
    Veriyi AES algoritmasıyla şifreler ve Base64 formatında döndürür.

    Veriyi AES algoritması ile şifreleyerek güvenli hale getirir. Şifreleme işlemi
    sırasında verinin uzunluğu 16 baytın katı olacak şekilde doldurulur ve AES
    şifreleme CBC modunda yapılır. Şifrelenmiş veriyi Base64 ile kodlayarak döndürür.

    Args:
        data (str): Şifrelenmesi gereken düz metin.

    Returns:
        str: Base64 formatında şifrelenmiş metin.

    Not:
        Şifreleme için AES 128-bit (16 bayt) CBC modu kullanılır. Bu işlev, veriyi
        güvenli bir şekilde saklamak veya iletmek için Base64 formatında ASCII kodlanmış
        şifreli metin olarak döndürür.

    Örnek:
        `"Gizli Mesaj"` gibi bir düz metin girildiğinde, Base64 ile kodlanmış
        şifreli metin olarak döner, örneğin `"w34v...=="`.
    """
    data = pad(data)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted_bytes = cipher.encrypt(data.encode('utf-8'))
    return base64.b64encode(encrypted_bytes).decode('utf-8')

def decrypt(data):
    """
    AES ile şifrelenmiş veriyi çözerek orijinal metne döndürür.

    Şifrelenmiş veriyi Base64 formatında alır, AES algoritmasını kullanarak çözer ve
    orijinal düz metne dönüştürür. Şifre çözme işlemi, şifreleme sırasında kullanılan 
    aynı anahtar ve IV değerleri ile yapılmalıdır. Şifre çözme sonrası veriyi 
    orijinal haliyle döndürmek için dolgu karakterleri kaldırılır.

    Args:
        data (str): Base64 formatında şifrelenmiş metin.

    Returns:
        str: Orijinal düz metin.

    Not:
        AES CBC modunda şifre çözme işlemi yapılır. Bu nedenle, veriyi çözmek için
        aynı anahtar ve IV kullanılmalıdır. Şifre çözme işlemi tamamlandıktan sonra,
        metin dolgu karakterlerinden arındırılarak döndürülür.

    Örnek:
        `"w34v...=="` gibi Base64 kodlu şifreli bir metin girildiğinde, bu işlev 
        `"Gizli Mesaj"` gibi orijinal metni döndürür.
    """
    encrypted_bytes = base64.b64decode(data)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_bytes = cipher.decrypt(encrypted_bytes)
    return unpad(decrypted_bytes.decode('utf-8'))
