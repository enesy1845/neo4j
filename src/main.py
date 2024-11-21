# main.py

import os
from user import User
from exam import Exam
from admin import admin_menu, create_initial_admin
from utils import clear_screen, read_json, USERS_FILE

def main():
    # Check if any admin users exist
    if not os.path.exists(USERS_FILE):
        # If the users file does not exist, create the first admin
        admin_user = create_initial_admin()
        # Redirect to the admin menu with the created admin user
        admin_menu(admin_user)
    else:
        # If the users file exists, check if an admin exists
        users = read_json(USERS_FILE)
        admin_exists = any(user.get('role') == 'admin' for user in users)
        if not admin_exists:
            # If no admin exists, create the first admin
            admin_user = create_initial_admin()
            # Redirect to the admin menu with the created admin user
            admin_menu(admin_user)
        else:
            # If an admin exists, proceed with the normal flow
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
                            admin_menu(user)
                        else:
                            user_menu(user)
                elif choice == '2':
                    user = User.login()
                    if user:
                        if user.role == 'admin':
                            admin_menu(user)
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

def user_menu(user):
    while True:
        clear_screen()
        print(f"=== User Menu ({user.name} {user.surname}) ===")
        print("1. Start Exam")
        print("2. View My Results")
        print("3. Logout")
        choice = input("Your choice: ").strip()

        if choice == '1':
            if not user.can_attempt_exam():
                print("You have no remaining attempts for the exam. Have a nice day!")
                input("Press Enter to continue...")
                continue
            exam = Exam(user)
            exam.start_exam()
            input("\nSınav tamamlandı. Sonuçları gördükten sonra devam etmek için Enter tuşuna basın...")
        elif choice == '2':
            user.view_results()
            input("Press Enter to continue...")
        elif choice == '3':
            print("Logging out...")
            break
        else:
            print("Invalid choice. Please try again.")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()