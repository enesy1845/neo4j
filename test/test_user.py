import pytest
import os
from user import User
from utils import write_json, read_json

USERS_FILE = 'data/users/users.json'

@pytest.fixture
def setup_user_data():
    """
    Test kullanıcı verilerini hazırlar ve test sonunda temizler.
    """
    # Test kullanıcı verisi
    test_user_data = {
        'user_id': 999,
        'name': 'Test',
        'surname': 'User',
        'phone_number': '1234567890',
        'attempts': 1,
        'last_attempt_date': '',
        'scores': [],
        'role': 'user'
    }
    # Kullanıcı verisini dosyaya yaz
    os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
    write_json([test_user_data], USERS_FILE)

    yield test_user_data

    # Test dosyasını sil
    if os.path.exists(USERS_FILE):
        os.remove(USERS_FILE)

def test_load_user(setup_user_data):
    """
    Kullanıcı verilerinin doğru şekilde yüklendiğini test eder.
    """
    user = User()
    user.name = 'Test'
    user.surname = 'User'
    user.phone_number = '1234567890'
    
    loaded_user = user.load_user()
    assert loaded_user is not None
    assert loaded_user['user_id'] == 999
    assert loaded_user['attempts'] == 1
    assert loaded_user['role'] == 'user'

def test_can_attempt_exam():
    """
    Kullanıcının sınav yapıp yapamayacağını test eder.
    """
    user = User()
    user.attempts = 1
    assert user.can_attempt_exam() is True

    user.attempts = 2
    assert user.can_attempt_exam() is False

def test_increment_attempts(setup_user_data):
    """
    Kullanıcının sınav deneme sayısının artırılmasını test eder.
    """
    user = User()
    user.user_id = 999
    user.name = 'Test'
    user.surname = 'User'
    user.phone_number = '1234567890'
    user.attempts = 1

    user.save_user()
    user.increment_attempts()
    
    updated_user = user.load_user()
    assert updated_user['attempts'] == 2
