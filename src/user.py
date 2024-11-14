# user.py

import os
from utils import read_json, write_json, get_next_user_id

USERS_FILE = 'data/users/users.json'

class User:
    def __init__(self):
        """
        User sınıfı, sınava katılacak kullanıcıların bilgilerini yönetir.
        """
        self.user_id = None
        self.name = ''
        self.surname = ''
        self.phone_number = ''
        self.attempts = 0
        self.last_attempt_date = ''
        self.scores = []
        self.role = 'user'  # Rol özelliği eklendi

    def get_user_info(self):
        """
        Kullanıcıdan isim, soyisim ve telefon numarası alır ve doğrular.

        Kullanıcı bilgileri mevcut değilse yeni kullanıcı kaydı yapılır.
        """
        try:
            print("Lütfen sınava giriş için bilgilerinizi giriniz.\n")
            self.name = input("Adınız: ").strip()
            self.surname = input("Soyadınız: ").strip()
            self.phone_number = input("Telefon Numaranız: ").strip()

            # Kullanıcıyı yükle veya yeni kullanıcı oluştur
            existing_user = self.load_user()
            if existing_user:
                self.user_id = existing_user['user_id']
                self.attempts = existing_user['attempts']
                self.last_attempt_date = existing_user['last_attempt_date']
                self.scores = existing_user.get('scores', [])
                print(f"Hoş geldiniz, {self.name} {self.surname}!")
            else:
                # Yeni kullanıcı oluştur ve kaydet
                self.user_id = get_next_user_id()
                self.save_user()
                print(f"Kayıt başarılı! Hoş geldiniz, {self.name} {self.surname}!")
        except Exception as e:
            print(f"Hata oluştu: {e}")
            input("Devam etmek için Enter tuşuna basın...")
            self.get_user_info()

    def load_user(self):
        """
        Kullanıcı bilgilerini users.json dosyasından yükler.

        Returns:
            dict or None: Kullanıcı bilgileri, bulunamazsa None.
        """
        if not os.path.exists(USERS_FILE):
            return None

        users = read_json(USERS_FILE)
        for user in users:
            if (user['name'].lower() == self.name.lower() and
                user['surname'].lower() == self.surname.lower() and
                user['phone_number'] == self.phone_number and
                user.get('role', 'user') == 'user'):
                return user
        return None

    def save_user(self):
        """
        Kullanıcı bilgilerini users.json dosyasına kaydeder.
        """
        users = []
        if os.path.exists(USERS_FILE):
            users = read_json(USERS_FILE)

        # Kullanıcı zaten varsa güncelle
        for i, user in enumerate(users):
            if user['user_id'] == self.user_id:
                users[i] = self.to_dict()
                break
        else:
            # Yeni kullanıcı ekle
            users.append(self.to_dict())

        write_json(users, USERS_FILE)

    def can_attempt_exam(self):
        """
        Kullanıcının sınava girme hakkı olup olmadığını kontrol eder.

        Returns:
            bool: Kullanıcının sınava girebilme hakkı varsa True, değilse False.
        """
        return self.attempts < 2

    def increment_attempts(self):
        """
        Sınav giriş sayısını bir artırır ve kaydeder.
        """
        self.attempts += 1
        self.save_user()

    def to_dict(self):
        """
        Kullanıcı nesnesini sözlük formatına dönüştürür.

        Returns:
            dict: Kullanıcı bilgilerini içeren sözlük.
        """
        return {
            'user_id': self.user_id,
            'name': self.name,
            'surname': self.surname,
            'phone_number': self.phone_number,
            'attempts': self.attempts,
            'last_attempt_date': self.last_attempt_date,
            'scores': self.scores,
            'role': self.role  # Rol bilgisi eklendi
        }

    # CRUD İşlemleri

    @staticmethod
    def list_users():
        """
        Tüm kullanıcıları listeler ve ekrana yazdırır.
        """
        if not os.path.exists(USERS_FILE):
            print("Kullanıcı listesi boş.")
            return

        users = read_json(USERS_FILE)
        print("\n=== Kullanıcı Listesi ===")
        for user in users:
            if user.get('role', 'user') == 'user':
                print(f"ID: {user['user_id']}, İsim: {user['name']} {user['surname']}, Telefon: {user['phone_number']}, Giriş Sayısı: {user['attempts']}")

    @staticmethod
    def delete_user(user_id):
        """
        Belirtilen ID'ye sahip kullanıcıyı siler.

        Args:
            user_id (int): Silinecek kullanıcı ID'si.
        """
        if not os.path.exists(USERS_FILE):
            print("Kullanıcı dosyası bulunamadı.")
            return

        users = read_json(USERS_FILE)
        users = [user for user in users if user['user_id'] != user_id]
        write_json(users, USERS_FILE)
        print(f"Kullanıcı ID {user_id} silindi.")

    @staticmethod
    def update_user(user_id, updated_data):
        """
        Belirtilen ID'ye sahip kullanıcıyı günceller.

        Args:
            user_id (int): Güncellenecek kullanıcı ID'si.
            updated_data (dict): Güncellenecek veri.
        """
        if not os.path.exists(USERS_FILE):
            print("Kullanıcı dosyası bulunamadı.")
            return

        users = read_json(USERS_FILE)
        for user in users:
            if user['user_id'] == user_id and user.get('role', 'user') == 'user':
                user.update(updated_data)
                write_json(users, USERS_FILE)
                print(f"Kullanıcı ID {user_id} güncellendi.")
                return

        print(f"Kullanıcı ID {user_id} bulunamadı.")
