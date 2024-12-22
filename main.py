## main.py
import sys
import os
from tools.user import register_user, login_panel, list_users, add_user, delete_user, update_user
from tools.exam import start_exam
from tools.result import view_results
from tools.database import get_db, init_db
from sqlalchemy.orm import Session
from tools.token_generator import renew_token_if_needed, token_gnrtr

def initialize_admin(db: Session):
    from tools.models import User
    admins = db.query(User).filter(User.role == "admin").all()
    if not admins:
        username = os.getenv("ADMIN_USERNAME", "admin")
        password = os.getenv("ADMIN_PASSWORD", "adminpass")
        name = os.getenv("ADMIN_NAME", "Admin")
        surname = os.getenv("ADMIN_SURNAME", "User")
        class_name = "7-a"
        role = "admin"
        register_user(db, username, password, name, surname, class_name, role)
        print(f"Admin created: {username}/{password}")
    else:
        print("Admin kullanıcı(ları) zaten mevcut.\n")

def main_menu():
    try:
        # Veritabanı başlatma
        init_db()
        print("Veritabanı başlatıldı.")
        with next(get_db()) as db:
            initialize_admin(db)
            

        while True:
            print("\n=== Welcome to the Examination System ===")
            print("1. Register")
            print("2. Login")
            print("3. Exit")
            choice = input("Choose an option: ").strip()

            if choice == '1':
                register_panel()
            elif choice == '2':
                user = login_panel(db)
                if user:
                    token_gnrtr(user.user_id)
                    if user.role == 'student':
                        student_panel(user)
                    elif user.role == 'teacher':
                        teacher_panel(user)
                    elif user.role == 'admin':
                        admin_panel(user)
                    else:
                        print("Unknown role. Please contact the administrator.")
                else:
                    print("Login failed. Please try again.")
            elif choice == '3':
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please enter 1, 2, or 3.\n")
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)


def register_panel():
    with next(get_db()) as db:
        print("\n=== Register ===")
        username = input("Username: ")
        password = input("Password: ")
        name = input("Name: ")
        surname = input("Surname: ")
        class_name = input("Class (7-a,7-b,7-c,7-d): ")
        role = input("Role (teacher/student): ").lower()
        if role not in ['teacher', 'student']:
            print("Invalid role selected. Only 'teacher' or 'student' roles are allowed.")
            return
        registered_section = None
        if role == 'teacher':
            registered_section = input("Registered Section (1-4): ")
            if registered_section not in ['1', '2', '3', '4']:
                print("Invalid section. Must be between 1 and 4.")
                return
        success = register_user(db, username, password, name, surname, class_name, role, registered_section)
        if success:
            print("Registration successful.\n")
        else:
            print("Registration failed.\n")

# def login_panel():
#     print("\n=== Login ===")
#     username = input("Username: ")
#     password = input("Password: ")  
#     user = login_user(username, password)
#     return user

def student_panel(user):
    while True:
        print("\n=== Student Panel ===")
        print("1. Start Exam")
        print("2. View Results")
        print("3. Logout")
        choice = input("Choose an option: ")
        renew_token_if_needed()
        if choice == '1':
            with next(get_db()) as db:
                if user.attempts < 2:
                    user = db.merge(user)
                    start_exam(db, user)
                    db.refresh(user)
                else:
                    print("You have no remaining exam attempts.\n")
        elif choice == '2':
            with next(get_db()) as db:
                user = db.merge(user)
                view_results(db, user)
        elif choice == '3':
            print("Logged out.\n")
            break
        else:
            print("Invalid choice.\n")

def teacher_panel(user):
    while True:
        print("\n=== Teacher Panel ===")
        print("1. View Statistics")
        print("2. Add Question")
        print("3. Logout")
        choice = input("Choose an option: ")
        renew_token_if_needed()
        print("token gecti")
        if choice == '1':
            with next(get_db()) as db:
                view_teacher_statistics(db, user)
        elif choice == '2':
            with next(get_db()) as db:
                user = db.merge(user)
                add_question_panel(db, user)
        elif choice == '3':
            print("Logged out.\n")
            break
        else:
            print("Invalid choice.\n")

def admin_panel(user):
    while True:
        print("\n=== Admin Panel ===")
        print("1. Manage Users")
        print("2. View User Statistics")
        print("3. Logout")
        choice = input("Choose an option: ")
        renew_token_if_needed()
        if choice == '1':
            manage_users_panel(user)
        elif choice == '2':
            with next(get_db()) as db:
                view_admin_statistics(db)
        elif choice == '3':
            print("Logged out.\n")
            break
        else:
            print("Invalid choice.\n")

def view_teacher_statistics(db, user):
    from rich.console import Console
    from rich.table import Table
    from tools.utils import DEFAULT_SCHOOL_NAME
    from tools.models import Statistics
    console = Console()

    stats = db.query(Statistics).filter(Statistics.school_name == DEFAULT_SCHOOL_NAME).all()
    if not stats:
        console.print("No statistics available.")
        return
    
    classes = {}
    for s in stats:
        if s.class_name not in classes:
            classes[s.class_name] = []
        classes[s.class_name].append(s)

    for class_name, sections_data in classes.items():
        console.print(f"\n[bold underline]Sınıf: {class_name}[/bold underline]")
        table = Table(show_header=True, header_style="bold blue")
        table.add_column("Soru Bölümü", style="cyan", no_wrap=True)
        table.add_column("Doğru Sayısı (DS)", style="green")
        table.add_column("Yanlış Sayısı (YS)", style="red")
        table.add_column("Ortalama Skor (%)", style="magenta")
        for sec_data in sections_data:
            soru_bolumu = f"{sec_data.section_number}s."
            ds = sec_data.correct_questions
            ys = sec_data.wrong_questions
            avg = sec_data.average_score
            table.add_row(soru_bolumu, str(ds), str(ys), f"{avg:.2f}%")
        class_avg = sum([sd.average_score for sd in sections_data]) / len(sections_data)
        console.print(table)
        console.print(f"Sınıf Ortalaması: [bold green]{class_avg:.2f}%[/bold green]")

    all_avg = sum([s.average_score for s in stats]) / len(stats)
    console.print(f"\n[bold underline]Okul Genel İstatistikleri[/bold underline]")
    school_table = Table(show_header=True, header_style="bold blue")
    school_table.add_column("Kategori", style="cyan", no_wrap=True)
    school_table.add_column("Ortalama Skor (%)", style="magenta")
    school_table.add_row("Okul Ortalaması", f"{all_avg:.2f}%")
    console.print(school_table)

