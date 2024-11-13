# utils.py

import json
import os
import random
import platform
from encryption import encrypt, decrypt

def read_json(file_path):
    """Belirtilen JSON dosyasını okur ve veriyi döndürür."""
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
                f.seek(0)
                data_str = f.read()
                return json.loads(data_str)
        else:
            return []

def write_json(data, file_path):
    """Veriyi belirtilen JSON dosyasına yazar."""
    data_str = json.dumps(data, ensure_ascii=False, indent=4)
    encrypted_data = encrypt(data_str)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(encrypted_data)

def get_next_user_id():
    """Kullanıcılar için otomatik ID üretir."""
    USERS_FILE = 'data/users/users.json'
    if not os.path.exists(USERS_FILE):
        return 1
    users = read_json(USERS_FILE)
    if not users:
        return 1
    max_id = max(user['user_id'] for user in users)
    return max_id + 1

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
    """Konsolu temizler."""
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')

def validate_input(prompt, valid_options):
    """Kullanıcıdan geçerli bir giriş alır."""
    while True:
        user_input = input(prompt).strip()
        if user_input in valid_options:
            return user_input
        else:
            print("Geçersiz giriş. Lütfen tekrar deneyin.")

def format_time(seconds):
    """Saniye cinsinden verilen süreyi dakika ve saniye olarak formatlar."""
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes} dakika {seconds} saniye"

def generate_random_number(start, end):
    """Belirtilen aralıkta rastgele bir sayı üretir."""
    return random.randint(start, end)
