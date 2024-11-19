import sys
import os
import pytest
from unittest.mock import patch, MagicMock
from exam import Exam
from user import User
from result import Result  # Result sınıfını içe aktardık

# Fixture ile Ortak Test Verisi Sağlama
@pytest.fixture
def test_user():
    """
    Testlerde kullanılacak kullanıcı nesnesi.
    """
    return User(
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

@pytest.fixture
def exam_instance(test_user):
    """
    Testlerde kullanılacak Exam örneği.
    """
    return Exam(test_user)

# Test Fonksiyonu
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
def test_end_exam_successful(mock_calculate, mock_check_answer, mock_load_questions, exam_instance):
    """
    Sınavın başarılı bir şekilde sonlandırıldığını ve sonuçların hesaplandığını test eder.
    Beklenen Sonuç: calculate_results metodunun çağrılması.
    """
    exam_instance.answers = {'1': 'Doğru'}
    exam_instance.used_question_ids = {1}
    exam_instance.sections = 1

    exam_instance.end_exam()
    mock_calculate.assert_called_once()

# Diğer testlerinizi benzer şekilde dönüştürebilirsiniz.
