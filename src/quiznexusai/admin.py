# src/admin.py

import os
import bcrypt
from quiznexusai.utils import (
    read_json,
    write_json,
    USERS_FILE,
    get_next_user_id,
    read_user_answers,
    SCHOOLS_FILE,
    CLASSES_FILE,
    clear_screen,
)
from quiznexusai.user import User
from quiznexusai.question import QuestionManager
from quiznexusai.exam import Exam
from quiznexusai.school import SchoolManager
from quiznexusai.class_module import ClassManager
from quiznexusai.statistics_module import StatisticsManager
from quiznexusai.token_generator import renew_token_if_needed, token_generator


class Admin:
    def __init__(self, admin_user):
        self.admin_user = admin_user
        self.question_manager = QuestionManager()
        self.school_manager = SchoolManager()
        self.class_manager = ClassManager()
        self.statistics_manager = StatisticsManager()

    @staticmethod
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
            'score_avg': None,
            'class_id': None,  # Admin does not have class information
            'school_id': None,  # Admin does not have school information
            'teacher_sections': [],
            'assigned_school_ids': [],
            'assigned_class_ids': [],
        }

        # Save admin
        users = []
        if os.path.exists(USERS_FILE):
            users = read_json(USERS_FILE)
            if not isinstance(users, list):
                print(f"Error: {USERS_FILE} is not a list. Resetting to an empty list.")
                users = []
        users.append(admin)
        write_json(users, USERS_FILE)
        print(f"First admin '{username}' has been created.")
        token_generator(admin)

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
            score_avg=admin['score_avg'],
            class_id=admin['class_id'],
            school_id=admin['school_id'],
            teacher_sections=admin['teacher_sections'],
        )

    def admin_menu(self):
        """Admin user menu."""
        while True:
            clear_screen()
            print(f"=== Admin Menu ({self.admin_user.name} {self.admin_user.surname}) ===")
            print("1. Solve Exam")
            print("2. Admin Panel")
            print("3. Exit")
            choice = input("Your choice: ").strip()
            renew_token_if_needed()
            if choice == '1':
                # Start the exam
                exam = Exam(self.admin_user)
                exam.start_exam()
                input("Press Enter to continue...")
                renew_token_if_needed()
            elif choice == '2':
                # Show the admin panel
                self.admin_panel()
            elif choice == '3':
                print("Exiting...")
                break
            else:
                print("Invalid choice.")
                input("Press Enter to continue...")
                renew_token_if_needed()

    def admin_panel(self):
        """Admin operations panel."""
        while True:
            clear_screen()
            print(f"=== Admin Panel ({self.admin_user.username}) ===")
            print("1. Manage Questions")
            print("2. Manage Users")
            print("3. Manage Teachers")
            print("4. Manage Schools")
            print("5. Manage Classes")
            print("6. View Statistics")
            print("7. Logout")
            choice = input("Your choice: ").strip()
            renew_token_if_needed()
            if choice == '1':
                self.manage_questions()
            elif choice == '2':
                self.manage_users()
            elif choice == '3':
                self.manage_teachers()  # New option for managing teachers
            elif choice == '4':
                self.school_manager.manage_schools()
            elif choice == '5':
                self.class_manager.manage_classes()
            elif choice == '6':
                self.statistics_manager.view_admin_statistics()
                input("Press Enter to continue...")
                renew_token_if_needed()
            elif choice == '7':
                print("Logging out...")
                break
            else:
                print("Invalid choice.")
                input("Press Enter to continue...")
                renew_token_if_needed()

    def manage_questions(self):
        """Manage questions."""
        while True:
            clear_screen()
            print("=== Manage Questions ===")
            print("1. Add Question")
            print("2. Update Question")
            print("3. Delete Question")
            print("4. List Questions")
            print("5. Back to Admin Panel")
            choice = input("Your choice: ").strip()
            renew_token_if_needed()
            if choice == '1':
                self.question_manager.add_question()
                input("Press Enter to continue...")
                renew_token_if_needed()
            elif choice == '2':
                self.question_manager.update_question()
                input("Press Enter to continue...")
                renew_token_if_needed()
            elif choice == '3':
                self.question_manager.delete_question()
                input("Press Enter to continue...")
                renew_token_if_needed()
            elif choice == '4':
                self.question_manager.list_all_questions()
                input("Press Enter to continue...")
                renew_token_if_needed()
            elif choice == '5':
                break
            else:
                print("Invalid choice.")
                input("Press Enter to continue...")
                renew_token_if_needed()

    def manage_users(self):
        """Manage users."""
        while True:
            clear_screen()
            print("=== Manage Users ===")
            print("1. List Users")
            print("2. Delete User")
            print("3. Update User")
            print("4. Create New Admin")
            print("5. Update User Role")
            print("6. Back to Admin Panel")
            choice = input("Your choice: ").strip()
            renew_token_if_needed()
            if choice == '1':
                User.list_users()
                input("Press Enter to continue...")
                renew_token_if_needed()
            elif choice == '2':
                user_id = input("Enter the user ID to delete: ").strip()
                renew_token_if_needed()
                User.delete_user(user_id)
                input("Press Enter to continue...")
            elif choice == '3':
                user_id = input("Enter the user ID to update: ").strip()
                renew_token_if_needed()
                User.update_user(user_id)
                input("Press Enter to continue...")
                renew_token_if_needed()
            elif choice == '4':
                self.create_new_admin()
                input("Press Enter to continue...")
                renew_token_if_needed()
            elif choice == '5':
                self.update_user_role()
                input("Press Enter to continue...")
                renew_token_if_needed()
            elif choice == '6':
                break
            else:
                print("Invalid choice.")
                input("Press Enter to continue...")
                renew_token_if_needed()

    def create_new_admin(self):
        """Creates a new admin user."""
        print("=== Create New Admin ===")
        username = input("Username: ").strip()
        renew_token_if_needed()
        password = input("Password: ").strip()
        renew_token_if_needed()
        name = input("Your Name: ").strip()
        renew_token_if_needed()
        surname = input("Your Surname: ").strip()
        renew_token_if_needed()
        phone_number = input("Your Phone Number: ").strip()
        renew_token_if_needed()

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
        new_admin = {
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
            'score_avg': None,
            'class_id': None,
            'school_id': None,
            'teacher_sections': [],
            'assigned_school_ids': [],
            'assigned_class_ids': [],
        }

        # Save the admin
        users.append(new_admin)
        write_json(users, USERS_FILE)
        print(f"Admin '{username}' has been created.")

    def update_user_role(self):
        """Updates the role of a user and assigns sections to teachers."""
        user_id_input = input("User ID to update role: ").strip()
        renew_token_if_needed()
        if not user_id_input:
            print("Invalid user ID.")
            return

        users = read_json(USERS_FILE)
        user = next((u for u in users if u['user_id'] == user_id_input), None)
        if user:
            new_role = input("Enter new role (user/admin/teacher): ").strip().lower()
            renew_token_if_needed()
            if new_role not in ['user', 'admin', 'teacher']:
                print("Invalid role.")
                return
            user['role'] = new_role
            if new_role == 'teacher':
                # Assign sections
                sections_input = input("Assign sections to teacher (e.g., 1,2): ").strip()
                renew_token_if_needed()
                sections = [int(sec.strip()) for sec in sections_input.split(',') if sec.strip().isdigit()]
                user['teacher_sections'] = sections

                # Assign schools
                print("\nAssign Schools to Teacher:")
                schools = read_json(SCHOOLS_FILE)
                for idx, school in enumerate(schools, 1):
                    print(f"{idx}. {school['school_name']}")
                school_choices = input("Enter the numbers of the schools separated by commas: ").strip()
                renew_token_if_needed()
                school_ids = []
                for choice in school_choices.split(','):
                    if choice.strip().isdigit() and 1 <= int(choice.strip()) <= len(schools):
                        school_ids.append(schools[int(choice.strip()) - 1]['school_id'])
                user['assigned_school_ids'] = school_ids

                # Assign classes from selected schools
                print("\nAssign Classes to Teacher:")
                classes = read_json(CLASSES_FILE)
                # Filter classes by selected school_ids
                filtered_classes = [cls for cls in classes if cls['school_id'] in school_ids]
                if not filtered_classes:
                    print("No classes available for the selected schools.")
                else:
                    for idx, cls in enumerate(filtered_classes, 1):
                        school_name = next((sch['school_name'] for sch in schools if sch['school_id'] == cls['school_id']), 'Unknown School')
                        print(f"{idx}. {cls['class_name']} (School: {school_name})")
                    class_choices = input("Enter the numbers of the classes separated by commas: ").strip()
                    renew_token_if_needed()
                    class_ids = []
                    for choice in class_choices.split(','):
                        if choice.strip().isdigit() and 1 <= int(choice.strip()) <= len(filtered_classes):
                            class_ids.append(filtered_classes[int(choice.strip()) - 1]['class_id'])
                    user['assigned_class_ids'] = class_ids
            else:
                user['teacher_sections'] = []
                user['assigned_school_ids'] = []
                user['assigned_class_ids'] = []

            write_json(users, USERS_FILE)
            print(f"User ID {user_id_input} role updated to {new_role}.")
        else:
            print(f"User ID {user_id_input} not found.")


            users = read_json(USERS_FILE)
            user = next((u for u in users if u['user_id'] == user_id_input), None)
            if user:
                new_role = input("Enter new role (user/admin/teacher): ").strip().lower()
                renew_token_if_needed()
                if new_role not in ['user', 'admin', 'teacher']:
                    print("Invalid role.")
                    return
                user['role'] = new_role
                if new_role == 'teacher':
                    # Assign sections
                    sections_input = input("Assign sections to teacher (e.g., 1,2): ").strip()
                    renew_token_if_needed()
                    sections = [int(sec.strip()) for sec in sections_input.split(',') if sec.strip().isdigit()]
                    user['teacher_sections'] = sections

                    # Assign schools
                    print("\nAssign Schools to Teacher:")
                    schools = read_json(SCHOOLS_FILE)
                    for idx, school in enumerate(schools, 1):
                        print(f"{idx}. {school['school_name']}")
                    school_choices = input("Enter the numbers of the schools separated by commas: ").strip()
                    renew_token_if_needed()
                    school_ids = []
                    for choice in school_choices.split(','):
                        if choice.strip().isdigit() and 1 <= int(choice.strip()) <= len(schools):
                            school_ids.append(schools[int(choice.strip()) - 1]['school_id'])
                    user['assigned_school_ids'] = school_ids

                    # Assign classes
                    print("\nAssign Classes to Teacher:")
                    classes = read_json(CLASSES_FILE)
                    for idx, cls in enumerate(classes, 1):
                        school_name = next((sch['school_name'] for sch in schools if sch['school_id'] == cls['school_id']), 'Unknown School')
                        print(f"{idx}. {cls['class_name']} (School: {school_name})")
                    class_choices = input("Enter the numbers of the classes separated by commas: ").strip()
                    renew_token_if_needed()
                    class_ids = []
                    for choice in class_choices.split(','):
                        if choice.strip().isdigit() and 1 <= int(choice.strip()) <= len(classes):
                            class_ids.append(classes[int(choice.strip()) - 1]['class_id'])
                    user['assigned_class_ids'] = class_ids
                else:
                    user['teacher_sections'] = []
                    user['assigned_school_ids'] = []
                    user['assigned_class_ids'] = []

                write_json(users, USERS_FILE)
                print(f"User ID {user_id_input} role updated to {new_role}.")
            else:
                print(f"User ID {user_id_input} not found.")

    def manage_teachers(self):
        """Manage teachers."""
        while True:
            clear_screen()
            print("=== Manage Teachers ===")
            print("1. List Teachers")
            print("2. Create Teacher")
            print("3. Update Teacher")
            print("4. Delete Teacher")
            print("5. Go Back")
            choice = input("Your choice: ").strip()
            renew_token_if_needed()
            if choice == '1':
                self.list_teachers()
                input("Press Enter to continue...")
                renew_token_if_needed()
            elif choice == '2':
                self.create_teacher()
                input("Press Enter to continue...")
                renew_token_if_needed()
            elif choice == '3':
                self.update_teacher()
                input("Press Enter to continue...")
                renew_token_if_needed()
            elif choice == '4':
                self.delete_teacher()
                input("Press Enter to continue...")
                renew_token_if_needed()
            elif choice == '5':
                break
            else:
                print("Invalid choice.")
                input("Press Enter to continue...")
                renew_token_if_needed()

    def list_teachers(self):
        """Lists all teachers."""
        users = read_json(USERS_FILE)
        teachers = [user for user in users if user.get('role') == 'teacher']
        print("\n=== Teacher List ===")
        if not teachers:
            print("No teachers found.")
        else:
            for teacher in teachers:
                sections = ', '.join(map(str, teacher.get('teacher_sections', [])))
                assigned_schools = teacher.get('assigned_school_ids', [])
                assigned_classes = teacher.get('assigned_class_ids', [])
                print(f"ID: {teacher['user_id']}, Name: {teacher['name']} {teacher['surname']}")
                print(f"Sections: {sections}")
                print(f"Assigned Schools: {assigned_schools}")
                print(f"Assigned Classes: {assigned_classes}")
                print("-" * 40)

    def update_teacher(self):
        """Updates a teacher's information."""
        self.list_teachers()
        teacher_id = input("Enter the ID of the teacher you want to update: ").strip()
        renew_token_if_needed()
        users = read_json(USERS_FILE)
        teacher = next((u for u in users if u['user_id'] == teacher_id and u.get('role') == 'teacher'), None)
        if teacher:
            # Update sections
            sections_input = input("Assign sections to teacher (e.g., 1,2), leave blank to keep current: ").strip()
            renew_token_if_needed()
            if sections_input:
                sections = [int(sec.strip()) for sec in sections_input.split(',') if sec.strip().isdigit()]
                teacher['teacher_sections'] = sections
        
            # Update assigned schools
            print("\nAssign Schools to Teacher:")
            schools = read_json(SCHOOLS_FILE)
            for idx, school in enumerate(schools, 1):
                print(f"{idx}. {school['school_name']}")
            school_choices = input("Enter the numbers of the schools separated by commas, leave blank to keep current: ").strip()
            renew_token_if_needed()
            if school_choices:
                school_ids = []
                for choice in school_choices.split(','):
                    if choice.strip().isdigit() and 1 <= int(choice.strip()) <= len(schools):
                        school_ids.append(schools[int(choice.strip()) - 1]['school_id'])
                teacher['assigned_school_ids'] = school_ids
        
            # Update assigned classes
            print("\nAssign Classes to Teacher:")
            classes = read_json(CLASSES_FILE)
            # Filter classes by assigned schools
            assigned_school_ids = teacher.get('assigned_school_ids', [])
            filtered_classes = [cls for cls in classes if cls['school_id'] in assigned_school_ids]
            for idx, cls in enumerate(filtered_classes, 1):
                school_name = next((sch['school_name'] for sch in schools if sch['school_id'] == cls['school_id']), 'Unknown School')
                print(f"{idx}. {cls['class_name']} (School: {school_name})")
            class_choices = input("Enter the numbers of the classes separated by commas, leave blank to keep current: ").strip()
            renew_token_if_needed()
            if class_choices:
                class_ids = []
                for choice in class_choices.split(','):
                    if choice.strip().isdigit() and 1 <= int(choice.strip()) <= len(filtered_classes):
                        class_ids.append(filtered_classes[int(choice.strip()) - 1]['class_id'])
                teacher['assigned_class_ids'] = class_ids
        
            # Save changes
            write_json(users, USERS_FILE)
            print(f"Teacher ID {teacher_id} has been updated.")
        else:
            print(f"Teacher ID {teacher_id} not found.")

    def delete_teacher(self):
        """Deletes a teacher."""
        self.list_teachers()
        teacher_id = input("Enter the ID of the teacher you want to delete: ").strip()
        renew_token_if_needed()
        users = read_json(USERS_FILE)
        teacher = next((u for u in users if u['user_id'] == teacher_id and u.get('role') == 'teacher'), None)
        if teacher:
            confirm = input(f"Are you sure you want to delete teacher '{teacher['name']} {teacher['surname']}'? (yes/no): ").strip().lower()
            renew_token_if_needed()
            if confirm == 'yes':
                users = [u for u in users if u['user_id'] != teacher_id]
                write_json(users, USERS_FILE)
                print(f"Teacher ID {teacher_id} has been deleted.")
            else:
                print("Deletion cancelled.")
        else:
            print(f"Teacher ID {teacher_id} not found.")

    def create_teacher(self):
        """Creates a new teacher."""
        print("=== Create New Teacher ===")
        username = input("Username: ").strip()
        renew_token_if_needed()
        password = input("Password: ").strip()
        renew_token_if_needed()
        name = input("First Name: ").strip()
        renew_token_if_needed()
        surname = input("Last Name: ").strip()
        renew_token_if_needed()
        phone_number = input("Phone Number: ").strip()
        

        # Check if the username is already taken
        users = read_json(USERS_FILE)
        if any(u['username'] == username for u in users):
            print("This username is already taken. Please choose another username.")
            return

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Assign sections
        sections_input = input("Assign sections to teacher (e.g., 1,2): ").strip()
        renew_token_if_needed()
        sections = [int(sec.strip()) for sec in sections_input.split(',') if sec.strip().isdigit()]
        
        # Assign schools
        print("\nAssign Schools to Teacher:")
        schools = read_json(SCHOOLS_FILE)
        for idx, school in enumerate(schools, 1):
            print(f"{idx}. {school['school_name']}")
        school_choices = input("Enter the numbers of the schools separated by commas: ").strip()
        renew_token_if_needed()
        school_ids = []
        for choice in school_choices.split(','):
            if choice.strip().isdigit() and 1 <= int(choice.strip()) <= len(schools):
                school_ids.append(schools[int(choice.strip()) - 1]['school_id'])

        # Assign classes from selected schools
        print("\nAssign Classes to Teacher:")
        classes = read_json(CLASSES_FILE)
        # Filter classes by selected school_ids
        filtered_classes = [cls for cls in classes if cls['school_id'] in school_ids]
        if not filtered_classes:
            print("No classes available for the selected schools.")
            class_ids = []
        else:
            for idx, cls in enumerate(filtered_classes, 1):
                school_name = next((sch['school_name'] for sch in schools if sch['school_id'] == cls['school_id']), 'Unknown School')
                print(f"{idx}. {cls['class_name']} (School: {school_name})")
            class_choices = input("Enter the numbers of the classes separated by commas: ").strip()
            renew_token_if_needed()
            class_ids = []
            for choice in class_choices.split(','):
                if choice.strip().isdigit() and 1 <= int(choice.strip()) <= len(filtered_classes):
                    class_ids.append(filtered_classes[int(choice.strip()) - 1]['class_id'])

        # Create new teacher
        new_teacher = {
            'user_id': get_next_user_id(),
            'username': username,
            'password': hashed_password,
            'name': name,
            'surname': surname,
            'phone_number': phone_number,
            'role': 'teacher',
            'attempts': 0,
            'last_attempt_date': '',
            'score1': None,
            'score2': None,
            'score_avg': None,
            'class_id': None,
            'school_id': None,
            'teacher_sections': sections,
            'assigned_school_ids': school_ids,
            'assigned_class_ids': class_ids,
        }

        # Save the teacher
        users.append(new_teacher)
        write_json(users, USERS_FILE)
        print(f"Teacher '{username}' has been created.")
