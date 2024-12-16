# main.py

from tools.user import register_user, login_user, list_users, add_user, delete_user, update_user
from tools.exam import start_exam
from tools.result import view_results
from tools.utils import load_json, DEFAULT_SCHOOL_NAME,save_json
import sys
from rich.console import Console
from rich.table import Table
from tests.test_scenario import run_tests
def initialize_admin():
    users_data = load_json('users/users.json')
    admins = [user for user in users_data.get('users', []) if user['role'] == 'admin']
    if not admins:
        print("\n=== İlk Admin Oluşturma ===")
        print("Sistemde hiç admin bulunmamaktadır. Lütfen ilk admin hesabını oluşturun.")
        while True:
            username = input("Username: ")
            password = input("Password: ")
            name = input("Name: ")
            surname = input("Surname: ")
            class_name = "7-a"  # Varsayılan sınıf
            role = "admin"
            success = register_user(username, password, name, surname, class_name, role)
            if success:
                print("İlk admin başarıyla oluşturuldu.\n")
                break
            else:
                print("Admin oluşturulamadı. Lütfen tekrar deneyin.\n")
    else:
        print("Admin kullanıcı(ları) zaten mevcut.\n")

def main_menu():
    initialize_admin()  # Program başlangıcında admini initialize et
    while True:
        print("=== Welcome to the Examination System ===")
        print("1. Register")
        print("2. Login")
        print("3. Exit")
        print("4 Run Test")
        choice = input("Choose an option: ")
        if choice == '1':
            register_panel()
        elif choice == '2':
            user = login_panel()
            if user:
                if user['role'] == 'student':
                    student_panel(user)
                elif user['role'] == 'teacher':
                    teacher_panel(user)
                elif user['role'] == 'admin':
                    admin_panel(user)
        elif choice == '3':
            print("Goodbye!")
            sys.exit()
        elif choice == '4':
            run_tests()
        else:
            print("Invalid choice.\n")

def register_panel():
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
    success = register_user(username, password, name, surname, class_name, role, registered_section)
    if success:
        print("Registration successful.\n")
    else:
        print("Registration failed.\n")

def login_panel():
    print("\n=== Login ===")
    username = input("Username: ")
    password = input("Password: ")
    user = login_user(username, password)
    return user

def student_panel(user):
    while True:
        print("\n=== Student Panel ===")
        print("1. Start Exam")
        print("2. View Results")
        print("3. Logout")
        choice = input("Choose an option: ")
        if choice == '1':
            if user['attempts'] < 2:
                start_exam(user)
            else:
                print("You have no remaining exam attempts.\n")
        elif choice == '2':
            view_results(user)
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
        if choice == '1':
            view_teacher_statistics(user)
        elif choice == '2':
            add_question_panel(user)
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
        if choice == '1':
            manage_users_panel(user)
        elif choice == '2':
            view_admin_statistics()
        elif choice == '3':
            print("Logged out.\n")
            break
        else:
            print("Invalid choice.\n")

def view_teacher_statistics(user):
    statistics = load_json('users/statistics.json')
    console = Console()
    
    for school in statistics['schools']:
        if school['school_name'] == DEFAULT_SCHOOL_NAME:
            # Sınıf Bazında İstatistikler
            for class_name, class_data in school['classes'].items():
                console.print(f"\n[bold underline]Sınıf: {class_name}[/bold underline]")
                table = Table(show_header=True, header_style="bold blue")
                table.add_column("Soru Bölümü", style="cyan", no_wrap=True)
                table.add_column("Doğru Sayısı (DS)", style="green")
                table.add_column("Yanlış Sayısı (YS)", style="red")
                table.add_column("Ortalama Skor (%)", style="magenta")
                
                for section, data in class_data['sections'].items():
                    soru_bolumu = f"{section}s."
                    ds = data['correct_questions']
                    ys = data['wrong_questions']
                    avg = data['average_score']
                    table.add_row(soru_bolumu, str(ds), str(ys), f"{avg:.2f}%")
                
                # Sınıf Ortalaması ve Okul Ortalaması
                class_avg = class_data['average_score']
                console.print(table)
                console.print(f"Sınıf Ortalaması: [bold green]{class_avg:.2f}%[/bold green]")
            
            # Okul Genel İstatistikleri
            console.print(f"\n[bold underline]Okul Genel İstatistikleri[/bold underline]")
            school_table = Table(show_header=True, header_style="bold blue")
            school_table.add_column("Kategori", style="cyan", no_wrap=True)
            school_table.add_column("Ortalama Skor (%)", style="magenta")
            
            school_avg = school['average_score']
            school_table.add_row("Okul Ortalaması", f"{school_avg:.2f}%")
            
            console.print(school_table)
            break  # Sadece DefaultSchool için işlemleri yaptık

