# tests/test_question.py

import unittest
import sys
import os

# Ana klasörü path'e ekleyin
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from question import QuestionManager
from utils import write_json, read_json

class TestQuestionManager(unittest.TestCase):

    def setUp(self):
        self.qm = QuestionManager()
        self.qm.question_types = {
            'true_false': 'test_true_false_questions.json',
            'single_choice': 'test_single_choice_questions.json',
            'multiple_choice': 'test_multiple_choice_questions.json'
        }

        # Boş soru dosyaları oluştur
        write_json([], 'data/questions/test_true_false_questions.json')
        write_json([], 'data/questions/test_single_choice_questions.json')
        write_json([], 'data/questions/test_multiple_choice_questions.json')
        write_json({}, 'data/answers/answers.json')

    def tearDown(self):
        # Test dosyalarını sil
        os.remove('data/questions/test_true_false_questions.json')
        os.remove('data/questions/test_single_choice_questions.json')
        os.remove('data/questions/test_multiple_choice_questions.json')
        os.remove('data/answers/answers.json')

    def test_add_question(self):
        # add_question metodunu test etmek için girdi alımını mock edebiliriz
        with unittest.mock.patch('builtins.input', side_effect=[
            'true_false',  # Soru tipi
            '1',           # Bölüm numarası
            'Test Soru',   # Soru metni
            '5',           # Puan
            'Doğru'        # Doğru cevap
        ]):
            self.qm.add_question()
            questions = read_json('data/questions/test_true_false_questions.json')
            self.assertEqual(len(questions), 1)
            self.assertEqual(questions[0]['question'], 'Test Soru')

    # Diğer test metotlarını ekleyebilirsiniz

if __name__ == '__main__':
    unittest.main()
