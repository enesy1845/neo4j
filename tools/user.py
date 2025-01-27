# tools/user.py
from sqlalchemy.orm import Session
from tools.utils import hash_password, check_password
from tools.models import User, School
import os

# Eskiden SECTION_MAPPING vb. yoktu veya çokluydu. Artık tekil "registered_section" bekliyoruz.
SECTION_MAP = {
    "math": "1",
    "english": "2",
    "physics": "3",
    "chemistry": "4"
}

def register_user(db: Session, username, password, name, surname, class_name, role, registered_section=None):
    # Aynı username varsa kayda izin vermiyoruz
    existing = db.query(User).filter(User.username == username).first()
    if existing:
        print("Username already exists.")
        return False
    
    # DefaultSchool çek
    default_school = db.query(School).filter(School.name == "DefaultSchool").first()
    if not default_school:
        print("DefaultSchool not found.")
        return False
    
    hashed_pw = hash_password(password)
    user = User(
        username=username,
        password=hashed_pw,
        name=name,
        surname=surname,
        role=role.lower(),
        school_id=default_school.school_id
    )

    # Öğretmen rolünde tekil "registered_section" map
    if user.role == "teacher":
        # Örn. "math" -> "1"
        if registered_section and registered_section in SECTION_MAP:
            user.registered_section = SECTION_MAP[registered_section]
        else:
            user.registered_section = None

        # Teacher aynı anda birden çok sınıfa bakabilir (class_name => virgülle saklıyoruz)
        # Front-end'den "7-A,7-B" gibi gelebilir
        user.class_name = class_name
    else:
        # Öğrenci ise tek bir sınıf (class_name)
        user.class_name = class_name
        # Otomatik okul_no atama
        max_no = db.query(User.okul_no).filter(User.role == "student").order_by(User.okul_no.desc()).first()
        next_no = 1
        if max_no and max_no[0]:
            next_no = max_no[0] + 1
        user.okul_no = next_no

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

def add_user(db: Session, admin_user, **kwargs):
    if admin_user.role.lower() != 'admin':
        print("Only admins can add users.")
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

    # Teacher section
    if "role" in kwargs and kwargs["role"] and kwargs["role"].lower() == "teacher":
        if "registered_section" in kwargs and kwargs["registered_section"]:
            rs_key = kwargs["registered_section"]
            if rs_key in SECTION_MAP:
                kwargs["registered_section"] = SECTION_MAP[rs_key]
            else:
                kwargs["registered_section"] = None

    for key, value in kwargs.items():
        if hasattr(user, key) and value is not None:
            if key == "password":
                value = hash_password(value)
            setattr(user, key, value)

    db.commit()
    print("User updated.")
    return True

def create_admin_user(engine):
    from sqlalchemy.orm import sessionmaker
    from tools.models import User, School
    from dotenv import load_dotenv
    load_dotenv()

    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
    ADMIN_NAME = os.getenv("ADMIN_NAME")
    ADMIN_SURNAME = os.getenv("ADMIN_SURNAME")

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == ADMIN_USERNAME).first()
        if admin:
            print("Admin user already exists.")
            return
        
        default_school = db.query(School).filter(School.name == "DefaultSchool").first()
        if not default_school:
            print("DefaultSchool not found. Creating DefaultSchool.")
            default_school = School(name="DefaultSchool")
            db.add(default_school)
            db.commit()
            db.refresh(default_school)

        hashed_pw = hash_password(ADMIN_PASSWORD)
        admin_user = User(
            username=ADMIN_USERNAME,
            password=hashed_pw,
            name=ADMIN_NAME,
            surname=ADMIN_SURNAME,
            role="admin",
            class_name="",
            school_id=default_school.school_id
        )
        db.add(admin_user)
        db.commit()
        print("Admin user created successfully.")
    except Exception as e:
        print(f"Error creating admin user: {e}")
    finally:
        db.close()
