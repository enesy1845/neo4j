# tools/user.py
import os
from uuid import uuid4
from tools.utils import hash_password, check_password


def register_user(session, username, password, name, surname, class_name, role, registered_section=None):
    # Normalize username (trim and lower-case)
    username = username.strip().lower()
    # Check if user already exists
    result = session.run("MATCH (u:User {username: $username}) RETURN u LIMIT 1", {"username": username})
    if result.single():
        print("Username already exists.")
        return False
    # Find DefaultSchool node
    result = session.run("MATCH (s:School {name: 'DefaultSchool'}) RETURN s LIMIT 1")
    record = result.single()
    if not record:
        print("DefaultSchool not found.")
        return False
    school = record["s"]
    user_id = str(uuid4())
    hashed_pw = hash_password(password)
    # Determine school number for student by counting existing students in the school
    if role.lower() == "student":
        result = session.run("MATCH (u:User {school_id: $school_id, role: 'student'}) RETURN count(u) as student_count", {"school_id": school.get("school_id", "default-school")})
        count = result.single()["student_count"]
        okul_no = count + 1
    else:
        okul_no = None
    session.run("""
    CREATE (u:User {
        user_id: $user_id,
        username: $username,
        password: $password,
        name: $name,
        surname: $surname,
        role: $role,
        class_name: $class_name,
        registered_section: $registered_section,
        attempts: 0,
        score_avg: 0,
        okul_no: $okul_no,
        school_id: $school_id
    })
    """, {
        "user_id": user_id,
        "username": username,
        "password": hashed_pw,
        "name": name,
        "surname": surname,
        "role": role.lower(),
        "class_name": class_name,
        "registered_section": registered_section if role.lower() == "teacher" else None,
        "okul_no": okul_no,
        "school_id": school.get("school_id", "default-school")
    })
    print(f"User registered: {username} | Password: {password}")
    return True

def login_user(session, username, password):
    # Normalize username to ensure consistency
    username = username.strip().lower()
    result = session.run("MATCH (u:User {username: $username}) RETURN u LIMIT 1", {"username": username})
    record = result.single()
    if not record:
        print("User not found.")
        return None
    user = record["u"]
    if check_password(password, user["password"]):
        print(f"Welcome, {user['name']} {user['surname']}!")
        return user
    else:
        print("Incorrect password.")
        return None

def delete_user(session, admin_user, username):
    if admin_user["role"].lower() != "admin":
        print("Only admins can delete users.")
        return False
    session.run("MATCH (u:User {username: $username}) DELETE u", {"username": username})
    print("User deleted.")
    return True

def update_user(session, current_user, user_id, **kwargs):
    # Eğer güncellemeyi yapan kişi kendisi ise veya admin ise güncellemeye izin ver
    if current_user["role"].lower() != "admin" and current_user["user_id"] != user_id:
        print("Only admins can update other users.")
        return False
    set_statements = []
    params = {"user_id": user_id}
    for key, value in kwargs.items():
        set_statements.append(f"u.{key} = ${key}")
        params[key] = value
    if not set_statements:
        return False
    query = "MATCH (u:User {user_id: $user_id}) SET " + ", ".join(set_statements) + " RETURN u"
    result = session.run(query, params)
    if result.single():
        print(f"User {user_id} updated: {kwargs}")
        return True
    else:
        print("User not found.")
        return False

def create_admin_user(session):
    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
    ADMIN_NAME = os.getenv("ADMIN_NAME")
    ADMIN_SURNAME = os.getenv("ADMIN_SURNAME")
    result = session.run("MATCH (u:User {username: $username}) RETURN u LIMIT 1", {"username": ADMIN_USERNAME})
    if result.single():
        print("Admin user already exists.")
        return
    result = session.run("MATCH (s:School {name: 'DefaultSchool'}) RETURN s LIMIT 1")
    record = result.single()
    if not record:
        # Eğer DefaultSchool yoksa oluştur
        new_school_id = str(uuid4())
        session.run("CREATE (s:School {school_id: $school_id, name: 'DefaultSchool'})", {"school_id": new_school_id})
        result = session.run("MATCH (s:School {name: 'DefaultSchool'}) RETURN s LIMIT 1")
        record = result.single()
    school = record["s"]
    user_id = str(uuid4())
    hashed_pw = hash_password(ADMIN_PASSWORD)
    session.run("""
    CREATE (u:User {
        user_id: $user_id,
        username: $username,
        password: $password,
        name: $name,
        surname: $surname,
        role: 'admin',
        class_name: '',
        attempts: 0,
        score_avg: 0,
        school_id: $school_id
    })
    """, {
        "user_id": user_id,
        "username": ADMIN_USERNAME,
        "password": hashed_pw,
        "name": ADMIN_NAME,
        "surname": ADMIN_SURNAME,
        "school_id": school.get("school_id", "default-school")
    })
    print("Admin user created successfully.")
