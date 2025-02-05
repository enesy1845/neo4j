import sys
import os
import pytest
import random
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from tools.database import init_db, SessionLocal
from tools.models import Question, School, User, QuestionChoice
import logging

# Adjust the PYTHONPATH so the app is discoverable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import app
client = TestClient(app)

# -------------------------
# Define name pools for realistic names
# -------------------------
teacher_first_names = ["Ali", "Veli", "Mustafa", "Emre", "Kerem", "Berk", "Caner"]
teacher_last_names = ["Yılmaz", "Kaya", "Demir", "Şahin", "Çelik", "Arslan", "Aslan"]
student_first_names = ["Ahmet", "Mehmet", "Mustafa", "Ali", "Veli", "Okan", "Emre", "Can", "Deniz", "Baran"]
student_last_names = ["Yıldız", "Öztürk", "Aydın", "Şimşek", "Arslan", "Güler", "Kılıç", "Çetin", "Aksoy", "Koç"]

# Pools for classes and sections
class_pool = ["7-A", "7-B", "7-C", "7-D"]
section_pool = [str(x) for x in range(1, 5)]  # "1", "2", "3", "4"

# -------------------------
# Setup database fixture (do not drop data)
# -------------------------
@pytest.fixture(scope="session", autouse=True)
def setup_db():
    from tools.database import Base, engine
    # Do not drop tables so data is preserved
    init_db()  # Create tables if they don't exist
    # Seed initial data if necessary (e.g. DefaultSchool)
    db = SessionLocal()
    try:
        school = db.query(School).filter(School.name == "DefaultSchool").first()
        if not school:
            school = School(name="DefaultSchool")
            db.add(school)
            db.commit()
            db.refresh(school)
    except Exception as e:
        print(f"Error setting up test database: {e}")
    finally:
        db.close()
    yield
    # Do not drop tables on teardown

# -------------------------
# Admin user fixture (using "ADMIN" credentials)
# -------------------------
@pytest.fixture
def admin_user():
    username = "ADMIN"
    password = "ADMIN"
    name = "ADMIN"
    surname = "ADMIN"
    class_name = "AdminClass"
    role = "admin"
    # Try to register the admin; if it already exists, print a message.
    response = client.post("/auth/register", json={
        "username": username,
        "password": password,
        "name": name,
        "surname": surname,
        "class_name": class_name,
        "role": role
    })
    if response.status_code != 200:
        print(f"Admin registration may have already occurred: {response.json()}")
    response = client.post("/auth/login", json={"username": username, "password": password})
    assert response.status_code == 200, f"Admin login failed: {response.json()}"
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    return headers

# -------------------------
# Helper functions for user registration and login
# -------------------------
def register_user(username, password, name, surname, class_name, role, registered_section=None):
    payload = {
        "username": username,
        "password": password,
        "name": name,
        "surname": surname,
        "class_name": class_name,
        "role": role
    }
    if registered_section:
        payload["registered_section"] = registered_section
    response = client.post("/auth/register", json=payload)
    print(f"Registering user {username}: {response.status_code} - {response.json()}")
    return response

def login_user(username, password):
    response = client.post("/auth/login", json={"username": username, "password": password})
    if response.status_code == 200:
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print(f"Logging in user {username}: Success. Username: {username}, Password: {password}")
        return headers
    else:
        print(f"Login failed for {username}: {response.json()}")
        return None

# -------------------------
# Teacher users fixture: create 4 teachers with realistic names
# -------------------------
@pytest.fixture
def teacher_users():
    teachers = []
    num_teachers = 4
    for _ in range(num_teachers):
        first_name = random.choice(teacher_first_names)
        last_name = random.choice(teacher_last_names)
        rand_suffix = random.randint(100, 999)
        username = f"{first_name.lower()}{last_name.lower()}{rand_suffix}"
        password = f"TeacherPass{rand_suffix}"
        name = first_name
        surname = last_name
        class_name = random.choice(class_pool)
        registered_section = random.choice(section_pool)
        role = "teacher"
        response = register_user(username, password, name, surname, class_name, role, registered_section)
        assert response.status_code == 200, f"Registration failed for teacher {username}"
        headers = login_user(username, password)
        assert headers is not None, f"Login failed for teacher {username}"
        teachers.append(headers)
    return teachers

# -------------------------
# Student users fixture: create 5 students with realistic names
# -------------------------
@pytest.fixture
def student_users():
    students = []
    num_students = 5
    for _ in range(num_students):
        first_name = random.choice(student_first_names)
        last_name = random.choice(student_last_names)
        rand_suffix = random.randint(100, 999)
        username = f"{first_name.lower()}{last_name.lower()}{rand_suffix}"
        password = f"StudentPass{rand_suffix}"
        name = first_name
        surname = last_name
        class_name = random.choice(class_pool)
        role = "student"
        response = register_user(username, password, name, surname, class_name, role)
        assert response.status_code == 200, f"Registration failed for student {username}"
        headers = login_user(username, password)
        assert headers is not None, f"Login failed for student {username}"
        students.append(headers)
    return students

# -------------------------
# Main test scenario: admin lists users and each student takes an exam with simulated answers
# -------------------------
def test_full_scenario(admin_user, teacher_users, student_users):
    # Admin lists all users
    print("\n--- Admin: List all users ---")
    response = client.get("/users/", headers=admin_user)
    print(f"GET /users/ - Status Code: {response.status_code}")
    assert response.status_code == 200
    users = response.json()
    print(f"Users before update/delete: {users}")
    assert isinstance(users, list)
    
    # For each student, simulate exam participation with realistic answers
    for idx, student_headers in enumerate(student_users, start=1):
        print(f"\n--- Student {idx}: Starting Exam ---")
        response = client.post("/exams/start", headers=student_headers)
        print(f"POST /exams/start - Status Code: {response.status_code} - Response: {response.json()}")
        assert response.status_code == 200
        data = response.json()
        exam_id = data["exam_id"]
        questions = data["questions"]
        
        # Open a database session to fetch correct answers from the QuestionChoice table
        db = SessionLocal()
        answers_payload = {}
        # For each section and question in the exam:
        for sec, qs in questions.items():
            for q in qs:
                q_id = q["question_id"]
                # Query the correct answer(s)
                correct_choices = db.query(QuestionChoice).filter(
                    QuestionChoice.question_id == q_id,
                    QuestionChoice.is_correct == True
                ).all()
                if correct_choices:
                    # For simplicity, pick the first correct answer
                    correct_answer = correct_choices[0].choice_text
                else:
                    correct_answer = "A"
                
                # Retrieve available choices from the question data
                available_choices = [choice["choice_text"] for choice in q.get("choices", [])]
                
                # Simulate: 70% chance to answer correctly, else choose a wrong answer if available
                if random.random() < 0.7:
                    selected_answer = correct_answer
                else:
                    wrong_choices = [ans for ans in available_choices if ans.strip().lower() != correct_answer.strip().lower()]
                    if wrong_choices:
                        selected_answer = random.choice(wrong_choices)
                    else:
                        selected_answer = correct_answer
                answers_payload[q_id] = {"selected_texts": [selected_answer]}
        db.close()
        
        # Submit the exam with the generated answers_payload
        submit_payload = {
            "exam_id": exam_id,
            "answers": answers_payload
        }
        response = client.post("/exams/submit", json=submit_payload, headers=student_headers)
        print(f"POST /exams/submit - Status Code: {response.status_code} - Response: {response.json()}")
        assert response.status_code == 200
