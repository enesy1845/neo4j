# admin.py

import os
import bcrypt
from user import User
from utils import read_json, write_json, clear_screen

ADMINS_FILE = 'data/admins/admins.json'

class Admin:
    def __init__(self):
        self.admin_id = None
        self.username = ''
        self.password = ''
        self.name = ''
        self.surname = ''
        self.phone_number = ''
        self.role = 'admin'

    def get_admin_info(self):
        """Admin bilgilerini alır ve doğrular."""
        try:
            print("Lütfen admin girişi için bilgilerinizi giriniz.\n")
            self.username = input("Kullanıcı Adı: ").strip()
            password_input = input("Şifre: ").strip()
            
            # Admini yükle ve doğrula
            existing_admin = self.load_admin()
            if existing_admin:
                self.admin_id = existing_admin['admin_id']
                self.name = existing_admin['name']
                self.surname = existing_admin['surname']
                self.phone_number = existing_admin['phone_number']
                stored_password = existing_admin['password']  # Hashlenmiş şifre

                # Şifreyi doğrula
                if bcrypt.checkpw(password_input.encode('utf-8'), stored_password.encode('utf-8')):
                    print(f"Hoş geldiniz, Admin {self.name} {self.surname}!")
                else:
                    print("Hatalı şifre. Giriş başarısız.")
                    exit()
            else:
                print("Admin bulunamadı. Giriş başarısız.")
                exit()
        except Exception as e:
            print(f"Hata oluştu: {e}")
            input("Devam etmek için Enter tuşuna basın...")
            self.get_admin_info()

    def load_admin(self):
        """Admin bilgilerini admins.json dosyasından yükler."""
        if not os.path.exists(ADMINS_FILE):
            return None
        admins = read_json(ADMINS_FILE)
        for admin in admins:
            if admin['username'] == self.username:
                return admin
        return None

    def save_admin(self):
        """Admin bilgilerini admins.json dosyasına kaydeder."""
        admins = []
        if os.path.exists(ADMINS_FILE):
            admins = read_json(ADMINS_FILE)
        # Admin zaten varsa güncelle
        for i, admin in enumerate(admins):
            if admin['admin_id'] == self.admin_id:
                admins[i] = self.to_dict()
                break
        else:
            # Yeni admin ekle
            admins.append(self.to_dict())
        write_json(admins, ADMINS_FILE)

    def get_next_admin_id(self):
        """Adminler için otomatik ID üretir."""
        if not os.path.exists(ADMINS_FILE):
            return 1
        admins = read_json(ADMINS_FILE)
        admin_ids = [admin['admin_id'] for admin in admins]
        if not admin_ids:
            return 1
        return max(admin_ids) + 1

    def to_dict(self):
        """Admin nesnesini sözlük formatına dönüştürür."""
        return {
            'admin_id': self.admin_id,
            'username': self.username,
            'password': self.password,
            'name': self.name,
            'surname': self.surname,
            'phone_number': self.phone_number,
            'role': self.role
        }

    def admin_menu(self):
        """Admin işlemleri menüsü."""
        from question import QuestionManager
        qm = QuestionManager()
        while True:
            clear_screen()
            print("=== Admin Paneli ===")
            print("1. Soru Ekle")
            print("2. Soru Güncelle")
            print("3. Soru Sil")
            print("4. Soruları Listele")
            print("5. Kullanıcıları Listele")
            print("6. Kullanıcı Sil")
            print("7. Kullanıcı Güncelle")
            print("8. Yeni Admin Oluştur")
            print("9. Çıkış")
            choice = input("Seçiminiz: ").strip()
            if choice == '1':
                qm.add_question()
                input("Devam etmek için Enter tuşuna basın...")
            elif choice == '2':
                question_id = int(input("Güncellenecek Soru ID: ").strip())
                qm.update_question(question_id)
                input("Devam etmek için Enter tuşuna basın...")
            elif choice == '3':
                question_id = int(input("Silinecek Soru ID: ").strip())
                qm.delete_question(question_id)
                input("Devam etmek için Enter tuşuna basın...")
            elif choice == '4':
                question_type = input("Soru Tipi (true_false, single_choice, multiple_choice): ").strip()
                qm.list_questions(question_type)
                input("Devam etmek için Enter tuşuna basın...")
            elif choice == '5':
                User.list_users()
                input("Devam etmek için Enter tuşuna basın...")
            elif choice == '6':
                user_id = int(input("Silinecek Kullanıcı ID: ").strip())
                User.delete_user(user_id)
                input("Devam etmek için Enter tuşuna basın...")
            elif choice == '7':
                user_id = int(input("Güncellenecek Kullanıcı ID: ").strip())
                updated_data = {}
                new_name = input("Yeni Adı (boş bırakılırsa aynı kalır): ").strip()
                if new_name:
                    updated_data['name'] = new_name
                new_surname = input("Yeni Soyadı (boş bırakılırsa aynı kalır): ").strip()
                if new_surname:
                    updated_data['surname'] = new_surname
                new_phone = input("Yeni Telefon Numarası (boş bırakılırsa aynı kalır): ").strip()
                if new_phone:
                    updated_data['phone_number'] = new_phone
                User.update_user(user_id, updated_data)
                input("Devam etmek için Enter tuşuna basın...")
            elif choice == '8':
                # Yeni Admin Oluşturma
                self.create_admin()
                input("Devam etmek için Enter tuşuna basın...")
            elif choice == '9':
                print("Çıkış yapılıyor...")
                break
            else:
                print("Geçersiz seçim.")
                input("Devam etmek için Enter tuşuna basın...")

    def create_admin(self):
        """Yeni bir admin oluşturur, master şifre doğrulaması ile."""
        print("=== Yeni Admin Oluşturma ===")
        master_password = input("Master Şifreyi Giriniz: ").strip()
        if master_password != '123':
            print("Hatalı master şifre. Yeni admin oluşturma yetkiniz yok.")
            return

        username = input("Kullanıcı Adı: ").strip()
        password = input("Şifre: ").strip()
        name = input("Adınız: ").strip()
        surname = input("Soyadınız: ").strip()
        phone_number = input("Telefon Numaranız: ").strip()

        # Şifreyi hashleyelim
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Yeni admin nesnesi oluştur
        new_admin = Admin()
        new_admin.admin_id = new_admin.get_next_admin_id()
        new_admin.username = username
        new_admin.password = hashed_password.decode('utf-8')
        new_admin.name = name
        new_admin.surname = surname
        new_admin.phone_number = phone_number

        # Admini kaydet
        new_admin.save_admin()
        print(f"Admin '{username}' oluşturuldu.")
