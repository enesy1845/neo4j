# tools/user.py

import uuid
from tools.utils import load_json, save_json, hash_password, check_password, DEFAULT_SCHOOL_NAME

USERS_FILE = 'users/users.json'
STATISTICS_FILE = 'users/statistics.json'

def register_user(username, password, name, surname, class_name, role, registered_section=None):
    users_data = load_json(USERS_FILE)
    for user in users_data.get('users', []):
        if user['username'] == username:
            print("Username already exists.")
            return False
    hashed_pw = hash_password(password)
    user_id = str(uuid.uuid4())
    user = {
        "user_id": user_id,
        "username": username,
        "password": hashed_pw,
        "name": name,
        "surname": surname,
        "phone_number": "",
        "role": role.lower(),
        "attempts": 0,
        "last_attempt_date": "",
        "score1": 0,
        "score2": 0,
        "score_avg": 0,
        "class_name": class_name,
        "school_name": DEFAULT_SCHOOL_NAME,
        "registered_section": registered_section or ""
    }
    users_data['users'].append(user)
    save_json(USERS_FILE, users_data)

    # Initialize statistics if admin
    if role.lower() == 'admin':
        statistics = load_json(STATISTICS_FILE)
        # Varsayılan okul zaten load_json tarafından oluşturulmuş
        pass

    print("Registration successful.")
    return True

def login_user(username, password):
    users_data = load_json(USERS_FILE)
    for user in users_data.get('users', []):
        if user['username'] == username:
            if check_password(password, user['password']):
                print(f"Welcome, {user['name']} {user['surname']}!")
                return user
            else:
                print("Incorrect password.")
                return None
    print("User not found.")
    return None

def list_users():
    users_data = load_json(USERS_FILE)
    print("\n=== User List ===")
    for user in users_data.get('users', []):
        print(f"Username: {user['username']} | Role: {user['role']} | Class: {user['class_name']}")

def add_user(admin_user, **kwargs):
    # Sadece admin ekleyebilir
    if admin_user['role'].lower() != 'admin':
        print("Only admins can add users.")
        return False
    role = kwargs.get('role', '').lower()
    if role not in ['teacher', 'student']:
        print("Role must be either 'teacher' or 'student'.")
        return False
    return register_user(**kwargs)

def delete_user(admin_user, username):
    if admin_user['role'].lower() != 'admin':
        print("Only admins can delete users.")
        return False
    users_data = load_json(USERS_FILE)
    users = users_data.get('users', [])
    users = [user for user in users if user['username'] != username]
    users_data['users'] = users
    save_json(USERS_FILE, users_data)
    print("User deleted.")
    return True

def update_user(admin_user, username, **kwargs):
    if admin_user['role'].lower() != 'admin':
        print("Only admins can update users.")
        return False
    users_data = load_json(USERS_FILE)
    for user in users_data.get('users', []):
        if user['username'] == username:
            for key, value in kwargs.items():
                if key in user and value:
                    user[key] = value
            save_json(USERS_FILE, users_data)
            print("User updated.")
            return True
    print("User not found.")
    return False
