import unittest
import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from result import Result
from user import User
from utils import write_json

class TestResult(unittest.TestCase):

    def setUp(self):
        # Create a test user
        self.user = User()
        self.user.user_id = 1
        self.user.name = 'Test'
        self.user.surname = 'User'
        self.user.phone_number = '1234567890'
        self.user.attempts = 0
        self.user.scores = []

        # Prepare user answers and correct answers
        self.user_answers = {'1': 'Doğru'}
        write_json({'1': 'Doğru'}, 'data/answers/answers.json')

        # Create question information
        write_json([
            {
                'id': 1,
                'section': 1,
                'question': 'Test Doğru/Yanlış Soru',
                'points': 5,
                'type': 'true_false'
            }
        ], 'data/questions/true_false_questions.json')

        # Initialize parameters for Result
        self.used_question_ids = ['1']
        self.total_sections = 1

    def tearDown(self):
        # Remove test files
        os.remove('data/answers/answers.json')
        os.remove('data/questions/true_false_questions.json')

    def test_calculate_results(self):
        # Initialize Result object with required parameters
        result = Result(
            user=self.user,
            user_answers=self.user_answers,
            used_question_ids=self.used_question_ids,
            total_sections=self.total_sections
        )
        # Calculate results and assert values
        result.calculate_results()
        self.assertEqual(result.total_score, 100.0)
        self.assertTrue(result.passed)

if __name__ == '__main__':
    unittest.main()
