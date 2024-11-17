# admin.py

import os
import bcrypt
from utils import read_json, write_json, USERS_FILE, get_next_user_id
from user import User
from question import QuestionManager
from utils import clear_screen
from exam import Exam  # Exam sınıfını içe aktardık

def create_initial_admin():
    """Sistemdeki ilk admin hesabını oluşturur ve USERS_FILE dosyasına kaydeder."""
    print("=== İlk Admin Oluşturma ===")
    username = input("İlk admin için kullanıcı adı: ").strip()
    password = input("Şifre: ").strip()
    name = input("Adınız: ").strip()
    surname = input("Soyadınız: ").strip()
    phone_number = input("Telefon Numaranız: ").strip()

    # Şifreyi hashleyelim
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # Yeni admin oluştur
    admin = {
        'user_id': get_next_user_id(),
        'username': username,
        'password': hashed_password,
        'name': name,
        'surname': surname,
        'phone_number': phone_number,
        'role': 'admin',
        'attempts': 0,
        'last_attempt_date': '',
        'score1': None,
        'score2': None,
        'score_avg': None
    }

    # Admini kaydet
    users = []
    if os.path.exists(USERS_FILE):
        users = read_json(USERS_FILE)
    users.append(admin)
    write_json(users, USERS_FILE)
    print(f"İlk admin '{username}' oluşturuldu.")

    # Oluşturulan admin kullanıcısını döndür
    return User(
        user_id=admin['user_id'],
        username=admin['username'],
        password=admin['password'],
        name=admin['name'],
        surname=admin['surname'],
        phone_number=admin['phone_number'],
        role='admin',
        attempts=admin['attempts'],
        last_attempt_date=admin['last_attempt_date'],
        score1=admin['score1'],
        score2=admin['score2'],
        score_avg=admin['score_avg']
    )

def admin_menu(admin_user):
    """Admin kullanıcı menüsü."""
    while True:
        clear_screen()
        print(f"=== Admin Menüsü ({admin_user.name} {admin_user.surname}) ===")
        print("1. Sınavı Çöz")
        print("2. Admin Paneli")
        print("3. Çıkış")
        choice = input("Seçiminiz: ").strip()
        if choice == '1':
            # Sınavı başlat
            exam = Exam(admin_user)
            exam.start_exam()
            input("Devam etmek için Enter tuşuna basın...")
        elif choice == '2':
            # Admin panelini göster
            admin_panel(admin_user)
        elif choice == '3':
            print("Çıkış yapılıyor...")
            break
        else:
            print("Geçersiz seçim.")
            input("Devam etmek için Enter tuşuna basın...")

def admin_panel(admin_user):
    """Admin işlemleri paneli."""
    qm = QuestionManager()
    while True:
        clear_screen()
        print(f"=== Admin Paneli ({admin_user.username}) ===")
        print("1. Soru Ekle")
        print("2. Soru Güncelle")
        print("3. Soru Sil")
        print("4. Soruları Listele")
        print("5. Kullanıcıları Listele")
        print("6. Kullanıcı Sil")
        print("7. Kullanıcı Güncelle")
        print("8. Yeni Admin Oluştur")
        print("9. Geri Dön")
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
            section_number = input("Hangi bölümün sorularını listelemek istiyorsunuz? (1-4, tüm bölümler için 0): ").strip()
            if section_number.isdigit():
                section_number = int(section_number)
                qm.list_questions(section_number)
            else:
                print("Geçersiz bölüm numarası.")
            input("Devam etmek için Enter tuşuna basın...")
        elif choice == '5':
            User.list_users()
            input("Devam etmek için Enter tuşuna basın...")
        elif choice == '6':
            user_id = input("Silinecek Kullanıcı ID: ").strip()
            if user_id.isdigit():
                user_id = int(user_id)
                User.delete_user(user_id)
            else:
                print("Geçersiz kullanıcı ID.")
            input("Devam etmek için Enter tuşuna basın...")
        elif choice == '7':
            user_id = input("Güncellenecek Kullanıcı ID: ").strip()
            if user_id.isdigit():
                user_id = int(user_id)
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
            else:
                print("Geçersiz kullanıcı ID.")
            input("Devam etmek için Enter tuşuna basın...")
        elif choice == '8':
            # Yeni Admin Oluşturma
            create_admin()
            input("Devam etmek için Enter tuşuna basın...")
        elif choice == '9':
            print("Admin menüsüne dönülüyor...")
            break
        else:
            print("Geçersiz seçim.")
            input("Devam etmek için Enter tuşuna basın...")

def create_admin():
    """Yeni bir admin oluşturur, master şifre doğrulaması ile."""
    print("=== Yeni Admin Oluşturma ===")
    # Master şifreyi güvenli bir şekilde yönetmek için aşağıdaki yöntemi kullanın
    master_password = input("Master Şifreyi Giriniz: ").strip()
    # Master şifreyi bir ortam değişkeninden alalım
    correct_master_password = os.environ.get('MASTER_PASSWORD', 'default_master_password')
    if master_password != correct_master_password:
        print("Hatalı master şifre. Yeni admin oluşturma yetkiniz yok.")
        return

    username = input("Kullanıcı Adı: ").strip()
    password = input("Şifre: ").strip()
    name = input("Adınız: ").strip()
    surname = input("Soyadınız: ").strip()
    phone_number = input("Telefon Numaranız: ").strip()

    # Kullanıcı adı kontrolü
    users = []
    if os.path.exists(USERS_FILE):
        users = read_json(USERS_FILE)
        for user in users:
            if user['username'] == username:
                print("Bu kullanıcı adı zaten alınmış. Lütfen başka bir kullanıcı adı seçin.")
                return

    # Şifreyi hashleyelim
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # Yeni admin kullanıcı oluştur
    new_admin = User(
        user_id=get_next_user_id(),
        username=username,
        password=hashed_password,
        name=name,
        surname=surname,
        phone_number=phone_number,
        role='admin',
        attempts=0,
        last_attempt_date='',
        score1=None,
        score2=None,
        score_avg=None
    )

    # Admini kaydet
    new_admin.save_user()
    print(f"Admin '{username}' oluşturuldu.")
