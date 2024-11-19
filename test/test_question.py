import os
import sys
import pytest

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from question import QuestionManager
from utils import write_json, read_json


@pytest.fixture
def setup_test_environment():
    """
    Test ortamını hazırlayan bir pytest fixture.
    """
    qm = QuestionManager()
    qm.question_types = {
        'true_false': 'test_true_false_questions.json',
        'single_choice': 'test_single_choice_questions.json',
        'multiple_choice': 'test_multiple_choice_questions.json'
    }

    # Boş soru dosyaları oluştur
    write_json([], 'data/questions/test_true_false_questions.json')
    write_json([], 'data/questions/test_single_choice_questions.json')
    write_json([], 'data/questions/test_multiple_choice_questions.json')
    write_json({}, 'data/answers/answers.json')

    yield qm  # Test için gereken nesneyi döndür

    # Testler bittikten sonra dosyaları sil
    os.remove('data/questions/test_true_false_questions.json')
    os.remove('data/questions/test_single_choice_questions.json')
    os.remove('data/questions/test_multiple_choice_questions.json')
    os.remove('data/answers/answers.json')



def test_add_question(monkeypatch, setup_test_environment):   #####burada bir key error veriyor def(add_question)
    """
    add_question metodunu test eder.
    """
    qm = setup_test_environment

    # Kullanıcı girdilerini monkeypatch ile taklit edin
    input_values = {
        "Soru tipi (true_false, single_choice, multiple_choice): ": "true_false",
        "Bölüm numarası (1-4): ": "1",
        "Soru metni: ": "Test Soru",
        "Soru puanı: ": "5",
        "Doğru cevap(lar) (birden fazla ise virgülle ayırın): ": "Doğru"
    }

    def mock_input(prompt):
        # Girdi alınan her mesaj için simüle edilen bir cevap döndür
        return input_values[prompt]

    monkeypatch.setattr('builtins.input', mock_input)

    # Metodu çağır
    qm.add_question()

    # Sonuçları doğrula
    questions = read_json('data/questions/test_true_false_questions.json')
    assert len(questions) == 1
    assert questions[0]['question'] == "Test Soru"
    assert questions[0]['points'] == 5


