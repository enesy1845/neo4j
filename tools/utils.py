# tools/utils.py

import json
import bcrypt
from pathlib import Path

DEFAULT_SCHOOL_NAME = "DefaultSchool"

def load_json(filepath):
    path = Path(filepath)
    if not path.exists():
        # Dosya yoksa, varsayılan veriyi oluştur
        default_data = get_default_data(filepath)
        save_json(filepath, default_data)
        return default_data
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if data is None:
                raise ValueError("JSON içeriği boş.")
            return data
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Error loading {filepath}: {e}")
        # Hatalı veya boşsa, varsayılan veriyi oluştur
        default_data = get_default_data(filepath)
        save_json(filepath, default_data)
        return default_data

def get_default_data(filepath):
    if filepath == 'users/statistics.json':
        return {
            "schools": [
                {
                    "school_name": DEFAULT_SCHOOL_NAME,
                    "classes": {
                        "7-a": {
                            "sections": {
                                "1": {"correct_questions": 0, "wrong_questions": 0, "average_score": 0, "section_percentage": 0},
                                "2": {"correct_questions": 0, "wrong_questions": 0, "average_score": 0, "section_percentage": 0},
                                "3": {"correct_questions": 0, "wrong_questions": 0, "average_score": 0, "section_percentage": 0},
                                "4": {"correct_questions": 0, "wrong_questions": 0, "average_score": 0, "section_percentage": 0}
                            },
                            "average_score": 0.0
                        },
                        "7-b": {
                            "sections": {
                                "1": {"correct_questions": 0, "wrong_questions": 0, "average_score": 0, "section_percentage": 0},
                                "2": {"correct_questions": 0, "wrong_questions": 0, "average_score": 0, "section_percentage": 0},
                                "3": {"correct_questions": 0, "wrong_questions": 0, "average_score": 0, "section_percentage": 0},
                                "4": {"correct_questions": 0, "wrong_questions": 0, "average_score": 0, "section_percentage": 0}
                            },
                            "average_score": 0.0
                        },
                        "7-c": {
                            "sections": {
                                "1": {"correct_questions": 0, "wrong_questions": 0, "average_score": 0, "section_percentage": 0},
                                "2": {"correct_questions": 0, "wrong_questions": 0, "average_score": 0, "section_percentage": 0},
                                "3": {"correct_questions": 0, "wrong_questions": 0, "average_score": 0, "section_percentage": 0},
                                "4": {"correct_questions": 0, "wrong_questions": 0, "average_score": 0, "section_percentage": 0}
                            },
                            "average_score": 0.0
                        },
                        "7-d": {
                            "sections": {
                                "1": {"correct_questions": 0, "wrong_questions": 0, "average_score": 0, "section_percentage": 0},
                                "2": {"correct_questions": 0, "wrong_questions": 0, "average_score": 0, "section_percentage": 0},
                                "3": {"correct_questions": 0, "wrong_questions": 0, "average_score": 0, "section_percentage": 0},
                                "4": {"correct_questions": 0, "wrong_questions": 0, "average_score": 0, "section_percentage": 0}
                            },
                            "average_score": 0.0
                        }
                    }
                }
            ]
        }
    elif filepath == 'users/users.json':
        return {"users": []}
    elif filepath == 'users/user_answers.json':
        return {"exams": []}
    elif filepath.startswith('questions/questions_section'):
        return {"questions": []}
    elif filepath == 'answers/answers.json':
        return {}
    else:
        return {}

def save_json(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())
