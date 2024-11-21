import pytest
from unittest.mock import patch, MagicMock
from io import StringIO
from main import main
from admin import admin_menu
from user import User

# === MAIN TESTLERİ === BURAYA AYRICA REGISTER ICIN DA BIR TEST EKLENEBİLİR.
@patch('builtins.input', side_effect=['3'])  # Programdan çıkış
@patch('sys.stdout', new_callable=StringIO)
def test_main_exit_flow(mock_stdout, mock_input):
    """
    main() içinde kullanıcı '3' seçerse çıkışı test eder.
    Beklenen: "Exiting the program..." çıktıda yer alır.
    """
    main()
    output = mock_stdout.getvalue()
    assert "Exiting the program..." in output


@patch('builtins.input', side_effect=['2', 'Admin', 'User', '1234567890', '3'])
@patch('sys.stdout', new_callable=StringIO)
def test_login_and_exit(mock_stdout, mock_input):
    """
    main() içinde kayıt ve ardından çıkış akışını test eder.
    """
    main()
    output = mock_stdout.getvalue()
    assert "Exiting the program..." in output