def add_question_panel(db, user):
    from tools.models import Question, Answer
    question_text = input("Enter question text: ")
    renew_token_if_needed()
    q_type = input("Enter question type (single_choice/multiple_choice/true_false/ordering): ").lower()
    renew_token_if_needed()
    if q_type not in ['single_choice', 'multiple_choice', 'true_false', 'ordering']:
        print("Invalid question type.")
        return
    try:
        points = int(input("Enter points for the question: "))
        renew_token_if_needed()
    except ValueError:
        print("Points must be an integer.")
        return
    correct_answer = input("Enter correct answer (for multiple answers, separate by commas): ")
    renew_token_if_needed()
    section = user.registered_section
    if not section:
        print("No registered section.")
        return
    q = Question(section=int(section), question=question_text, points=points, type=q_type)
    db.add(q)
    db.commit()
    db.refresh(q)

    ans = Answer(question_id=q.id, correct_answer=correct_answer.strip())
    db.add(ans)
    db.commit()
    print("Question added successfully.\n")

def manage_users_panel(admin_user):
    while True:
        print("\n=== Manage Users ===")
        print("1. Add User")
        print("2. Update User")
        print("3. Delete User")
        print("4. List Users")
        print("5. Back")
        choice = input("Choose an option: ")
        renew_token_if_needed()
        if choice == '1':
            add_user_panel(admin_user)
        elif choice == '2':
            update_user_panel(admin_user)
        elif choice == '3':
            delete_user_panel(admin_user)
        elif choice == '4':
            from tools.database import get_db
            with next(get_db()) as db:
                list_users(db)
        elif choice == '5':
            break
        else:
            print("Invalid choice.\n")

def add_user_panel(admin_user):
    print("\n=== Add User ===")
    username = input("Username: ")
    renew_token_if_needed()
    password = input("Password: ")
    renew_token_if_needed()
    name = input("Name: ")
    renew_token_if_needed()
    surname = input("Surname: ")
    renew_token_if_needed()
    class_name = input("Class (7-a,7-b,7-c,7-d): ")
    renew_token_if_needed()
    role = input("Role (teacher/student): ").lower()
    renew_token_if_needed()
    if role not in ['teacher', 'student']:
        print("Invalid role. Only 'teacher' or 'student' roles are allowed.\n")
        return
    registered_section = None
    if role == 'teacher':
        registered_section = input("Registered Section (1-4): ")
        renew_token_if_needed()
        if registered_section not in ['1', '2', '3', '4']:
            print("Invalid section. Must be between 1 and 4.\n")
            return
    from tools.database import get_db
    with next(get_db()) as db:
        add_user(db, admin_user, username=username, password=password, name=name, surname=surname,
                 class_name=class_name, role=role, registered_section=registered_section)

def update_user_panel(admin_user):
    print("\n=== Update User ===")
    username = input("Enter the username to update: ")
    renew_token_if_needed()
    print("Leave fields blank to keep current values.")
    name = input("New Name: ")
    renew_token_if_needed()
    surname = input("New Surname: ")
    renew_token_if_needed()
    class_name = input("New Class: ")
    renew_token_if_needed()
    role = input("New Role (teacher/student): ").lower()
    renew_token_if_needed()
    if role and role not in ['teacher', 'student']:
        print("Invalid role. Only 'teacher' or 'student' roles are allowed.\n")
        return
    registered_section = None
    if role == 'teacher':
        registered_section = input("Registered Section (1-4): ")
        renew_token_if_needed()
        if registered_section not in ['1', '2', '3', '4']:
            print("Invalid section. Must be between 1 and 4.\n")
            return
    update_fields = {}
    if name:
        update_fields['name'] = name
    if surname:
        update_fields['surname'] = surname
    if class_name:
        update_fields['class_name'] = class_name
    if role:
        update_fields['role'] = role
    if registered_section:
        update_fields['registered_section'] = registered_section
    from tools.database import get_db
    with next(get_db()) as db:
        update_user(db, admin_user, username, **update_fields)

def delete_user_panel(admin_user):
    print("\n=== Delete User ===")
    username = input("Enter the username to delete: ")
    renew_token_if_needed()
    confirm = input(f"Are you sure you want to delete {username}? (y/n): ")
    renew_token_if_needed()
    if confirm.lower() == 'y':
        from tools.database import get_db
        with next(get_db()) as db:
            delete_user(db, admin_user, username)
    else:
        print("Deletion cancelled.\n")

def view_admin_statistics(db: Session):
    from tools.models import Statistics
    stats = db.query(Statistics).all()
    for s in stats:
        print(f"\nSchool: {s.school_name}")
        print(f"  Class: {s.class_name}")
        print(f"    Section {s.section_number} - Correct: {s.correct_questions}, Wrong: {s.wrong_questions}, Average Score: {s.average_score}, Percentage: {s.section_percentage}%")

if __name__ == "__main__":
    main_menu()