def add_question_panel(user):
    import uuid
    section = user['registered_section']
    if not section:
        print("No registered section.")
        return
    question = input("Enter question text: ")
    q_type = input("Enter question type (single_choice/multiple_choice/true_false/ordering): ").lower()
    if q_type not in ['single_choice', 'multiple_choice', 'true_false', 'ordering']:
        print("Invalid question type.")
        return
    try:
        points = int(input("Enter points for the question: "))
    except ValueError:
        print("Points must be an integer.")
        return
    correct_answer = input("Enter correct answer (for multiple answers, separate by commas): ")
    question_id = str(uuid.uuid4())
    # Save to questions_sectionX.json
    questions_file = f"questions/questions_section{section}.json"
    questions_data = load_json(questions_file)
    new_question = {
        "id": question_id,
        "section": int(section),
        "question": question,
        "points": points,
        "type": q_type
    }
    questions_data['questions'].append(new_question)
    save_json(questions_file, questions_data)
    # Save to answers.json
    answers_data = load_json('answers/answers.json')
    if q_type in ['multiple_choice', 'ordering']:
        answers = [ans.strip() for ans in correct_answer.split(',')]
        answers_data[question_id] = answers
    else:
        answers_data[question_id] = correct_answer.strip()
    save_json('answers/answers.json', answers_data)
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
        if choice == '1':
            add_user_panel(admin_user)
        elif choice == '2':
            update_user_panel(admin_user)
        elif choice == '3':
            delete_user_panel(admin_user)
        elif choice == '4':
            list_users()
        elif choice == '5':
            break
        else:
            print("Invalid choice.\n")

def add_user_panel(admin_user):
    print("\n=== Add User ===")
    username = input("Username: ")
    password = input("Password: ")
    name = input("Name: ")
    surname = input("Surname: ")
    class_name = input("Class (7-a,7-b,7-c,7-d): ")
    role = input("Role (teacher/student): ").lower()
    if role not in ['teacher', 'student']:
        print("Invalid role. Only 'teacher' or 'student' roles are allowed.\n")
        return
    registered_section = None
    if role == 'teacher':
        registered_section = input("Registered Section (1-4): ")
        if registered_section not in ['1', '2', '3', '4']:
            print("Invalid section. Must be between 1 and 4.\n")
            return
    success = add_user(admin_user, username=username, password=password, name=name, surname=surname,
                      class_name=class_name, role=role, registered_section=registered_section)
    if success:
        print("User added successfully.\n")
    else:
        print("Failed to add user.\n")

def update_user_panel(admin_user):
    print("\n=== Update User ===")
    username = input("Enter the username to update: ")
    print("Leave fields blank to keep current values.")
    name = input("New Name: ")
    surname = input("New Surname: ")
    class_name = input("New Class: ")
    role = input("New Role (teacher/student): ").lower()
    if role and role not in ['teacher', 'student']:
        print("Invalid role. Only 'teacher' or 'student' roles are allowed.\n")
        return
    registered_section = None
    if role == 'teacher':
        registered_section = input("Registered Section (1-4): ")
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
    success = update_user(admin_user, username, **update_fields)
    if success:
        print("User updated successfully.\n")
    else:
        print("Failed to update user.\n")

def delete_user_panel(admin_user):
    print("\n=== Delete User ===")
    username = input("Enter the username to delete: ")
    confirm = input(f"Are you sure you want to delete {username}? (y/n): ")
    if confirm.lower() == 'y':
        success = delete_user(admin_user, username)
        if success:
            print(f"User '{username}' deleted successfully.\n")
    else:
        print("Deletion cancelled.\n")

def view_admin_statistics():
    statistics = load_json('users/statistics.json')
    for school in statistics['schools']:
        print(f"\nSchool: {school['school_name']}")
        for class_name, class_data in school['classes'].items():
            print(f"  Class: {class_name}")
            for section, data in class_data['sections'].items():
                print(f"    Section {section} - Correct: {data['correct_questions']}, Wrong: {data['wrong_questions']}, Average Score: {data['average_score']}, Percentage: {data['section_percentage']}%")

if __name__ == "__main__":
    main_menu()
