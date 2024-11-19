# admin.py

import os
import bcrypt
from utils import read_json, write_json, USERS_FILE, get_next_user_id
from user import User
from question import QuestionManager
from utils import clear_screen
from exam import Exam  # Imported the Exam class

def create_initial_admin():
    """Creates the first admin account in the system and saves it to the USERS_FILE."""
    print("=== Creating First Admin ===")
    username = input("Username for the first admin: ").strip()
    password = input("Password: ").strip()
    name = input("Your Name: ").strip()
    surname = input("Your Surname: ").strip()
    phone_number = input("Your Phone Number: ").strip()

    # Hash the password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # Create new admin
    admin = {
        'user_id': get_next_user_id(),
        'username': username,
        'password': hashed_password,
        'name': name,
        'surname': surname,
        'phone_number': phone_number,
        'role': 'admin',
        'attempts': 0,
        'last_attempt_date': '',
        'score1': None,
        'score2': None,
        'score_avg': None
    }

    # Save admin
    users = []
    if os.path.exists(USERS_FILE):
        users = read_json(USERS_FILE)
    users.append(admin)
    write_json(users, USERS_FILE)
    print(f"First admin '{username}' has been created.")

    # Return the created admin user
    return User(
        user_id=admin['user_id'],
        username=admin['username'],
        password=admin['password'],
        name=admin['name'],
        surname=admin['surname'],
        phone_number=admin['phone_number'],
        role='admin',
        attempts=admin['attempts'],
        last_attempt_date=admin['last_attempt_date'],
        score1=admin['score1'],
        score2=admin['score2'],
        score_avg=admin['score_avg']
    )

def admin_menu(admin_user):
    """Admin user menu."""
    while True:
        clear_screen()
        print(f"=== Admin Menu ({admin_user.name} {admin_user.surname}) ===")
        print("1. Solve Exam")
        print("2. Admin Panel")
        print("3. Exit")
        choice = input("Your choice: ").strip()
        if choice == '1':
            # Start the exam
            exam = Exam(admin_user)
            exam.start_exam()
            input("Press Enter to continue...")
        elif choice == '2':
            # Show the admin panel
            admin_panel(admin_user)
        elif choice == '3':
            print("Exiting...")
            break
        else:
            print("Invalid choice.")
            input("Press Enter to continue...")

def admin_panel(admin_user):
    """Admin operations panel."""
    qm = QuestionManager()
    while True:
        clear_screen()
        print(f"=== Admin Panel ({admin_user.username}) ===")
        print("1. Add Question")
        print("2. Update Question")
        print("3. Delete Question")
        print("4. List Questions")
        print("5. List Users")
        print("6. Delete User")
        print("7. Update User")
        print("8. Create New Admin")
        print("9. Go Back")
        choice = input("Your choice: ").strip()
        if choice == '1':
            qm.add_question()
            input("Press Enter to continue...")
        elif choice == '2':
            question_id = int(input("Question ID to update: ").strip())
            qm.update_question(question_id)
            input("Press Enter to continue...")
        elif choice == '3':
            question_id = int(input("Question ID to delete: ").strip())
            qm.delete_question(question_id)
            input("Press Enter to continue...")
        elif choice == '4':
            section_number = input("Which section's questions do you want to list? (1-4, all sections for 0): ").strip()
            if section_number.isdigit():
                section_number = int(section_number)
                qm.list_questions(section_number)
            else:
                print("Invalid section number.")
            input("Press Enter to continue...")
        elif choice == '5':
            User.list_users()
            input("Press Enter to continue...")
        elif choice == '6':
            user_id = input("User ID to delete: ").strip()
            if user_id.isdigit():
                user_id = int(user_id)
                User.delete_user(user_id)
            else:
                print("Invalid user ID.")
            input("Press Enter to continue...")
        elif choice == '7':
            user_id = input("User ID to update: ").strip()
            if user_id.isdigit():
                user_id = int(user_id)
                updated_data = {}
                new_name = input("New Name (leave blank to keep the same): ").strip()
                if new_name:
                    updated_data['name'] = new_name
                new_surname = input("New Surname (leave blank to keep the same): ").strip()
                if new_surname:
                    updated_data['surname'] = new_surname
                new_phone = input("New Phone Number (leave blank to keep the same): ").strip()
                if new_phone:
                    updated_data['phone_number'] = new_phone
                User.update_user(user_id, updated_data)
            else:
                print("Invalid user ID.")
            input("Press Enter to continue...")
        elif choice == '8':
            # Create new admin
            create_admin()
            input("Press Enter to continue...")
        elif choice == '9':
            print("Returning to admin menu...")
            break
        else:
            print("Invalid choice.")
            input("Press Enter to continue...")

def create_admin():
    """Creates a new admin, with master password verification."""
    print("=== Create New Admin ===")
    # Use the following method to securely manage the master password
    master_password = input("Enter Master Password: ").strip()
    # Retrieve the master password from an environment variable
    correct_master_password = os.environ.get('MASTER_PASSWORD', 'default_master_password')
    if master_password != correct_master_password:
        print("Incorrect master password. You do not have permission to create a new admin.")
        return

    username = input("Username: ").strip()
    password = input("Password: ").strip()
    name = input("Your Name: ").strip()
    surname = input("Your Surname: ").strip()
    phone_number = input("Your Phone Number: ").strip()

    # Check if the username is already taken
    users = []
    if os.path.exists(USERS_FILE):
        users = read_json(USERS_FILE)
        for user in users:
            if user['username'] == username:
                print("This username is already taken. Please choose another username.")
                return

    # Hash the password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # Create new admin user
    new_admin = User(
        user_id=get_next_user_id(),
        username=username,
        password=hashed_password,
        name=name,
        surname=surname,
        phone_number=phone_number,
        role='admin',
        attempts=0,
        last_attempt_date='',
        score1=None,
        score2=None,
        score_avg=None
    )

    # Save the admin
    new_admin.save_user()
    print(f"Admin '{username}' has been created.")
