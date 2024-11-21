import pytest
import sys
import os


from encryption import encrypt, decrypt

def test_encrypt_decrypt():
    """
    Şifrelenen metnin başarıyla geri çözümlenip aynı metni verdiğini test eder.
    """
    original_text = 'Bu bir test mesajıdır. Türkçe karakterler içerir: ğüşiöç'
    encrypted_text = encrypt(original_text)
    decrypted_text = decrypt(encrypted_text)
    assert original_text == decrypted_text

def test_encrypt_different_outputs():
    """
    Farklı metinlerin şifrelenmiş çıktılarının birbirinden farklı olduğunu test eder.
    """
    text1 = 'Mesaj 1'
    text2 = 'Mesaj 2'
    encrypted1 = encrypt(text1)
    encrypted2 = encrypt(text2)
    assert encrypted1 != encrypted2

# Daha fazla test fonksiyonu ekleyebilirsiniz.
