# utils.py

import json
import os
import random
import platform
from encryption import encrypt, decrypt

def read_json(file_path):
    """
    Belirtilen JSON dosyasını okur, şifreliyse çözer ve veriyi döndürür.

    Verilen dosya yolundaki JSON verisini okur. Eğer veri şifrelenmişse, şifre
    çözme işlemi uygulanır ve JSON formatında bir Python veri yapısına dönüştürülür.
    Dosya şifrelenmemişse doğrudan JSON olarak okunur. Dosya yoksa veya boşsa
    boş bir liste döndürür.

    Args:
        file_path (str): Okunacak JSON dosyasının dosya yolu.

    Returns:
        dict or list: JSON dosyasından okunan Python veri yapısı.
    """
    if not os.path.exists(file_path):
        return []
    with open(file_path, 'r', encoding='utf-8') as f:
        encrypted_data = f.read()
        if encrypted_data:
            try:
                data_str = decrypt(encrypted_data)
                return json.loads(data_str)
            except Exception:
                # Eğer şifre çözme başarısız olursa, dosya şifrelenmemiş olabilir
                f.seek(0)# dosya başına dönmek için
                data_str = f.read()
                return json.loads(data_str)
        else:
            return []

def write_json(data, file_path):
    """
    Veriyi belirtilen JSON dosyasına şifrelenmiş olarak yazar.

    Verilen Python veri yapısını (sözlük veya liste), JSON formatına dönüştürerek
    belirtilen dosya yoluna şifrelenmiş biçimde kaydeder. Veriyi JSON formatında
    stringe dönüştürür ve şifreleyerek güvenli bir şekilde dosyaya yazar.

    Args:
        data (dict or list): JSON formatında kaydedilecek Python veri yapısı.
        file_path (str): JSON verisinin kaydedileceği dosya yolu.
    """
    data_str = json.dumps(data, ensure_ascii=False, indent=4)#.dumps-> stringe dönüştürür,indent boşluk koyar(rahat okunması için)
    encrypted_data = encrypt(data_str)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(encrypted_data)

def get_next_user_id():
    """
    Yeni kullanıcılar için benzersiz bir ID üretir.

    Kullanıcıların saklandığı JSON dosyasındaki mevcut ID'leri kontrol eder
    ve en yüksek ID'nin bir fazlasını döndürerek yeni bir kullanıcı için
    benzersiz bir ID atar. Dosya yoksa veya boşsa ID'yi 1 olarak başlatır.

    Returns:
        int: Yeni kullanıcı için benzersiz ID.
    """
    USERS_FILE = 'data/users/users.json'
    if not os.path.exists(USERS_FILE):
        return 1
    users = read_json(USERS_FILE)
    if not users:
        return 1
    max_id = max(user['user_id'] for user in users)
    return max_id + 1

"""
UUID Yaklaşımı: Tamamen benzersiz bir kimlik için ideal, ancak çok uzun ID'ler üretir.
Prefiks ile Birleşik Kimlik: Okunabilir ve her soru türü için ID’yi düzenli hale getirir.
bir zamandan sonra id'lerin karışmasına karşılık,get_next_question_id bu fonksiyon için yukarıdaki metotlardan birisi uygulanabilir.
"""
def get_next_question_id(question_type):
    """Sorular için otomatik ID üretir."""
    QUESTIONS_FOLDER = 'data/questions/'
    files = {
        'true_false': 'true_false_questions.json',
        'single_choice': 'single_choice_questions.json',
        'multiple_choice': 'multiple_choice_questions.json'
    }
    file_path = os.path.join(QUESTIONS_FOLDER, files[question_type])
    if not os.path.exists(file_path):
        starting_ids = {
            'true_false': 1,
            'single_choice': 1000,
            'multiple_choice': 2000
        }
        return starting_ids[question_type]
    questions = read_json(file_path)
    if not questions:
        starting_ids = {
            'true_false': 1,
            'single_choice': 1000,
            'multiple_choice': 2000
        }
        return starting_ids[question_type]
    max_id = max(question['id'] for question in questions)
    return max_id + 1

def clear_screen():
    """
    Konsolu temizler.

    İşletim sistemine bağlı olarak konsolu temizlemek için uygun komutu çalıştırır.
    Windows işletim sisteminde `cls` komutu, diğer işletim sistemlerinde (Linux, macOS)
    `clear` komutu kullanılır.

    Yöntem:
        - Windows: `os.system('cls')`
        - Diğerleri: `os.system('clear')`
    """
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')


def validate_input(prompt, valid_options):
    """
    Kullanıcıdan geçerli bir giriş alır.

    Kullanıcıdan belirli seçenekler arasından geçerli bir giriş almasını sağlar.
    Kullanıcının geçerli olmayan bir giriş yapması durumunda tekrar giriş yapması istenir.

    Args:
        prompt (str): Kullanıcıya gösterilecek giriş istemi.
        valid_options (list or set): Kullanıcının girebileceği geçerli seçeneklerin listesi veya kümesi.

    Returns:
        str: Geçerli bir giriş yapıldığında, kullanıcının girdiği seçenek döndürülür.
    """
    while True:
        user_input = input(prompt).strip()
        if user_input in valid_options:
            return user_input
        else:
            print("Geçersiz giriş. Lütfen tekrar deneyin.")

def format_time(seconds):
    """
    Saniye cinsinden verilen süreyi "dakika ve saniye" formatında metin olarak döndürür.

    Belirtilen saniye değerini dakikaya çevirir ve kalan saniyeleri hesaplar.
    Bu süreyi "X dakika Y saniye" formatında bir metin olarak döndürür.

    Args:
        seconds (int): Saniye cinsinden toplam süre.

    Returns:
        str: Dakika ve saniye olarak formatlanmış süre metni.
    """
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes} dakika {seconds} saniye"

def generate_random_number(start, end):
    """Belirtilen aralıkta rastgele bir sayı üretir."""
    return random.randint(start, end)
