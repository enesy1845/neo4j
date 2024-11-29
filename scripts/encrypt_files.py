import os
from quiznexusai.utils import read_json, write_json

def encrypt_file(file_path):
    if os.path.exists(file_path):
        data = read_json(file_path, encrypted=False)  # Şifresiz oku
        write_json(data, file_path, encrypted=True)    # Şifreli olarak yaz
        print(f"Encrypted {file_path}")
    else:
        print(f"File {file_path} does not exist.")

# Şifrelemek istediğiniz tüm dosyaların yollarını belirtin
files_to_encrypt = [
    'data/schools/schools.json',
    'data/classes/classes.json',
]

for file_path in files_to_encrypt:
    encrypt_file(file_path)
