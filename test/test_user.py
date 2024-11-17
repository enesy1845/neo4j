# tests/test_user.py

import unittest
import os
import sys

# src klasörü path'e ekleyin
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from user import User
from utils import write_json, read_json

USERS_FILE = 'data/users/users.json'

class TestUser(unittest.TestCase):

    def setUp(self):
        # Test kullanıcı verisini oluştur
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
        write_json([self.test_user_data], USERS_FILE)
        print(f"Test user data written to {USERS_FILE}")

    def tearDown(self):
        # Test sırasında oluşturulan dosyayı sil
        if os.path.exists(USERS_FILE):
            os.remove(USERS_FILE)
            print(f"Test user data removed from {USERS_FILE}")

    def test_load_user(self):
        user = User()
        user.name = 'Test'
        user.surname = 'User'
        user.phone_number = '1234567890'
        loaded_user = user.load_user()
        self.assertIsNotNone(loaded_user)
        self.assertEqual(loaded_user['user_id'], 999)
        self.assertEqual(loaded_user['attempts'], 1)
        self.assertEqual(loaded_user['role'], 'user')

    def test_can_attempt_exam(self):
        user = User()
        user.attempts = 1
        self.assertTrue(user.can_attempt_exam())
        user.attempts = 2
        self.assertFalse(user.can_attempt_exam())
        print(f"User can attempt the exam: {user.can_attempt_exam()}")

    def test_increment_attempts(self):
        user = User()
        user.user_id = 999
        user.attempts = 1
        user.save_user()
        user.increment_attempts()
        updated_user = user.load_user()
        self.assertEqual(updated_user['attempts'], 2)
        print(f"User attempts incremented to {updated_user['attempts']}")

if __name__ == '__main__':
    unittest.main()
