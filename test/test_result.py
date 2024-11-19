import pytest
import os
from result import Result
from user import User
from utils import write_json

@pytest.fixture
def prepare_test_environment():
    """
    Test ortamını hazırlar: Kullanıcıyı, cevapları ve soruları oluşturur.
    Test sonunda dosyaları temizler.
    """
    # Test kullanıcıyı oluştur
    user = User()
    user.user_id = 1
    user.name = 'Test'
    user.surname = 'User'
    user.phone_number = '1234567890'
    user.attempts = 0
    user.scores = []

    # Kullanıcı cevaplarını ve doğru cevapları oluştur
    user_answers = {'1': 'Doğru'}
    write_json({'1': 'Doğru'}, 'data/answers/answers.json')

    # Soru bilgilerini oluştur
    write_json([{
        'id': 1,
        'section': 1,
        'question': 'Test Doğru/Yanlış Soru',
        'points': 5,
        'type': 'true_false'
    }], 'data/questions/true_false_questions.json')

    # Gerekli parametreleri döndür
    yield {
        'user': user,
        'user_answers': user_answers,
        'used_question_ids': ['1'],
        'total_sections': 1
    }

    # Test dosyalarını sil
    os.remove('data/answers/answers.json')
    os.remove('data/questions/true_false_questions.json')

def test_calculate_results(prepare_test_environment):
    """
    Sonuçların doğru bir şekilde hesaplandığını test eder.
    """
    env = prepare_test_environment
    result = Result(
        user=env['user'],
        user_answers=env['user_answers'],
        used_question_ids=env['used_question_ids'],
        total_sections=env['total_sections']
    )

    # Sonuçları hesapla ve kontrol et
    result.calculate_results()
    assert result.total_score == 100.0
    assert result.passed
