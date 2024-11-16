# tests/test_exam.py

import unittest
import sys
import os
from unittest.mock import patch



sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from exam import Exam
from user import User
from question import QuestionManager
from utils import write_json

class TestExam(unittest.TestCase):

    def setUp(self):
        # Test kullanıcı oluştur
        self.user = User()
        self.user.user_id = 1
        self.user.name = 'Test'
        self.user.surname = 'User'
        self.user.phone_number = '1234567890'
        self.user.attempts = 0
        self.user.scores = []

        # Soruları hazırlamak için QuestionManager'ı kullanabiliriz
        self.qm = QuestionManager()
        # Örnek soruları ekleyelim
        self.qm.question_types = {
            'true_false': 'test_true_false_questions.json',
            'single_choice': 'test_single_choice_questions.json',
            'multiple_choice': 'test_multiple_choice_questions.json'
        }

        # Test sorularını ve cevapları dosyalara yazalım
        write_json([{
            'id': 1,
            'section': 1,
            'question': 'Test Doğru/Yanlış Soru',
            'points': 5
        }], 'data/questions/test_true_false_questions.json')

        write_json([{
            'id': 1000,
            'section': 2,
            'question': 'Test Tek Seçimli Soru',
            'options': ['Seçenek A', 'Seçenek B'],
            'points': 5
        }], 'data/questions/test_single_choice_questions.json')

        write_json([{
            'id': 2000,
            'section': 3,
            'question': 'Test Çok Seçimli Soru',
            'options': ['Seçenek 1', 'Seçenek 2', 'Seçenek 3'],
            'points': 5
        }], 'data/questions/test_multiple_choice_questions.json')

        write_json({
            '1': 'Doğru',
            '1000': 'Seçenek A',
            '2000': ['Seçenek 1', 'Seçenek 2']
        }, 'data/answers/answers.json')

    def tearDown(self):
        # Test dosyalarını sil
        os.remove('data/questions/test_true_false_questions.json')
        os.remove('data/questions/test_single_choice_questions.json')
        os.remove('data/questions/test_multiple_choice_questions.json')
        os.remove('data/answers/answers.json')

    def test_exam_initialization(self):
        exam = Exam(self.user)
        self.assertEqual(exam.user.name, 'Test')
        self.assertEqual(exam.duration, 180)

    # Diğer test metotlarını ekleyebilirsiniz

if __name__ == '__main__':
    unittest.main()
