# setup_admin.py

import os
import bcrypt
from utils import read_json, write_json

ADMINS_FILE = 'data/admins/admins.json'

def create_initial_admin():
    """
    Sistemdeki ilk admin hesabını oluşturur ve `ADMINS_FILE` dosyasına kaydeder.

    Admin dosyası zaten mevcutsa yeni bir admin oluşturulmaz. Eğer dosya yoksa veya boşsa,
    kullanıcının giriş bilgilerini alarak bir admin hesabı oluşturur ve güvenli bir şekilde
    hashlenmiş şifre ile birlikte `ADMINS_FILE` dosyasına kaydeder.

    İşleyiş:
        - Admin dosyası için gerekli dizin kontrol edilir ve yoksa oluşturulur.
        - Kullanıcıdan admin bilgileri (kullanıcı adı, şifre, ad, soyad, telefon) istenir.
        - Şifre `bcrypt` modülü kullanılarak hashlenir ve güvenli bir şekilde dosyaya yazılır.
    
    Not:
        Şifreler `bcrypt` ile hashlenmiş olarak saklanır, bu sayede şifrelerin güvenliği artırılır.
        Bu işlev yalnızca sistemin başlangıcında çalıştırılır ve ilk admin oluşturulduktan sonra
        yeniden çalıştırılmamalıdır.

    Attributes:
        admin_dir (str): Admin dosyasının bulunduğu dizin.
        admins (list): Adminlerin bulunduğu liste, yeni admin bu listeye eklenir.

    Raises:
        IOError: Admin dosyası okuma/yazma sırasında bir hata oluşursa.

    """
    admin_dir = os.path.dirname(ADMINS_FILE)
    if not os.path.exists(admin_dir):
        os.makedirs(admin_dir)

    admins = []
    if os.path.exists(ADMINS_FILE):
        admins = read_json(ADMINS_FILE)
        if admins:
            print("Admin dosyası zaten mevcut.")
            return

    username = input("İlk admin için kullanıcı adı: ").strip()
    password = input("Şifre: ").strip()
    name = input("Adınız: ").strip()
    surname = input("Soyadınız: ").strip()
    phone_number = input("Telefon Numaranız: ").strip()

    # Şifreyi hashleyelim
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    admin = {
        'admin_id': 1,
        'username': username,
        'password': hashed_password.decode('utf-8'),
        'name': name,
        'surname': surname,
        'phone_number': phone_number,
        'role': 'admin'
    }

    # Admini kaydet
    admins.append(admin)
    write_json(admins, ADMINS_FILE)
    print(f"İlk admin '{username}' oluşturuldu.")

if __name__ == "__main__":
    create_initial_admin()
