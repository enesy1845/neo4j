# user.py

import os
import bcrypt
from quiznexusai.utils import read_json, write_json, USERS_FILE, get_next_user_id, read_user_answers, write_user_answers,CLASSES_FILE,SCHOOLS_FILE,read_statistics,print_table
import re

# user.py

class User:
    def __init__(self, user_id, username, password, name, surname, phone_number, role='user',
                 attempts=0, last_attempt_date='', score1=None, score2=None, score_avg=None,
                 class_id=None, school_id=None, teacher_sections=None,
                 assigned_school_ids=None, assigned_class_ids=None):
        self.user_id = user_id
        self.username = username
        self.password = password
        self.name = name
        self.surname = surname
        self.phone_number = phone_number
        self.role = role
        self.attempts = attempts
        self.last_attempt_date = last_attempt_date
        self.score1 = score1
        self.score2 = score2
        self.score_avg = score_avg
        self.class_id = class_id
        self.school_id = school_id
        self.teacher_sections = teacher_sections or []
        self.assigned_school_ids = assigned_school_ids or []
        self.assigned_class_ids = assigned_class_ids or []


    def get_user_info(self):
        """
        Collects and validates the user's name, surname, phone number, class, and school.
        """
        try:
            print("Please enter your information to access the exam.\n")
            self.name = input("Your Name: ").strip()
            self.surname = input("Your Surname: ").strip()
            self.phone_number = input("Your Phone Number: ").strip()
            if self.role != 'admin':
                # Select School
                schools = read_json(SCHOOLS_FILE)
                print("\nSelect Your School:")
                for idx, school in enumerate(schools, 1):
                    print(f"{idx}. {school['school_name']}")
                while True:
                    school_choice = input("Enter the number of your school: ").strip()
                    if school_choice.isdigit() and 1 <= int(school_choice) <= len(schools):
                        school_idx = int(school_choice) - 1
                        self.school_id = schools[school_idx]['school_id']
                        break
                    else:
                        print("Invalid choice. Please try again.")

                # Select Class
                classes = [cls for cls in read_json(CLASSES_FILE) if cls['school_id'] == self.school_id]
                print("\nSelect Your Class:")
                for idx, cls in enumerate(classes, 1):
                    print(f"{idx}. {cls['class_name']}")
                while True:
                    class_choice = input("Enter the number of your class: ").strip()
                    if class_choice.isdigit() and 1 <= int(class_choice) <= len(classes):
                        class_idx = int(class_choice) - 1
                        self.class_id = classes[class_idx]['class_id']
                        break
                    else:
                        print("Invalid choice. Please try again.")

            # Load or create a new user
            existing_user = self.load_user()
            if existing_user:
                self.user_id = existing_user['user_id']
                self.attempts = existing_user.get('attempts', 0)
                self.last_attempt_date = existing_user.get('last_attempt_date', '')
                self.score1 = existing_user.get('score1')
                self.score2 = existing_user.get('score2')
                self.score_avg = existing_user.get('score_avg')
                if self.role != 'admin':
                    self.class_id = existing_user.get('class_id')
                    self.school_id = existing_user.get('school_id')
                print(f"Welcome back, {self.name} {self.surname}!")
            else:
                # Create and save a new user
                self.user_id = get_next_user_id()
                self.save_user()
                print(f"Registration successful! Welcome, {self.name} {self.surname}!")
        except Exception as e:
            print(f"An error occurred: {e}")
            input("Press Enter to continue...")
            self.get_user_info()

    def load_user(self):
        """
        Loads user information from the users.json file.
        """
        if not os.path.exists(USERS_FILE):
            return None

        users = read_json(USERS_FILE)
        for user in users:
            if (user['username'] == self.username and
                user['role'] == self.role):
                self.class_id = user.get('class_id')
                self.school_id = user.get('school_id')
                return user
        return None

    def save_user(self):
        """Saves user information to the users.json file."""
        users = []
        if os.path.exists(USERS_FILE):
            users = read_json(USERS_FILE)

        # If user exists, update
        for i, user in enumerate(users):
            if user['user_id'] == self.user_id:
                users[i] = self.to_dict()
                break
        else:
            # Add new user
            users.append(self.to_dict())

        write_json(users, USERS_FILE)

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'username': self.username,
            'password': self.password,
            'name': self.name,
            'surname': self.surname,
            'phone_number': self.phone_number,
            'role': self.role,
            'attempts': self.attempts,
            'last_attempt_date': self.last_attempt_date,
            'score1': self.score1,
            'score2': self.score2,
            'score_avg': self.score_avg,
            'class_id': self.class_id,
            'school_id': self.school_id,
            'teacher_sections': self.teacher_sections,
            'assigned_school_ids': self.assigned_school_ids,
            'assigned_class_ids': self.assigned_class_ids,
        }
    def can_attempt_exam(self):
        """
        Checks if the user has the right to attempt the exam.
        """
        if self.role == 'admin':
            # Admin users can attempt exams unlimited times
            return True
        if self.attempts < 2:
            return True
        else:
            return False

    def increment_attempts(self):
        """
        Increments the number of exam attempts and saves the user.
        """
        self.attempts += 1
        self.save_user()
    

    def view_results(self):
        """Displays the user's exam results, including section-wise class and school averages."""
        print(f"\n=== {self.name} {self.surname} - Exam Results ===")
        if self.score1 is not None:
            print(f"Attempt 1: {self.score1:.2f}% success")
        if self.score2 is not None:
            print(f"Attempt 2: {self.score2:.2f}% success")
        if self.score_avg is not None:
            print(f"Average Success Percentage: {self.score_avg:.2f}%")
        if self.score1 is None and self.score2 is None:
            print("You have not taken any exams yet.")
        
        # Get class and school names
        classes = read_json(CLASSES_FILE)
        schools = read_json(SCHOOLS_FILE)
        user_class = next((cls for cls in classes if cls['class_id'] == self.class_id), {})
        school = next((sch for sch in schools if sch['school_id'] == self.school_id), {})
        class_name = user_class.get('class_name', 'Unknown Class')
        school_name = school.get('school_name', 'Unknown School')

        # Display class and school averages
        statistics = read_statistics()
        class_stats = statistics['classes'].get(self.class_id, {'average_score': 50.0, 'sections': {}})
        school_stats = statistics['schools'].get(self.school_id, {'average_score': 50.0, 'sections': {}})
        class_avg = class_stats['average_score']
        school_avg = school_stats['average_score']
        print(f"\nClass ({class_name}) Average: {class_avg:.2f}%")
        print(f"School ({school_name}) Average: {school_avg:.2f}%")

        # Compare student's average with class and school averages
        if self.score_avg is not None:
            if self.score_avg > class_avg:
                print("You are above the class average.")
            else:
                print("You are below the class average.")
            if self.score_avg > school_avg:
                print("You are above the school average.")
            else:
                print("You are below the school average.")

        # Display section-wise class and school averages
        print("\n=== Section-wise Averages ===")
        for section_number in range(1, 5):  # Assuming 4 sections
            section_name = f"Section {section_number}"
            # Convert section_number to string to match the keys in 'sections' dict
            section_str = str(section_number)
            
            # Class section average
            class_section_stats = class_stats.get('sections', {}).get(section_str, {})
            class_section_avg = class_section_stats.get('average_score', 'N/A')
            
            # School section average
            school_section_stats = school_stats.get('sections', {}).get(section_str, {})
            school_section_avg = school_section_stats.get('average_score', 'N/A')
            
            print(f"{section_name} Averages:")
            if class_section_avg != 'N/A':
                print(f" - Class Average: {class_section_avg:.2f}%")
            else:
                print(" - Class Average: N/A")
            
            if school_section_avg != 'N/A':
                print(f" - School Average: {school_section_avg:.2f}%")
            else:
                print(" - School Average: N/A")

        # Display attempts results in a tabular format
        self.display_attempts_results(class_stats, school_stats)

    def display_attempts_results(self, class_stats, school_stats):
        """Displays the user's exam attempts in a tabular format."""
        print("\n=== Your Exam Attempts ===")
        
        # Read user_answers.json to get the attempts
        user_answers_data = read_user_answers()
        attempts = user_answers_data.get("attempts", [])

        # Filter attempts by current user_id
        user_attempts = [attempt for attempt in attempts if attempt['user_id'] == self.user_id]

        if not user_attempts:
            print("No exam attempts found.")
            return

        # Prepare table headers and rows
        headers = ["Attempt ID", "Start Time", "End Time", "Total Score", "Passed"]
        rows = []
        for attempt in user_attempts:
            attempt_id = attempt.get('attempt_id', 'N/A')
            start_time = attempt.get('start_time', 'N/A')
            end_time = attempt.get('end_time', 'N/A')
            total_score = attempt.get('total_score', 0)
            passed = "Yes" if attempt.get('passed', False) else "No"
            rows.append([attempt_id, start_time, end_time, f"{total_score:.2f}%", passed])

        print_table(headers, rows, title="Your Exam Attempts")

        # Display detailed section-wise scores for each attempt
        for attempt in user_attempts:
            attempt_id = attempt.get('attempt_id', 'N/A')
            sections = attempt.get('sections', {})
            print(f"\n=== Detailed Results for Attempt ID: {attempt_id} ===")
            headers_sec = ["Section", "DS", "YS", "SO", "OO", "Notu", "Ort"]
            rows_sec = []
            for section_num, sec in sections.items():
                section_number = sec.get('section_number', 'N/A')
                correct = sec.get('section_score', 0)
                wrong = sec.get('section_total', 0) - sec.get('section_score', 0)
                
                # SO: Sınıf Ortalaması (Class Average based on DS)
                class_section_avg = class_stats.get('sections', {}).get(str(section_number), {}).get('average_score', 0)
                
                # OO: Okul Ortalaması (School Average based on DS)
                school_section_avg = school_stats.get('sections', {}).get(str(section_number), {}).get('average_score', 0)
                
                # Notu: Sınavdaki elde edilen puan (section_score)
                notu = sec.get('section_score', 0)
                
                # Ort: Ortalama (score_avg)
                ort = attempt.get('score_avg', 0)
                
                rows_sec.append([
                    f"Section {section_number}",
                    str(correct),
                    str(wrong),
                    f"{class_section_avg:.2f}",
                    f"{school_section_avg:.2f}",
                    f"{notu}",
                    f"{ort:.2f}%"
                ])
            print_table(headers_sec, rows_sec, title=f"Attempt ID: {attempt_id} - Section-wise Scores")





    def view_attempts(self):
        """Displays all exam attempts for the user."""
        user_answers_data = read_user_answers()
        attempts = user_answers_data.get("attempts", [])
        user_attempts = [att for att in attempts if att["user_id"] == self.user_id]

        if not user_attempts:
            print("You have no exam attempts yet.")
            return

        for att in user_attempts:
            print(f"\nAttempt ID: {att['attempt_id']}")
            print(f"Name: {att['name']} {att['surname']}")
            print(f"Phone Number: {att['phone_number']}")
            print(f"Class: {att['user_class']}")  # Bu alan sınıf adını içeriyor olmalı
            print(f"School: {att['school']}")      # Bu alan okul adını içeriyor olmalı
            print(f"Start Time: {att['start_time']}")
            print(f"End Time: {att['end_time']}")
            print(f"Total Score: {att['total_score']:.2f}%")
            print(f"Passed: {'Yes' if att['passed'] else 'No'}")
            print("Sections:")
            
            # sections bir sözlük olduğu için .items() ile anahtar-değer çiftlerine erişin
            for section_num, sec in att["sections"].items():
                print(f"  Section {sec['section_number']}: {sec['section_score']}/{sec['section_total']} points")
                for q in sec["questions"]:
                    print(f"    Question ID: {q['question_id']}")
                    print(f"    Text: {q['question_text']}")
                    print(f"    Type: {q['question_type']}")
                    print(f"    Your Answer: {q['user_answer']}")
                    print(f"    Correct Answer: {q['correct_answer']}")
                    print(f"    Correct: {'Yes' if q['is_correct'] else 'No'}")
                    print(f"    Points Earned: {q['points_earned']}")
                    print("-" * 20)


    @staticmethod
    def list_users():
        """Lists all users and displays their scores along with class and school."""
        if not os.path.exists(USERS_FILE):
            print("User list is empty.")
            return
        
        users = read_json(USERS_FILE)
        classes = read_json(CLASSES_FILE) if os.path.exists(CLASSES_FILE) else []
        schools = read_json(SCHOOLS_FILE) if os.path.exists(SCHOOLS_FILE) else []
        
        # Create dictionaries for quick lookup
        classes_dict = {cls['class_id']: cls['class_name'] for cls in classes}
        schools_dict = {sch['school_id']: sch['school_name'] for sch in schools}
        
        print("\n===UserList===")
        for user in users:
            if user.get('role', 'user') == 'user':
                score1 = user.get('score1')
                score2 = user.get('score2')
                score_avg = user.get('score_avg')
                scores_info = ""
                if score1 is not None:
                    scores_info += f"Score1: {score1:.2f}% "
                else:
                    scores_info += "Score1: - "
                if score2 is not None:
                    scores_info += f"Score2: {score2:.2f}% "
                else:
                    scores_info += "Score2: - "
                if score_avg is not None:
                    scores_info += f"Average: {score_avg:.2f}%"
                else:
                    scores_info += "Average: -"
                
                class_name = classes_dict.get(user.get('class_id'), 'Unknown Class')
                school_name = schools_dict.get(user.get('school_id'), 'Unknown School')
                
                print(f"ID: {user['user_id']}, Name: {user['name']} {user['surname']}, "
                    f"Phone: {user['phone_number']}, Class: {class_name}, "
                    f"School: {school_name}, LoginAttempts: {user['attempts']}, {scores_info}")

    @staticmethod
    def delete_user(user_id):
        """Deletes the user with the specified ID."""
        if not os.path.exists(USERS_FILE):
            print("User file not found.")
            return

        users = read_json(USERS_FILE)
        users = [user for user in users if user['user_id'] != user_id]
        write_json(users, USERS_FILE)
        print(f"User ID {user_id} has been deleted.")

    @staticmethod
    def update_user(user_id, updated_data):
        """
        Updates the user with the specified ID.
        """
        if not os.path.exists(USERS_FILE):
            print("User file not found.")
            return

        users = read_json(USERS_FILE)
        for user in users:
            if user['user_id'] == user_id and user.get('role', 'user') == 'user':
                user.update(updated_data)
                write_json(users, USERS_FILE)
                print(f"User ID {user_id} has been updated.")
                return

        print(f"User ID {user_id} not found.")

    @staticmethod
    def register():
        """Creates a new user registration."""
        print("\n=== User Registration ===")
        
        users = []
        if os.path.exists(USERS_FILE):
            users = read_json(USERS_FILE)
        
        while True:
            username = input("Username: ").strip()
            # Username validation code...
            
            # Check for unique username (case-insensitive)
            if any(user['username'].lower() == username.lower() for user in users):
                print("This username is already taken. Please choose another username.")
                continue
            else:
                break  # Username is unique
        
        while True:
            password = input("Password: ").strip()
            confirm_password = input("Confirm Password: ").strip()
            
            if not password:
                print("Password cannot be empty.")
                continue
            
            # Parola uzunluğu kontrolü ekleniyor
            if len(password) < 3:
                print("Password must be at least 3 characters long.")
                continue
            
            if password != confirm_password:
                print("Passwords do not match. Please try again.")
                continue
            break
        
        name = input("Your Name: ").strip()
        surname = input("Your Surname: ").strip()
        phone_number = input("Your Phone Number: ").strip()
        
        # Select School
        schools = read_json(SCHOOLS_FILE)
        print("\nSelect Your School:")
        for idx, school in enumerate(schools, 1):
            print(f"{idx}. {school['school_name']}")
        while True:
            school_choice = input("Enter the number of your school: ").strip()
            if school_choice.isdigit() and 1 <= int(school_choice) <= len(schools):
                school_idx = int(school_choice) - 1
                school_id = schools[school_idx]['school_id']
                break
            else:
                print("Invalid choice. Please try again.")
        
        # Select Class
        classes = [cls for cls in read_json(CLASSES_FILE) if cls['school_id'] == school_id]
        print("\nSelect Your Class:")
        for idx, cls in enumerate(classes, 1):
            print(f"{idx}. {cls['class_name']}")
        while True:
            class_choice = input("Enter the number of your class: ").strip()
            if class_choice.isdigit() and 1 <= int(class_choice) <= len(classes):
                class_idx = int(class_choice) - 1
                class_id = classes[class_idx]['class_id']
                break
            else:
                print("Invalid choice. Please try again.")
        
        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Create new user
        new_user = User(
            user_id=get_next_user_id(),
            username=username,
            password=hashed_password,
            name=name,
            surname=surname,
            phone_number=phone_number,
            role='user',
            class_id=class_id,
            school_id=school_id
        )
        
        # Save the user
        new_user.save_user()
        print(f"Registration successful! Welcome, {name} {surname}!")
        return new_user


    # In user.py, inside the User class
    @staticmethod
    def login():
        """Logs in a user."""
        print("\n=== User Login ===")
        username = input("Username: ").strip()
        password = input("Password: ").strip()

        users = []
        if os.path.exists(USERS_FILE):
            users = read_json(USERS_FILE)
        else:
            print("User database not found.")
            return None

        for user_data in users:
            if user_data['username'] == username:
                # Check the password
                if bcrypt.checkpw(password.encode('utf-8'), user_data['password'].encode('utf-8')):
                    # Create and return the user object
                    return User(
                        user_id=user_data['user_id'],
                        username=user_data['username'],
                        password=user_data['password'],
                        name=user_data['name'],
                        surname=user_data['surname'],
                        phone_number=user_data['phone_number'],
                        role=user_data.get('role', 'user'),
                        attempts=user_data.get('attempts', 0),
                        last_attempt_date=user_data.get('last_attempt_date', ''),
                        score1=user_data.get('score1'),
                        score2=user_data.get('score2'),
                        score_avg=user_data.get('score_avg'),
                        class_id=user_data.get('class_id'),
                        school_id=user_data.get('school_id'),
                        teacher_sections=user_data.get('teacher_sections'),
                        assigned_school_ids=user_data.get('assigned_school_ids', []),
                        assigned_class_ids=user_data.get('assigned_class_ids', []),
                    )
                else:
                    print("Incorrect password.")
                    return None
        print("User not found.")
        return None





