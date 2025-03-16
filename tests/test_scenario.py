# tests/test_scenario.py
import sys
import os
import pytest
import random
from fastapi.testclient import TestClient
from tools.database import init_db, get_db
import logging
import uuid
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import app
client = TestClient(app)
# Use English-friendly teacher names to avoid Turkish characters in usernames.
teacher_first_names = ["Ali", "Veli", "Mustafa", "Emre", "Kerem", "Berk", "Caner"]
teacher_last_names = ["Yilmaz", "Kaya", "Demir", "Sahin", "Celik", "Arslan", "Aslan"]
student_first_names = ["Ahmet", "Mehmet", "Mustafa", "Ali", "Veli", "Okan", "Emre", "Can", "Deniz", "Baran"]
student_last_names = ["Yildiz", "Ozturk", "Aydin", "Simsek", "Arslan", "Guler", "Kilic", "Cetin", "Aksoy", "Koc"]
class_pool = ["7-A", "7-B", "7-C", "7-D"]
section_pool = [str(x) for x in range(1, 5)]
@pytest.fixture(scope="session", autouse=True)
def setup_db():
    init_db()
    # Removed duplicate creation of DefaultSchool to avoid multiple default schools.
    yield
@pytest.fixture
def admin_user():
    username = "ADMIN"
    password = "ADMINpassword1"  # Ensure password meets complexity
    name = "ADMIN"
    surname = "ADMIN"
    class_name = "AdminClass"
    role = "admin"
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
        print(f"Logging in user {username}: Success.")
        return headers
    else:
        print(f"Login failed for {username}: {response.json()}")
        return None
@pytest.fixture
def teacher_users():
    teachers = []
    num_teachers = 4
    for _ in range(num_teachers):
        first_name = random.choice(teacher_first_names)
        last_name = random.choice(teacher_last_names)
        rand_suffix = random.randint(100, 999)
        unique_part = uuid.uuid4().hex[:6]  # unique 6 characters
        username = f"{first_name.lower()}{last_name.lower()}{rand_suffix}_{unique_part}"
        password = f"TeacherPass{rand_suffix}"  # Must meet complexity requirements
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
@pytest.fixture
def student_users():
    students = []
    num_students = 5
    for _ in range(num_students):
        first_name = random.choice(student_first_names)
        last_name = random.choice(student_last_names)
        rand_suffix = random.randint(100, 999)
        unique_part = uuid.uuid4().hex[:6]  # unique 6 characters
        username = f"{first_name.lower()}{last_name.lower()}{rand_suffix}_{unique_part}"
        password = f"StudentPass{rand_suffix}"  # Password complexity must be met
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
def test_full_scenario(admin_user, teacher_users, student_users):
    print("\n--- Admin: List all users ---")
    response = client.get("/users/", headers=admin_user)
    print(f"GET /users/ - Status Code: {response.status_code}")
    assert response.status_code == 200
    users = response.json()
    print(f"Users before update/delete: {users}")
    assert isinstance(users, list)
    for idx, student_headers in enumerate(student_users, start=1):
        print(f"\n--- Student {idx}: Starting Exam ---")
        response = client.post("/exams/start", headers=student_headers)
        print(f"POST /exams/start - Status Code: {response.status_code} - Response: {response.json()}")
        assert response.status_code == 200
        data = response.json()
        exam_id = data["exam_id"]
        questions = data["questions"]
        session = get_db()
        answers_payload = {}
        for sec, qs in questions.items():
            for q in qs:
                result = session.run("""
                MATCH (q:Question {id: $qid})-[:HAS_CHOICE]->(c:Choice)
                WHERE c.is_correct = true
                RETURN c.choice_text as correct
                LIMIT 1
                """, {"qid": q["question_id"]})
                record = result.single()
                correct_answer = record["correct"] if record else "A"
                available = [choice["choice_text"] for choice in q.get("choices", [])]
                import random
                if random.random() < 0.7:
                    selected_answer = correct_answer
                else:
                    wrong = [ans for ans in available if ans.strip().lower() != correct_answer.strip().lower()]
                    selected_answer = random.choice(wrong) if wrong else correct_answer
                answers_payload[q["question_id"]] = {"selected_texts": [selected_answer]}
        session.close()
        submit_payload = {
            "exam_id": exam_id,
            "answers": answers_payload
        }
        response = client.post("/exams/submit", json=submit_payload, headers=student_headers)
        print(f"POST /exams/submit - Status Code: {response.status_code} - Response: {response.json()}")
        assert response.status_code == 200
