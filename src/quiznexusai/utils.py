# src/utils.py

import json
import os
import random
import platform
from quiznexusai.encryption import encrypt, decrypt
import uuid

USERS_FILE = 'data/users/users.json'
USER_ANSWERS_FILE = 'data/user_answers/user_answers.json'
ANSWERS_FILE = 'data/answers/answers.json'  # **Yeni Ekleme**
QUESTIONS_DIR = 'data/questions/'  # Directory containing question files
SCHOOLS_FILE = 'data/schools/schools.json'
CLASSES_FILE = 'data/classes/classes.json'
STATISTICS_FILE = 'data/statistics/statistics.json'

def read_json(file_path, encrypted=True):
    """
    Reads the specified JSON file, decrypts it if encrypted, and returns the data.

    Args:
        file_path (str): Path to the JSON file.
        encrypted (bool): Indicates whether the file is encrypted.

    Returns:
        The JSON data as a Python object, or an empty list/dict if the file doesn't exist or is empty.
    """
    if not os.path.exists(file_path):
        if 'questions' in file_path or 'users' in file_path or 'user_answers' in file_path:
            return []
        return {}

    with open(file_path, 'r', encoding='utf-8') as f:
        data_content = f.read().strip()

        if data_content:
            if encrypted:
                try:
                    data_str = decrypt(data_content)
                    return json.loads(data_str)
                except ValueError as e:
                    print(f"Decryption failed for {file_path}: {e}")
                    return [] if 'questions' in file_path or 'users' in file_path or 'user_answers' in file_path else {}
                except json.JSONDecodeError as e:
                    print(f"JSON decoding failed for {file_path}: {e}")
                    return [] if 'questions' in file_path or 'users' in file_path or 'user_answers' in file_path else {}
            else:
                try:
                    return json.loads(data_content)
                except json.JSONDecodeError as e:
                    print(f"JSON decoding failed for {file_path}: {e}")
                    return [] if 'questions' in file_path or 'users' in file_path or 'user_answers' in file_path else {}
        else:
            if 'questions' in file_path or 'users' in file_path or 'user_answers' in file_path:
                return []
            return {}

def write_json(data, file_path, encrypted=True):
    """
    Writes the data to the specified JSON file in an encrypted or plain format.

    Args:
        data: The data to write (must be JSON serializable).
        file_path (str): Path to the JSON file.
        encrypted (bool): Indicates whether to encrypt the file content.
    """
    if encrypted:
        data_str = json.dumps(data, ensure_ascii=False, indent=4)
        encrypted_data = encrypt(data_str)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(encrypted_data)
    else:
        data_str = json.dumps(data, ensure_ascii=False, indent=4)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(data_str)

def read_encrypted_json(file_path):
    """Reads an encrypted JSON file."""
    return read_json(file_path, encrypted=True)

def write_encrypted_json(data, file_path):
    """Writes data to an encrypted JSON file."""
    write_json(data, file_path, encrypted=True)

def read_plain_json(file_path):
    """Reads a plain (unencrypted) JSON file."""
    return read_json(file_path, encrypted=False)

def write_plain_json(data, file_path):
    """Writes data to a plain (unencrypted) JSON file."""
    write_json(data, file_path, encrypted=False)

def read_user_answers():
    """
    Reads the user_answers.json file and returns the data.
    Ensures that the "attempts" key exists.
    """
    if not os.path.exists(USER_ANSWERS_FILE):
        return {"attempts": []}

    with open(USER_ANSWERS_FILE, 'r', encoding='utf-8') as f:
        encrypted_data = f.read().strip()

        if encrypted_data:
            try:
                data_str = decrypt(encrypted_data)
                data = json.loads(data_str)
                if "attempts" not in data:
                    data["attempts"] = []
                return data
            except ValueError as e:
                print(f"Decryption failed for {USER_ANSWERS_FILE}: {e}")
                print("Attempting to read the file without decryption.")
                try:
                    # Attempt to read the file as plain JSON
                    f.seek(0)
                    data_str = f.read()
                    data = json.loads(data_str)
                    if "attempts" not in data:
                        data["attempts"] = []
                    return data
                except json.JSONDecodeError as json_e:
                    print(f"Failed to decode JSON from {USER_ANSWERS_FILE}: {json_e}")
                    return {"attempts": []}
        else:
            return {"attempts": []}

def write_user_answers(data):
    """
    Writes data to the user_answers.json file in an encrypted format.
    """
    data_str = json.dumps(data, ensure_ascii=False, indent=4)
    encrypted_data = encrypt(data_str)
    with open(USER_ANSWERS_FILE, 'w', encoding='utf-8') as f:
        f.write(encrypted_data)

def get_next_user_id():
    """
    Generates a unique UUID for new users.
    """
    return str(uuid.uuid4())

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

def read_statistics():
    if not os.path.exists(STATISTICS_FILE):
        # Ensure the directory exists
        os.makedirs(os.path.dirname(STATISTICS_FILE), exist_ok=True)
        # Create the file with default values
        default_stats = {
            "classes": {},
            "schools": {},
            "total_students": 0,
            "total_exams": 0,
            "successful_exams": 0,
            "failed_exams": 0
        }
        write_statistics(default_stats)
        return default_stats
    else:
        data = read_json(STATISTICS_FILE, encrypted=True)
        if not isinstance(data, dict):
            data = {}
        # Ensure keys exist
        data.setdefault('classes', {})
        data.setdefault('schools', {})
        data.setdefault('total_students', 0)
        data.setdefault('total_exams', 0)
        data.setdefault('successful_exams', 0)
        data.setdefault('failed_exams', 0)
        return data

def write_statistics(data):
    # Ensure the directory exists
    os.makedirs(os.path.dirname(STATISTICS_FILE), exist_ok=True)
    write_json(data, STATISTICS_FILE, encrypted=True)

def print_table(headers, rows, title=None):
    """Prints a formatted table."""
    if title:
        print(f"\n=== {title} ===")
    
    # Normalize row lengths to match the headers
    normalized_rows = []
    for row in rows:
        # If row has fewer columns, fill the missing with empty strings
        normalized_row = row + [""] * (len(headers) - len(row))
        # If row has more columns, trim extra columns
        normalized_row = normalized_row[:len(headers)]
        normalized_rows.append(normalized_row)
    
    # Calculate the width of each column
    col_widths = [len(header) for header in headers]
    for row in normalized_rows:
        for idx, item in enumerate(row):
            col_widths[idx] = max(col_widths[idx], len(str(item)))
    
    # Create format string
    row_format = "|".join(["{{:<{}}}".format(width) for width in col_widths])
    separator = "-+-".join(['-' * width for width in col_widths])
    
    # Print headers
    print(row_format.format(*headers))
    print(separator)
    
    # Print rows
    for row in normalized_rows:
        print(row_format.format(*row))

