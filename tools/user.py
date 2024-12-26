# tools/user.py
from tools.utils import hash_password, check_password
from tools.models import User, School
from sqlalchemy.orm import Session

def register_user(db: Session, username, password, name, surname, class_name, role, registered_section=None):
    existing = db.query(User).filter(User.username == username).first()
    if existing:
        print("Username already exists.")
        return False

    hashed_pw = hash_password(password)

    # DefaultSchool'u alalım (seed_initial_data'da eklenmiş olması lazım)
    default_school = db.query(School).filter(School.name == "DefaultSchool").first()
    if not default_school:
        print("DefaultSchool not found in DB. Please check the seeding process.")
        return False

    user = User(
        username=username,
        password=hashed_pw,
        name=name,
        surname=surname,
        phone_number="",
        role=role.lower(),
        attempts=0,
        last_attempt_date=None,
        score1=0,
        score2=0,
        score_avg=0,
        class_name=class_name,
        registered_section=registered_section or "",
        school_id=default_school.school_id  # Varsayılan okulun IDsini setle
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    print("Registration successful.")
    return True


def login_user(db: Session, username, password):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        print("User not found.")
        return None
    if check_password(password, user.password):
        print(f"Welcome, {user.name} {user.surname}!")
        return user
    else:
        print("Incorrect password.")
        return None


def list_users(db: Session):
    users = db.query(User).all()
    print("\n=== User List ===")
    for user in users:
        print(f"Username: {user.username} | Role: {user.role} | Class: {user.class_name} | SchoolID: {user.school_id}")


def add_user(db: Session, admin_user, **kwargs):
    if admin_user.role.lower() != 'admin':
        print("Only admins can add users.")
        return False
    role = kwargs.get('role', '').lower()
    if role not in ['teacher', 'student']:
        print("Role must be either 'teacher' or 'student'.")
        return False
    return register_user(db, **kwargs)


def delete_user(db: Session, admin_user, username):
    if admin_user.role.lower() != 'admin':
        print("Only admins can delete users.")
        return False
    user = db.query(User).filter(User.username == username).first()
    if user:
        db.delete(user)
        db.commit()
        print("User deleted.")
        return True
    else:
        print("User not found.")
        return False


def update_user(db: Session, admin_user, username, **kwargs):
    if admin_user.role.lower() != 'admin':
        print("Only admins can update users.")
        return False
    user = db.query(User).filter(User.username == username).first()
    if not user:
        print("User not found.")
        return False

    for key, value in kwargs.items():
        if hasattr(user, key) and value:
            setattr(user, key, value)

    db.commit()
    print("User updated.")
    return True


def login_panel(db: Session):
    print("\n=== Login ===")
    username = input("Username: ")
    password = input("Password: ")
    user = login_user(db, username, password)
    return user
