# utils.py

import json
import os
import random
import platform
from encryption import encrypt, decrypt
import uuid

USERS_FILE = 'data/users/users.json'

def read_json(file_path):
    """
    Reads the specified JSON file, decrypts it if encrypted, and returns the data.
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
                f.seek(0)
                data_str = f.read()
                return json.loads(data_str)
        else:
            return []

def write_json(data, file_path):
    """
    Writes the data to the specified JSON file in an encrypted format.
    """
    data_str = json.dumps(data, ensure_ascii=False, indent=4)
    encrypted_data = encrypt(data_str)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(encrypted_data)

def get_next_user_id():
    """
    Generates a unique ID for new users.
    """
    
    if not os.path.exists(USERS_FILE):
        return 1
    users = read_json(USERS_FILE)
    if not users:
        return 1
    max_id = max(user['user_id'] for user in users)
    return max_id + 1

def clear_screen():
    """
    Clears the console screen.
    """
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')

def validate_input(prompt, valid_options):
    """
    Prompts the user for input and ensures it is one of the valid options.
    """
    while True:
        user_input = input(prompt).strip()
        if user_input in valid_options:
            return user_input
        else:
            print("Invalid input. Please try again.")

def format_time(seconds):
    """
    Converts the given time in seconds to a "minutes and seconds" formatted string.
    """
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes} minutes {seconds} seconds"

def generate_random_number(start, end):
    """Generates a random number within the specified range."""
    return random.randint(start, end)
