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
from utils import read_json, write_json, get_next_user_id

USERS_FILE = 'data/users/users.json'

class User:
    def __init__(self):
        self.user_id = None
        self.name = ''
        self.surname = ''
        self.phone_number = ''
        self.attempts = 0
        self.last_attempt_date = ''
        self.scores = []
        self.role = 'user'  

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
            'role': self.role 
        }

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
        """Tüm kullanıcıları listeler."""
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
