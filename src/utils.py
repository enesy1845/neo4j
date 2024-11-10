# utils.py

import json
import os
import random
import platform
from encryption import encrypt, decrypt

def read_json(file_path):
    """Belirtilen JSON dosyasını okur ve veriyi döndürür."""
    pass

def write_json(data, file_path):
    """Veriyi belirtilen JSON dosyasına yazar."""
    pass

def get_next_user_id():
    """Kullanıcılar için otomatik ID üretir."""
    pass

def get_next_question_id(question_type):
    """Sorular için otomatik ID üretir."""
    pass

def clear_screen():
    """Konsolu temizler."""
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')

def validate_input(prompt, valid_options):
    """Kullanıcıdan geçerli bir giriş alır."""
    pass

def format_time(seconds):
    """Saniye cinsinden verilen süreyi dakika ve saniye olarak formatlar."""
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes} dakika {seconds} saniye"

def generate_random_number(start, end):
    """Belirtilen aralıkta rastgele bir sayı üretir."""
    pass
