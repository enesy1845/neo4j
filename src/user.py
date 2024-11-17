# user.py


"""
Modules required for user management functions.

Modules:
    - os: Used to perform file and directory operations. This module is used
      to check the existence of the `USERS_FILE` and manage file path operations.
      
    - utils (read_json, write_json, get_next_user_id):
        - read_json: Used to load data by reading a JSON file.
          Retrieves user data from the `users.json` file.
          
        - write_json: Used to write data to a JSON file.
          Utilized when creating, updating, and deleting users in the `users.json` file.
          
        - get_next_user_id: Generates a unique ID for a new user.
          This function determines the next ID based on existing user IDs,
          ensuring that each user is assigned a unique identifier.
"""
import os
import bcrypt
from utils import read_json, write_json, get_next_user_id

USERS_FILE = 'data/users/users.json'

class User:
    def __init__(
        self,
        user_id,
        username,
        password,
        name,
        surname,
        phone_number,
        role='user',
        attempts=0,
        last_attempt_date='',
        score1=None,
        score2=None,
        score_avg=None
    ):
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
         

    def get_user_info(self):
        """
        Collects and validates the user's name, surname, and phone number.

        If user information does not exist, a new user registration is performed.
        """
        try:
            print("Please enter your information to access the exam.\n")
            self.name = input("Your Name: ").strip()
            self.surname = input("Your Surname: ").strip()
            self.phone_number = input("Your Phone Number: ").strip()

            # Load or create a new user
            existing_user = self.load_user()
            if existing_user:
                self.user_id = existing_user['user_id']
                self.attempts = existing_user['attempts']
                self.last_attempt_date = existing_user['last_attempt_date']
                self.score1 = existing_user.get('score1')
                self.score2 = existing_user.get('score2')
                self.score_avg = existing_user.get('score_avg')
                print(f"Welcome, {self.name} {self.surname}!")
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

        Returns:
            dict or None: User information if found, otherwise None.
        """
        if not os.path.exists(USERS_FILE):
            return None

        users = read_json(USERS_FILE)
        for user in users:
            if (user['name'].lower() == self.name.lower() and
                user['surname'].lower() == self.surname.lower() and
                user['phone_number'] == self.phone_number and
                user.get('role', 'user') == 'user'):
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
        """Converts the user object to a dictionary format."""
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
            'score_avg': self.score_avg
        }

    def can_attempt_exam(self):
        """
        Checks if the user has the right to attempt the exam.

        Returns:
            bool: True if the user can attempt the exam, False otherwise.
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
        """Displays the user's exam results."""
        print(f"\n=== {self.name} {self.surname} - Exam Results ===")
        if self.score1 is not None:
            print(f"Attempt 1: {self.score1:.2f}% success")
        if self.score2 is not None:
            print(f"Attempt 2: {self.score2:.2f}% success")
        if self.score_avg is not None:
            print(f"Average Success Percentage: {self.score_avg:.2f}%")
        if self.score1 is None and self.score2 is None:
            print("You have not taken any exams yet.")

    """
    @staticmethod Decorator

    The @staticmethod decorator allows functions defined within a class to be called
    without needing an instance of the class. A static method is neither bound to the class itself (`cls`)
    nor to any instance of the class (`self`). This means that it can operate independently
    of the class's attributes and methods.

    Features:
        - Static methods can be called directly on the class: `ClassName.method_name()`.
        - Static methods do not require access to the class instance or class variables,
          and thus, can function as general-purpose utility functions.

    Use Cases:
        Static methods are suitable for operations that are related to the class but do not need
        access to any class or instance-specific data. For example, general helper functions,
        simple data processing, or calculations that are independent of the class's state.

    Example Scenarios:
        - Data validation or formatting functions that do not depend on class attributes.
        - General-purpose helper functions that operate on inputs without needing class context.

    If Not Used:
        If a method is not defined as @staticmethod, it operates as an instance method and
        requires access to the instance (`self`). Consequently, it cannot be called directly on the
        class and must be accessed through an instance. For example, the `list_users` function
        without @staticmethod cannot be called as `User.list_users()`; instead, a `User` instance
        must be created, and the method called on that instance.
    
    Summary:
        The @staticmethod decorator enables the creation of methods that belong to the class's
        namespace but do not operate on class or instance data, allowing them to function as
        independent utility functions.
    """

    @staticmethod
    def list_users():
        """Lists all users and displays their scores."""
        if not os.path.exists(USERS_FILE):
            print("User list is empty.")
            return

        users = read_json(USERS_FILE)
        print("\n=== User List ===")
        for user in users:
            if user.get('role', 'user') == 'user':
                score1 = user.get('score1')
                score2 = user.get('score2')
                score_avg = user.get('score_avg')
                scores_info = ""
                if score1 is not None:
                    scores_info += f"Score 1: {score1:.2f}% "
                else:
                    scores_info += "Score 1: - "
                if score2 is not None:
                    scores_info += f"Score 2: {score2:.2f}% "
                else:
                    scores_info += "Score 2: - "
                if score_avg is not None:
                    scores_info += f"Average: {score_avg:.2f}%"
                else:
                    scores_info += "Average: -"
                print(f"ID: {user['user_id']}, Name: {user['name']} {user['surname']}, Phone: {user['phone_number']}, Login Attempts: {user['attempts']}, {scores_info}")


    @staticmethod
    def delete_user(user_id):
        """Deletes the user with the specified ID."""
        if not os.path.exists(USERS_FILE):
            print("User file not found.")
            return

        users = read_json(USERS_FILE)
        users = [user for user in users if user['user_id'] != user_id]
        """
        # A new list is defined
        filtered_users = []

        # Start a loop through the existing users list
        for user in users:
        # If user_id is not equal to 2, add the user to the filtered_users list
            if user['user_id'] != 2:
                filtered_users.append(user)

        # The filtered_users list is updated with the original users list
        users = filtered_users
        """
        write_json(users, USERS_FILE)
        print(f"User ID {user_id} has been deleted.")

    @staticmethod
    def update_user(user_id, updated_data):
        """
        Updates the user with the specified ID.

        Args:
            user_id (int): The ID of the user to update.
            updated_data (dict): The data to update.
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
                    return None

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Create a new user
        new_user = User(
            user_id=get_next_user_id(),
            username=username,
            password=hashed_password,
            name=name,
            surname=surname,
            phone_number=phone_number,
            role='user'
        )

        # Save the user
        new_user.save_user()
        print(f"Registration successful! Welcome, {name} {surname}!")
        return new_user

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
                        score_avg=user_data.get('score_avg')
                    )
                else:
                    print("Incorrect password.")
                    return None
        print("User not found.")
        return None
