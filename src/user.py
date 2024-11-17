# user.py


"""
Kullanıcı yönetimi işlevleri için gerekli modüller.

Modüller:
    - os: Dosya ve dizin işlemlerini gerçekleştirmek için kullanılır. Bu modül,
      `USERS_FILE` dosyasının varlığını kontrol etmek ve dosya yolu işlemlerini
      yönetmek için kullanılır.
      
    - utils (read_json, write_json, get_next_user_id):
        - read_json: JSON dosyasını okuyarak veriyi yüklemek için kullanılır. 
          Kullanıcı verilerini `users.json` dosyasından alır.
          
        - write_json: JSON dosyasına veri yazmak için kullanılır. Yeni kullanıcı
          oluşturma, güncelleme ve silme işlemlerinde `users.json` dosyasına
          veri yazarken kullanılır.
          
        - get_next_user_id: Yeni bir kullanıcı için benzersiz ID oluşturur. Bu işlev,
          mevcut kullanıcı ID'lerine göre bir sonraki ID'yi belirler, böylece
          her kullanıcıya özgün bir kimlik atanır.
"""
import os
import bcrypt
from utils import read_json, write_json, get_next_user_id

USERS_FILE = 'data/users/users.json'

class User:
    def __init__(
        self,
        user_id,
        username,
        password,
        name,
        surname,
        phone_number,
        role='user',
        attempts=0,
        last_attempt_date='',
        score1=None,
        score2=None,
        score_avg=None
    ):
        self.user_id = user_id
        self.username = username
        self.password = password
        self.name = name
        self.surname = surname
        self.phone_number = phone_number
        self.role = role
        self.attempts = attempts
        self.last_attempt_date = last_attempt_date
        self.score1 = score1
        self.score2 = score2
        self.score_avg = score_avg
         

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
                self.score1 = existing_user.get('score1')
                self.score2 = existing_user.get('score2')
                self.score_avg = existing_user.get('score_avg')
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
        """Kullanıcı bilgilerini users.json dosyasına kaydeder."""
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

    def to_dict(self):
        """Kullanıcı nesnesini sözlük formatına dönüştürür."""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'password': self.password,
            'name': self.name,
            'surname': self.surname,
            'phone_number': self.phone_number,
            'role': self.role,
            'attempts': self.attempts,
            'last_attempt_date': self.last_attempt_date,
            'score1': self.score1,
            'score2': self.score2,
            'score_avg': self.score_avg
        }

    def can_attempt_exam(self):
        """
        Kullanıcının sınava girme hakkı olup olmadığını kontrol eder.

        Returns:
            bool: Kullanıcının sınava girebilme hakkı varsa True, değilse False.
        """
        if self.role == 'admin':
            # Admin kullanıcıları sınava sınırsız girebilir
            return True
        if self.attempts < 2:
            return True
        else:
            return False

    def increment_attempts(self):
        """
        Sınav giriş sayısını bir artırır ve kaydeder.
        """
        self.attempts += 1
        self.save_user()



    def view_results(self):
        """Kullanıcının sınav sonuçlarını görüntüler."""
        print(f"\n=== {self.name} {self.surname} - Sınav Sonuçları ===")
        if self.score1 is not None:
            print(f"Deneme 1: {self.score1:.2f}% başarı")
        if self.score2 is not None:
            print(f"Deneme 2: {self.score2:.2f}% başarı")
        if self.score_avg is not None:
            print(f"Ortalama Başarı Yüzdesi: {self.score_avg:.2f}%")
        if self.score1 is None and self.score2 is None:
            print("Henüz bir sınava girmediniz.")

    """
    @staticmethod Dekoratörü

    @staticmethod dekoratörü, bir sınıfın metodu olarak tanımlanan işlevlerin sınıf
    örneğine (nesnesine) ihtiyaç duymadan çağrılabilmesini sağlar. Bir statik metod,
    ne sınıfın kendisine (`cls`), ne de sınıf örneğine (`self`) bağlıdır. Bu sayede,
    sınıfa ait bağımsız bir işlev olarak çalışabilir.

    Özellikler:
        - Statik metotlar, sınıf üzerinden doğrudan çağrılabilir: `ClassName.method_name()`.
        - Statik metotların, sınıfın örneğine veya özelliklerine erişmesi gerekmez, 
        yalnızca sınıfın genel bir işlevi olarak çalışır.

    Kullanım Alanları:
        Statik metotlar, belirli bir sınıfla ilişkili ancak sınıf örneğine ihtiyaç
        duymayan işlemleri gerçekleştirmek için uygundur. Örneğin, genel yardımcı
        işlevler, basit veri işleme veya sınıfın belirli bir durumundan bağımsız olan
        hesaplama ve kontrol işlemleri için statik metotlar tercih edilir.

    Örnek Senaryolar:
        - Veri doğrulama veya formatlama işlemleri gibi sınıfa bağlı olmayan işlevler.
        - Sınıfın örnekleri arasında bağımsız çalışan genel yardımcı işlevler.

    Kullanılmaması Durumunda:
        Eğer bir metot, @staticmethod olarak tanımlanmazsa, sınıfın örneğine (`self`)
        bağlı olarak çalışır. Bu durumda, işlevin sınıf üzerinden doğrudan çağrılması 
        mümkün olmaz ve yalnızca bir nesne üzerinden çağrılabilir hale gelir. Örneğin,
        `list_users` işlevi @staticmethod olmadan `User.list_users()` şeklinde
        çağrılamaz; bunun yerine önce bir `User` nesnesi oluşturulmalı ve `instance.list_users()` 
        şeklinde erişilmelidir.

    Özet:
        @staticmethod dekoratörü, bir sınıfın işlevselliğiyle ilgili genel işlemleri
        sınıf örneğine ihtiyaç duymadan gerçekleştirebilmeyi sağlar. Bu sayede işlev,
        yalnızca sınıfa ait bağımsız bir yardımcı işlev olarak tanımlanır.
    """

    @staticmethod
    def list_users():
        """Tüm kullanıcıları listeler ve skorlarını gösterir."""
        if not os.path.exists(USERS_FILE):
            print("Kullanıcı listesi boş.")
            return

        users = read_json(USERS_FILE)
        print("\n=== Kullanıcı Listesi ===")
        for user in users:
            if user.get('role', 'user') == 'user':
                score1 = user.get('score1')
                score2 = user.get('score2')
                score_avg = user.get('score_avg')
                scores_info = ""
                if score1 is not None:
                    scores_info += f"Skor 1: {score1:.2f}% "
                else:
                    scores_info += "Skor 1: - "
                if score2 is not None:
                    scores_info += f"Skor 2: {score2:.2f}% "
                else:
                    scores_info += "Skor 2: - "
                if score_avg is not None:
                    scores_info += f"Ortalama: {score_avg:.2f}%"
                else:
                    scores_info += "Ortalama: -"
                print(f"ID: {user['user_id']}, İsim: {user['name']} {user['surname']}, Telefon: {user['phone_number']}, Giriş Sayısı: {user['attempts']}, {scores_info}")


    @staticmethod
    def delete_user(user_id):
        """Belirtilen ID'ye sahip kullanıcıyı siler."""
        if not os.path.exists(USERS_FILE):
            print("Kullanıcı dosyası bulunamadı.")
            return

        users = read_json(USERS_FILE)
        users = [user for user in users if user['user_id'] != user_id]
        """
        # Yeni bir liste tanımlanır
        filtered_users = []

        # Mevcut users listesinde döngü başlatılır
        for user in users:
        # Eğer user_id 2'ye eşit değilse, kullanıcı filtered_users listesine eklenir
            if user['user_id'] != 2:
                filtered_users.append(user)

        # filtered_users listesi, orijinal users listesi ile güncellenir
        users = filtered_users
        """
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


    @staticmethod
    def register():
        """Yeni bir kullanıcı kaydı oluşturur."""
        print("\n=== Kullanıcı Kayıt ===")
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
                    return None

        # Şifre hashleme
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Yeni kullanıcı oluştur
        new_user = User(
            user_id=get_next_user_id(),
            username=username,
            password=hashed_password,
            name=name,
            surname=surname,
            phone_number=phone_number,
            role='user'
        )

        # Kullanıcıyı kaydet
        new_user.save_user()
        print(f"Kayıt başarılı! Hoş geldiniz, {name} {surname}!")
        return new_user

    @staticmethod
    def login():
        """Kullanıcı girişi yapar."""
        print("\n=== Kullanıcı Girişi ===")
        username = input("Kullanıcı Adı: ").strip()
        password = input("Şifre: ").strip()

        users = []
        if os.path.exists(USERS_FILE):
            users = read_json(USERS_FILE)
        else:
            print("Kullanıcı veritabanı bulunamadı.")
            return None

        for user_data in users:
            if user_data['username'] == username:
                # Şifreyi kontrol et
                if bcrypt.checkpw(password.encode('utf-8'), user_data['password'].encode('utf-8')):
                    # Kullanıcı nesnesini oluştur ve döndür
                    return User(
                        user_id=user_data['user_id'],
                        username=user_data['username'],
                        password=user_data['password'],
                        name=user_data['name'],
                        surname=user_data['surname'],
                        phone_number=user_data['phone_number'],
                        role=user_data.get('role', 'user'),
                        attempts=user_data.get('attempts', 0),
                        last_attempt_date=user_data.get('last_attempt_date', ''),
                        score1=user_data.get('score1'),
                        score2=user_data.get('score2'),
                        score_avg=user_data.get('score_avg')
                    )
                else:
                    print("Şifre yanlış.")
                    return None
        print("Kullanıcı bulunamadı.")
        return None