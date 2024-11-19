import pytest
from unittest.mock import patch
from io import StringIO
import sys
import os

# src klasörünü path'e ekleyin
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from main import main

@patch('builtins.input', side_effect=[
    '1',           # Giriş Tipi: Kullanıcı Girişi
    'Test',        # Ad
    'User',        # Soyad
    '1234567890',  # Telefon
    # Sınav sırasında soruların cevapları
    '1',           # Soru 1 cevabı
    '1',           # Soru 2 cevabı
    '1,2',         # Soru 3 cevabı
    # ...
])
@patch('sys.stdout', new_callable=StringIO)
def test_full_exam_flow(mock_stdout, mock_input):
    """
    Tüm sınav akışını test eder.
    Beklenen: 'Sınav tamamlandı.' ve 'Toplam Başarı Yüzdesi:' çıktıda yer alır.
    """
    main()
    output = mock_stdout.getvalue()
    assert 'Sınav tamamlandı.' in output
    assert 'Toplam Başarı Yüzdesi:' in output
