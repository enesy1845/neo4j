# tests/test_scenario.py
import sys
import random
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from tools.database import init_db, get_db
from tools.user import register_user
from tools.exam import select_questions, process_results
from tools.models import User, Exam, ExamAnswer, Statistics
from tools.result import view_results
from sqlalchemy.orm import Session

def reset_db_except_questions_and_answers(db: Session):
    db.query(ExamAnswer).delete()
    db.query(Statistics).delete()
    db.query(Exam).delete()
    db.query(User).filter(User.role != 'admin').delete()
    db.commit()
    print("Database reset completed (except questions and answers).")

def create_teachers(db: Session, num_teachers=5):
    for i in range(num_teachers):
        username = f"teacher{i}"
        password = "password123"
        name = f"TeacherName{i}"
        surname = f"TeacherSurname{i}"
        class_name = "7-d"
        role = "teacher"
        registered_section = str(random.randint(1,4))
        register_user(db, username, password, name, surname, class_name, role, registered_section)

def create_students(db: Session, num_students=10):
    classes = ["7-a", "7-b", "7-c", "7-d"]
    for i in range(num_students):
        username = f"student{i}"
        password = "password123"
        name = f"StudentName{i}"
        surname = f"StudentSurname{i}"
        class_name = random.choice(classes)
        role = "student"
        register_user(db, username, password, name, surname, class_name, role)

def simulate_exam_for_student(db: Session, user: User):
    selected_questions = select_questions(db, user)
    if not selected_questions:
        print(f"No questions available for {user.username}.")
        return

    user_answers = {}
    for section, questions in selected_questions.items():
        for q in questions:
            if q.type == 'true_false':
                user_answer = random.choice(['true', 'false'])
            elif q.type == 'single_choice':
                user_answer = random.choice(['a', 'b', 'c', 'd'])
            elif q.type == 'multiple_choice':
                options = ['a', 'b', 'c', 'd']
                chosen = random.sample(options, random.randint(1,4))
                user_answer = ','.join(chosen)
            elif q.type == 'ordering':
                options = ['a','b','c','d']
                random.shuffle(options)
                user_answer = ','.join(options)
            else:
                user_answer = ""
            user_answers[q.id] = user_answer

    end_time = datetime.now()
    process_results(db, user, selected_questions, user_answers, end_time)
    print(f"Exam completed for {user.username}.")

def view_all_students_results(db: Session):
    students = db.query(User).filter(User.role == 'student').all()
    for s in students:
        view_results(db, s)

def run_test_scenario():
    with next(get_db()) as db:
        init_db()
        reset_db_except_questions_and_answers(db)

        # Admin user kontrol
        admin_user = db.query(User).filter(User.role == 'admin').first()
        if not admin_user:
            # Tekrar init_db'de admin yaratacak
            pass

        create_teachers(db, 5)
        create_students(db, 10)
        db.commit()

        students = db.query(User).filter(User.role == 'student').all()
        for s in students:
            simulate_exam_for_student(db, s)

        view_all_students_results(db)

        from main import view_admin_statistics
        view_admin_statistics(db)

def run_tests():
    print("Running updated test scenario...")
    run_test_scenario()
    print("Test scenario completed.")

if __name__ == "__main__":
    run_tests()
