# main.py

from user import User
from admin import Admin
from exam import Exam
from utils import clear_screen

from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')
DEBUG = os.getenv('DEBUG')

def main():
    clear_screen()
    print("=== Çok Bölümlü Zaman Sınırlı Sınav Uygulaması ===\n")
    
    # Giriş tipi seçimi
    print("Giriş tipini seçiniz:")
    print("1. Kullanıcı Girişi")
    print("2. Admin Girişi")
    choice = input("Seçiminiz (1/2): ").strip()
    
    if choice == '1':
        # Kullanıcı girişi ve kontrolü
        user = User()
        user.get_user_info()
        
        if not user.can_attempt_exam():
            print("Sınava giriş hakkınız kalmamıştır. İyi günler!")
            return
        
        # Sınavı başlat
        try:
            exam = Exam(user)
            exam.start_exam()
        except Exception as e:
            print(f"Beklenmeyen bir hata oluştu: {e}")
            input("Programdan çıkmak için Enter tuşuna basın...")
    elif choice == '2':
        # Admin girişi
        admin = Admin()
        admin.get_admin_info()
        admin.admin_menu()
    else:
        print("Geçersiz seçim. Program sonlandırılıyor.")
        return

if __name__ == "__main__":
    main()
