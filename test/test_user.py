import unittest
import os
import sys

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from user import User
from utils import write_json, read_json

USERS_FILE = 'data/users/users.json'

class TestUser(unittest.TestCase):

    def setUp(self):
        # Create test user data
        self.test_user_data = {
            'user_id': 999,
            'name': 'Test',
            'surname': 'User',
            'phone_number': '1234567890',
            'attempts': 1,
            'last_attempt_date': '',
            'scores': [],
            'role': 'user'
        }
        # Ensure the data directory exists
        os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
        # Write test user data to USERS_FILE
        write_json([self.test_user_data], USERS_FILE)

    def tearDown(self):
        # Remove USERS_FILE after each test
        if os.path.exists(USERS_FILE):
            os.remove(USERS_FILE)

    def test_load_user(self):
        # Initialize a User instance with matching attributes
        user = User()
        user.name = 'Test'
        user.surname = 'User'
        user.phone_number = '1234567890'
        # Attempt to load user data
        loaded_user = user.load_user()
        # Verify that the user data is loaded correctly
        self.assertIsNotNone(loaded_user)
        self.assertEqual(loaded_user['user_id'], 999)
        self.assertEqual(loaded_user['attempts'], 1)
        self.assertEqual(loaded_user['role'], 'user')

    def test_can_attempt_exam(self):
        # Initialize a User instance and set the number of attempts
        user = User()
        user.attempts = 1
        # Check if the user can attempt the exam
        self.assertTrue(user.can_attempt_exam())
        # Update the attempts to exceed the limit and recheck
        user.attempts = 2
        self.assertFalse(user.can_attempt_exam())

    def test_increment_attempts(self):
        # Initialize a User instance and set user_id and attempts
        user = User()
        user.user_id = 999
        user.name = 'Test'
        user.surname = 'User'
        user.phone_number = '1234567890'
        user.attempts = 1
        # Save the initial state to file
        user.save_user()
        # Increment the attempts and save the result
        user.increment_attempts()
        # Reload the user data to verify changes
        updated_user = user.load_user()
        self.assertEqual(updated_user['attempts'], 2)

if __name__ == '__main__':
    unittest.main()
