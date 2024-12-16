# tests/test_scenario.py

import sys
import os
import random
from datetime import datetime
from pathlib import Path

# Proje dizinini sys.path'e ekleyin
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from tools.user import register_user, login_user
from tools.exam import select_questions, process_results
from tools.utils import load_json, save_json
from tools.result import view_results  # view_results fonksiyonunu içe aktarın

def create_random_students(num_students=5):
    for i in range(num_students):
        username = f"student{i}"
        password = "password123"
        name = f"StudentName{i}"
        surname = f"StudentSurname{i}"
        class_name = random.choice(["7-a", "7-b", "7-c", "7-d"])  # Doğru sınıf isimleri
        role = "student"
        registered_section = ""
        success = register_user(username, password, name, surname, class_name, role, registered_section)
        if success:
            print(f"Registration successful for {username}.")
        else:
            print(f"Registration failed for {username}.")

def create_teacher(username="teacher1", password="password123"):
    success = register_user(
        username=username,
        password=password,
        name="TeacherName",
        surname="TeacherSurname",
        class_name="7-d",  # Öğretmeni '7-d' sınıfına atayın
        role="teacher",
        registered_section="1"
    )
    if success:
        print(f"Teacher {username} registered successfully.")
    else:
        print(f"Failed to register teacher {username}.")

def simulate_exam_for_student(student_username, student_password, exam_number):
    # Öğrenciye giriş yap
    user = login_user(student_username, student_password)
    if not user:
        print(f"Login failed for {student_username}.")
        return
    # Sınav için soruları seç
    selected_questions = select_questions(user)
    if not selected_questions:
        print(f"No questions available for {student_username}.")
        return
    # Rastgele cevaplar üret
    user_answers = {}
    answers = load_json(BASE_DIR / 'answers' / 'answers.json')  # Doğru cevapları yükle
    for section, questions in selected_questions.items():
        for question in questions:
            q_id = question['id']
            q_type = question['type']
            correct_answer = answers.get(q_id)
            if q_type == 'true_false':
                user_answer = random.choice(['true', 'false'])
            elif q_type == 'single_choice':
                options = ['A', 'B', 'C', 'D']
                user_answer = random.choice(options)
            elif q_type == 'multiple_choice':
                options = ['A', 'B', 'C', 'D']
                selected = random.sample(options, random.randint(1, 4))
                user_answer = ','.join(selected)
            elif q_type == 'ordering':
                options = ['A', 'B', 'C', 'D']
                user_answer = ','.join(random.sample(options, len(options)))
            else:
                user_answer = ""
            user_answers[q_id] = user_answer
    # Sınav bitiş zamanını kaydet (simüle edilmiş)
    end_time = datetime.now().isoformat()
    # Sonuçları işle
    process_results(user, selected_questions, user_answers, end_time)
    print(f"Sınav {exam_number} tamamlandı for {student_username}.")
    
    # Öğrencinin sonuçlarını görüntüle
    view_results(user)

def simulate_exams_for_all_students(num_students=5, exams_per_student=2):
    for i in range(num_students):
        username = f"student{i}"
        password = "password123"
        for exam_num in range(1, exams_per_student + 1):
            simulate_exam_for_student(username, password, exam_num)

def view_teacher_statistics():
    from main import view_teacher_statistics  # Ana dosyanızın adını doğru şekilde kullanın
    # Öğretmen bilgilerini al (örneğin, varsayılan öğretmen)
    teacher_username = "teacher1"  # Test için oluşturduğunuz öğretmenin kullanıcı adını kullanın
    teacher_password = "password123"
    user = login_user(teacher_username, teacher_password)
    if not user:
        print(f"Login failed for {teacher_username}.")
        return
    view_teacher_statistics(user)

def reset_files():
    files_to_reset = [
        BASE_DIR / 'users' / 'users.json',
        BASE_DIR / 'users' / 'statistics.json',
        BASE_DIR / 'users' / 'user_answers.json',
    ]
    for file in files_to_reset:
        if file.exists():
            file.unlink()
            print(f"Deleted {file}")
    print("All files have been reset.")

def initialize_files():
    # Sıfırlama sonrası admin kullanıcıyı oluşturmak için initialize_user fonksiyonunu çağırabilirsiniz
    success = register_user(
        username="admin",
        password="adminpass",
        name="Admin",
        surname="User",
        class_name="7-a",  # Admin için bir sınıf atayın
        role="admin",
        registered_section=""
    )
    if success:
        print("Admin user initialized.")
    else:
        print("Failed to initialize admin user.")

def run_test_scenario():
    # Test öncesi reset
    reset_files()
    # Initialize admin user
    initialize_files()
    # 1. Öğretmen kullanıcıyı oluştur
    create_teacher()
    # 2. Öğrencileri oluştur
    create_random_students(num_students=5)
    # 3. Her öğrenci için iki sınavı simüle et
    simulate_exams_for_all_students(num_students=5, exams_per_student=2)
    # 4. Öğretmen istatistiklerini görüntüle
    view_teacher_statistics()

def run_tests():
    # Burada mevcut test senaryosu kodunuz olacak
    print("Running test scenarios...")
    # Örneğin, mevcut test senaryosu fonksiyonlarını çağırabilirsiniz
    run_test_scenario()

if __name__ == "__main__":
    run_tests()
