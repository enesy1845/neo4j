# tests/test_result.py

import unittest
import sys
import os

# src klasörü path'e ekleyin
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from result import Result
from user import User
from utils import write_json

class TestResult(unittest.TestCase):

    def setUp(self):
        # Test kullanıcı oluştur
        self.user = User()
        self.user.user_id = 1
        self.user.name = 'Test'
        self.user.surname = 'User'
        self.user.phone_number = '1234567890'
        self.user.attempts = 0
        self.user.scores = []

        # Kullanıcı cevaplarını ve doğru cevapları hazırlayalım
        self.user_answers = {'1': 'Doğru'}
        write_json({'1': 'Doğru'}, 'data/answers/answers.json')

        # Soru bilgilerini oluştur
        write_json([{
            'id': 1,
            'section': 1,
            'question': 'Test Doğru/Yanlış Soru',
            'points': 5,
            'type': 'true_false'
        }], 'data/questions/true_false_questions.json')

    def tearDown(self):
        # Test dosyalarını sil
        os.remove('data/answers/answers.json')
        os.remove('data/questions/true_false_questions.json')

    def test_calculate_results(self):
        result = Result(self.user, self.user_answers)
        result.calculate_results()
        self.assertEqual(result.total_score, 100.0)
        self.assertTrue(result.passed)

    # Diğer test metotlarını ekleyebilirsiniz

if __name__ == '__main__':
    unittest.main()
