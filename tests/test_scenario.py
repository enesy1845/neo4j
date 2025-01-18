# tests/test_full_scenario.py

import sys
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from tools.database import init_db, SessionLocal
from tools.models import Question, Answer, School, User
import logging

# Adjust the PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app

client = TestClient(app)

# Fixtures for setting up and tearing down the database
@pytest.fixture(scope="session", autouse=True)
def setup_db():
    from tools.database import Base, engine
    # Drop and create all tables
    Base.metadata.drop_all(bind=engine)
    init_db()
    # Seed initial data
    db = SessionLocal()
    try:
        # Ensure default school exists
        school = db.query(School).filter(School.name == "DefaultSchool").first()
        if not school:
            school = School(name="DefaultSchool")
            db.add(school)
            db.commit()
            db.refresh(school)
        
        # Add sample questions for all sections
        for section in range(1, 5):
            for q_num in range(1, 6):
                external_id = f"section{section}_q{q_num}"
                question_text = f"Sample question {q_num} for section {section}?"
                correct_answer = "A"  # Simplified correct answer
                question = Question(
                    external_id=external_id,
                    section=section,
                    question=question_text,
                    points=1,
                    type="single_choice"
                )
                db.add(question)
                db.commit()
                db.refresh(question)
                
                answer = Answer(
                    question_id=question.id,
                    correct_answer=correct_answer
                )
                db.add(answer)
                db.commit()
    except Exception as e:
        print(f"Error setting up test database: {e}")
    finally:
        db.close()
    
    yield
    
    # # Teardown: Drop all tables after tests
    # Base.metadata.drop_all(bind=engine)

# Helper functions for user operations
def register_user(username, password, name, surname, class_name, role, registered_section=None):
    reg_payload = {
        "username": username,
        "password": password,
        "name": name,
        "surname": surname,
        "class_name": class_name,
        "role": role
    }
    if registered_section:
        reg_payload["registered_section"] = registered_section
    response = client.post("/auth/register", json=reg_payload)
    print(f"Registering user {username}: {response.status_code} - {response.json()}")
    return response

def login_user(username, password):
    login_payload = {
        "username": username,
        "password": password
    }
    response = client.post("/auth/login", json=login_payload)
    if response.status_code == 200:
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print(f"Logging in user {username}: Success")
        return headers
    else:
        print(f"Logging in user {username}: Failed - {response.json()}")
        return None

# Fixtures for different user roles
@pytest.fixture
def admin_user():
    username = "admin_user"
    password = "adminpass"
    name = "Admin"
    surname = "User"
    class_name = "AdminClass"
    role = "admin"
    # Register admin user
    response = register_user(username, password, name, surname, class_name, role)
    assert response.status_code == 200
    # Login admin user
    headers = login_user(username, password)
    assert headers is not None
    return headers

@pytest.fixture
def teacher_users():
    teachers = []
    for i in range(1, 5):
        username = f"teacher{i}"
        password = "teacherpass"
        name = f"TeacherName{i}"
        surname = f"TeacherSurname{i}"
        class_name = f"Class{i}"
        role = "teacher"
        registered_section = str(i)  # Sections 1 to 4
        response = register_user(username, password, name, surname, class_name, role, registered_section)
        assert response.status_code == 200
        headers = login_user(username, password)
        assert headers is not None
        teachers.append(headers)
    return teachers

@pytest.fixture
def student_users():
    students = []
    for i in range(1, 5):
        username = f"student{i}"
        password = "studentpass"
        name = f"StudentName{i}"
        surname = f"StudentSurname{i}"
        class_name = f"Class{i}"
        role = "student"
        response = register_user(username, password, name, surname, class_name, role)
        assert response.status_code == 200
        headers = login_user(username, password)
        assert headers is not None
        students.append(headers)
    return students

