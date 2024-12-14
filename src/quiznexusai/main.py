# src/main.py

import os
from quiznexusai.user import User
from quiznexusai.exam import Exam
from quiznexusai.admin import Admin
from quiznexusai.teacher import Teacher
from quiznexusai.utils import clear_screen, read_json, USERS_FILE
from quiznexusai.token_generator import token_generator, verify_quiz_token, renew_token_if_needed

def main():
    # Check if any admin users exist
    if not os.path.exists(USERS_FILE) or not admin_exists():
        # If no admin exists, create the first admin
        admin_user = Admin.create_initial_admin()
        admin = Admin(admin_user)
        admin.admin_menu()
    else:
        # Proceed with the normal flow
        while True:
            clear_screen()
            print("=== Multi-Section Timed Exam Application ===\n")
            print("1. Register")
            print("2. Login")
            print("3. Exit")
            choice = input("Your choice (1/2/3): ").strip()

            if choice == '1':
                user = User.register()
                if user:
                    if user.role == 'admin':
                        admin = Admin(user)
                        admin.admin_menu()
                    elif user.role == 'teacher':
                        teacher = Teacher(user)
                        teacher.teacher_menu()
                    else:
                        user_menu(user)
                else:
                    print("Registration failed.")
                    input("Press Enter to continue...")
            elif choice == '2':
                user = User.login()
                if user:
                    token_generator(user.user_id)
                    if user.role == 'admin':
                        admin = Admin(user)
                        admin.admin_menu()
                    elif user.role == 'teacher':
                        teacher = Teacher(user)
                        teacher.teacher_menu()
                    else:
                        user_menu(user)
                else:
                    print("Incorrect username or password. Please try again.")
                    input("Press Enter to continue...")
            elif choice == '3':
                print("Exiting the program...")
                break
            else:
                print("Invalid choice. Please try again.")
                input("Press Enter to continue...")

def admin_exists():
    users = read_json(USERS_FILE)
    return any(user.get('role') == 'admin' for user in users)

def user_menu(user):
    """Normal user menu."""
    while True:
        clear_screen()
        print(f"=== User Menu ({user.name} {user.surname}) ===")
        print("1. Start Exam")
        print("2. View My Results")
        print("3. View My Attempts")
        print("4. Logout")
        choice = input("Your choice: ").strip()
        renew_token_if_needed()
        if choice == '1':
            if not user.can_attempt_exam():
                print("You have no remaining attempts for the exam. Have a nice day!")
                input("Press Enter to continue...")
                continue
            exam = Exam(user)
            exam.start_exam()
            input("\nExam completed. Press Enter to continue...")
            renew_token_if_needed()
        elif choice == '2':
            user.view_results()
            input("Press Enter to continue...")
            renew_token_if_needed()
        elif choice == '3':
            user.view_attempts()
            input("Press Enter to continue...")
            renew_token_if_needed()
        elif choice == '4':
            print("Logging out...")
            break
        else:
            print("Invalid choice. Please try again.")
            input("Press Enter to continue...")
            renew_token_if_needed()

if __name__ == "__main__":
    main()

