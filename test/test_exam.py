# tests/test_exam.py

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Önce src klasörünü sys.path'e ekleyin
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

# Importları sys.path güncellendikten sonra yapın
from exam import Exam
from user import User
from result import Result  # Result sınıfını içe aktardık

class TestExam(unittest.TestCase):
    """
    Exam sınıfını test eden birim testleri.
    """

    def setUp(self):
        """
        Testler başlamadan önce gerekli test verilerini oluşturur.
        """
        self.user = User(
            user_id=1,
            username='test_user',
            password='hashed_password',
            name='Test',
            surname='User',
            phone_number='1234567890',
            role='user',
            attempts=0,
            last_attempt_date='',
            score1=None,
            score2=None,
            score_avg=None
        )
        # Diğer setUp işlemleri...

    def tearDown(self):
        """
        Testler tamamlandıktan sonra gerekli temizleme işlemlerini yapar.
        """
        pass

    @patch.object(Result, 'load_all_questions', return_value={
        '1': {
            'id': 1,
            'section': 1,
            'question': 'Bu bir Doğru/Yanlış sorusudur.',
            'type': 'true_false',
            'points': 5
        }
    })
    @patch.object(Result, 'check_answer', return_value=True)
    @patch.object(Result, 'calculate_results')  # calculate_results metodunu mockladık
    def test_end_exam_successful(self, mock_calculate, mock_check_answer, mock_load_questions):
        """
        Sınavın başarılı bir şekilde sonlandırıldığını ve sonuçların hesaplandığını test eder.
        Beklenen Sonuç: calculate_results metodunun çağrılması.
        """
        exam = Exam(self.user)
        exam.answers = {'1': 'Doğru'}
        exam.used_question_ids = {1}
        exam.sections = 1

        exam.end_exam()
        mock_calculate.assert_called_once()

    # Diğer test metotlarınızı benzer şekilde düzenleyin...

if __name__ == '__main__':
    unittest.main(verbosity=2)
