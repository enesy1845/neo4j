# tests/test_integration.py

import unittest
import sys
import os
from unittest.mock import patch
from io import StringIO

# Ana klasörü path'e ekleyin
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import main

class TestIntegration(unittest.TestCase):

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
    def test_full_exam_flow(self, mock_stdout, mock_input):
        main()
        output = mock_stdout.getvalue()
        self.assertIn('Sınav tamamlandı.', output)
        self.assertIn('Toplam Başarı Yüzdesi:', output)

if __name__ == '__main__':
    unittest.main()
