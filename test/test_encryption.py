# tests/test_encryption.py

import unittest
import sys
import os

# src klasörü path'e ekleyin
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from encryption import encrypt, decrypt

class TestEncryption(unittest.TestCase):

    def test_encrypt_decrypt(self):
        original_text = 'Bu bir test mesajıdır. Türkçe karakterler içerir: şğüşiöç'
        encrypted_text = encrypt(original_text)
        decrypted_text = decrypt(encrypted_text)
        self.assertEqual(original_text, decrypted_text)

    def test_encrypt_different_outputs(self):
        text1 = 'Mesaj 1'
        text2 = 'Mesaj 2'
        encrypted1 = encrypt(text1)
        encrypted2 = encrypt(text2)
        self.assertNotEqual(encrypted1, encrypted2)

    # Diğer test metotlarını ekleyebilirsiniz

if __name__ == '__main__':
    unittest.main()