# Combined Test Function with Detailed Output
@pytest.mark.order(1)
def test_full_scenario(admin_user, teacher_users, student_users):
    # --- Admin: List all users ---
    print("\n--- Admin: List all users ---")
    response = client.get("/users/", headers=admin_user)
    print(f"GET /users/ - Status Code: {response.status_code}")
    assert response.status_code == 200
    users = response.json()
    print(f"Users before update/delete: {users}")
    assert isinstance(users, list)
    assert len(users) >= 1  # At least admin exists

    # --- Admin: Update a non-admin user (e.g., promote a teacher to admin) ---
    print("\n--- Admin: Update a non-admin user ---")
    admin_username = "admin_user"
    user_to_update = None
    for user in users:
        if user["username"] != admin_username:
            user_to_update = user
            break

    if user_to_update:
        username = user_to_update["username"]
        print(f"Updating user {username} to admin.")
        
        # Admin: Update the selected user's role to 'admin'
        update_payload = {"role": "admin"}
        response = client.put(f"/users/{username}", json=update_payload, headers=admin_user)
        print(f"PUT /users/{username} - Status Code: {response.status_code} - Response: {response.json()}")
        assert response.status_code == 200
        assert response.json()["message"] == f"User {username} updated successfully."
        
        # Admin: Delete the same user
        print(f"Deleting user {username}.")
        response = client.delete(f"/users/{username}", headers=admin_user)
        print(f"DELETE /users/{username} - Status Code: {response.status_code} - Response: {response.json()}")
        assert response.status_code == 200
        assert response.json()["message"] == f"User {username} deleted successfully."
    
    # --- Admin: Attempt to list users after deletion ---
    print("\n--- Admin: List all users after deletion ---")
    response = client.get("/users/", headers=admin_user)
    print(f"GET /users/ - Status Code: {response.status_code}")
    assert response.status_code == 200
    users_after = response.json()
    print(f"Users after update/delete: {users_after}")
    
    if user_to_update:
        assert len(users_after) == len(users) - 1
    else:
        # If no user was found to update/delete, the user count remains the same
        assert len(users_after) == len(users)
    
    # --- Teachers: Add new questions ---
    print("\n--- Teachers: Add new questions ---")
    for idx, teacher_headers in enumerate(teacher_users, start=1):
        add_question_payload = {
            "question_text": f"New question {idx} for section {idx}?",
            "q_type": "single_choice",
            "points": 2,
            "correct_answer": "B"
        }
        response = client.post("/questions/", json=add_question_payload, headers=teacher_headers)
        print(f"POST /questions/ by Teacher {idx} - Status Code: {response.status_code} - Response: {response.json()}")
        assert response.status_code == 200
        assert response.json()["message"] == "Question added successfully"
        assert "external_id" in response.json()
    
    # --- Teachers: List all questions ---
    print("\n--- Teachers: List all questions ---")
    for idx, teacher_headers in enumerate(teacher_users, start=1):
        response = client.get("/questions/", headers=teacher_headers)
        print(f"GET /questions/ by Teacher {idx} - Status Code: {response.status_code}")
        assert response.status_code == 200
        questions = response.json()
        print(f"Number of questions: {len(questions)}")
        assert isinstance(questions, list)
        assert len(questions) >= 20  # Initial 20 questions + new ones
    
    # --- Students: Take Exams ---
    print("\n--- Students: Take Exams ---")
    for idx, student_headers in enumerate(student_users, start=1):
        print(f"\n--- Student {idx}: Starting Exam ---")
        response = client.post("/exams/start", headers=student_headers)
        print(f"POST /exams/start - Status Code: {response.status_code} - Response: {response.json()}")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Exam started"
        assert "exam_id" in data
        assert "questions" in data
        exam_id = data["exam_id"]
        questions = data["questions"]
        
        # Prepare answers based on question types
        answers_payload = {}
        for section in questions:
            for q in section["questions"]:
                q_id = q["question_id"]
                q_type = q["type"]
                # For simplicity, always answer correctly
                if q_type == "single_choice":
                    answers_payload[q_id] = "A"  # Correct answer as per initial setup
                elif q_type == "multiple_choice":
                    answers_payload[q_id] = "A,B"  # Assuming correct answers are "A,B"
                elif q_type == "true_false":
                    answers_payload[q_id] = "A"  # Assuming 'A' stands for 'True'
                elif q_type == "ordering":
                    answers_payload[q_id] = "1,2,3"  # Assuming correct order
                else:
                    answers_payload[q_id] = "A"  # Default answer
        
        # Submit the exam
        print(f"--- Student {idx}: Submitting Exam ---")
        submit_payload = {
            "exam_id": exam_id,
            "answers": answers_payload
        }
        response = client.post("/exams/submit", json=submit_payload, headers=student_headers)
        print(f"POST /exams/submit - Status Code: {response.status_code} - Response: {response.json()}")
        assert response.status_code == 200
        assert response.json()["message"] == "Exam submitted successfully."
    
    # --- Teachers: View Statistics ---
    print("\n--- Teachers: View Statistics ---")
    for idx, teacher_headers in enumerate(teacher_users, start=1):
        response = client.get("/stats/", headers=teacher_headers)
        print(f"GET /stats/ by Teacher {idx} - Status Code: {response.status_code} - Response: {response.json()}")
        assert response.status_code == 200
        stats = response.json()
        print(f"Statistics for Teacher {idx}: {stats}")
        assert isinstance(stats, list)
        assert len(stats) == 1  # Each teacher has one section's stats
        stat = stats[0]
        assert stat["section_number"] == idx
        assert stat["class_name"] == f"Class{idx}"
        # Additional assertions can be added here to verify the correctness of statistics