# main.py

import os
from user import User
from exam import Exam
<<<<<<< HEAD
from admin import admin_menu, create_initial_admin
from utils import clear_screen, read_json, USERS_FILE

def main():
    # Admin kullanıcılarının var olup olmadığını kontrol edin
    if not os.path.exists(USERS_FILE):
        # Kullanıcılar dosyası yoksa, ilk admini oluştur
        admin_user = create_initial_admin()
        # Oluşturulan admin kullanıcıyla admin menüsüne yönlendir
        admin_menu(admin_user)
    else:
        # Kullanıcılar dosyası varsa, içinde admin var mı kontrol et
        users = read_json(USERS_FILE)
        admin_exists = any(user.get('role') == 'admin' for user in users)
        if not admin_exists:
            # Admin yoksa, ilk admini oluştur
            admin_user = create_initial_admin()
            # Oluşturulan admin kullanıcıyla admin menüsüne yönlendir
            admin_menu(admin_user)
        else:
            # Admin varsa, normal akışa devam et
            while True:
                clear_screen()
                print("=== Çok Bölümlü Zaman Sınırlı Sınav Uygulaması ===\n")
                print("1. Kayıt Ol")
                print("2. Giriş Yap")
                print("3. Çıkış")
                choice = input("Seçiminiz (1/2/3): ").strip()

                if choice == '1':
                    user = User.register()
                    if user:
                        if user.role == 'admin':
                            admin_menu(user)
                        else:
                            user_menu(user)
                elif choice == '2':
                    user = User.login()
                    if user:
                        if user.role == 'admin':
                            admin_menu(user)
                        else:
                            user_menu(user)
                    else:
                        print("Hatalı kullanıcı adı veya şifre. Lütfen tekrar deneyin.")
                        input("Devam etmek için Enter tuşuna basın...")
                elif choice == '3':
                    print("Programdan çıkılıyor...")
                    break
                else:
                    print("Geçersiz seçim. Lütfen tekrar deneyin.")
                    input("Devam etmek için Enter tuşuna basın...")

def user_menu(user):
    while True:
        clear_screen()
        print(f"=== Kullanıcı Menüsü ({user.name} {user.surname}) ===")
        print("1. Sınava Başla")
        print("2. Sonuçlarımı Görüntüle")
        print("3. Çıkış Yap")
        choice = input("Seçiminiz: ").strip()

        if choice == '1':
            if not user.can_attempt_exam():
                print("Sınava giriş hakkınız kalmamıştır. İyi günler!")
                input("Devam etmek için Enter tuşuna basın...")
                continue
=======
from utils import clear_screen
from inputhandler import InputHandler

def main():
    clear_screen()
    print("=== Çok Bölümlü Zaman Sınırlı Sınav Uygulaması ===\n")
    
    # Giriş tipi seçimi
    print("Giriş tipini seçiniz:")
    print("1. Kullanıcı Girişi")
    print("2. Admin Girişi")
    allowed_characters = '12'
    input_handler = InputHandler(allowed_characters)
    choice = input_handler.get_input()
    
    if choice == '1':
        # Kullanıcı girişi ve kontrolü
        user = User()
        user.get_user_info()
        
        if not user.can_attempt_exam():
            print("Sınava giriş hakkınız kalmamıştır. İyi günler!")
            return
        
        # Sınavı başlat
        try:
>>>>>>> Bilal
            exam = Exam(user)
            exam.start_exam()
        elif choice == '2':
            user.view_results()
            input("Devam etmek için Enter'a basın...")
        elif choice == '3':
            print("Çıkış yapılıyor...")
            break
        else:
            print("Geçersiz seçim. Lütfen tekrar deneyin.")
            input("Devam etmek için Enter tuşuna basın...")

if __name__ == "__main__":
    main()
