# MultiPartQuizApp

1. Proje Amacı
2. Dosya Yapısının Oluşturulması
3. Yardımcı Fonksiyonların (utils.py) Oluşturulması
4. Şifreleme Fonksiyonlarının (encryption.py) Oluşturulması
5. Kullanıcı Yönetiminin (user.py) Oluşturulması
6. Admin Yönetiminin (admin.py)nin Oluşturulması
7. Soru Yönetiminin (question.py) Oluşturulması
8. Sınav Yönetiminin (exam.py) Oluşturulması
9. Sonuç Yönetiminin (result.py) Oluşturulması
10. Admin Kurulumunun (setup_admin.py) Oluşturulması
11. Ana Programın (main.py) Oluşturulması
12. Testlerin (test/ Dizini) Oluşturulması

Bu proje kapsamında, kullanıcıların ve adminlerin etkileşimde bulunabileceği, şifrelenmiş verilerle güvenli bir sınav yönetim sistemi oluşturduk. Proje şu ana bileşenlerden oluşmaktadır:

- Kullanıcı Yönetimi: Kullanıcı hesaplarının oluşturulması, girişi ve sınav denemelerinin yönetilmesi.
- Admin Yönetimi: Adminlerin soruları eklemesi, güncellemesi, silmesi ve kullanıcıları yönetmesi.
- Soru Yönetimi: Farklı türlerde soruların (Doğru/Yanlış, Tek Seçimli, Çok Seçenekli) eklenmesi, listelenmesi, güncellenmesi ve silinmesi.
- Sınav Yönetimi: Sınavların başlatılması, süre yönetimi ve sonuçların kaydedilmesi.
- Şifreleme: Tüm verilerin güvenli bir şekilde şifrelenmesi ve çözülmesi.

2. Dosya Yapısının Oluşturulması
   Proje dizininde aşağıdaki dosya yapısını oluşturduk:

MultiPartQuizApp/
├── data/
│ ├── admins/
│ │ └── admins.json
│ ├── answers/
│ │ └── answers.json
│ ├── questions/
│ │ ├── multiple_choice_questions.json
│ │ ├── single_choice_questions.json
│ │ └── true_false_questions.json
│ └── users/
│ └── users.json
├── docs/
│ └── README.md
├── src/
│ ├── admin.py
│ ├── encryption.py
│ ├── exam.py
│ ├── main.py
│ ├── question.py
│ ├── result.py
│ ├── setup_admin.py
│ ├── user.py
│ └── utils.py
├── test/
│ ├── test_encryption.py
│ ├── test_exam.py
│ ├── test_integration.py
│ ├── test_question.py
│ ├── test_result.py
│ └── test_user.py
├── .gitignore
├── LICENSE
└── requirements.txt

3. Yardımcı Fonksiyonlar (utils.py)
   utils.py dosyasında, proje genelinde kullanılacak yardımcı fonksiyonları oluşturduk:

- def read_json(file_path):
  """Belirtilen JSON dosyasını okur ve veriyi döndürür."""

- def write_json(data, file_path):
  """Veriyi belirtilen JSON dosyasına şifreleyerek yazar."""

- def get_next_user_id():
  ""Kullanıcılar için otomatik ID üretir."""

- def get_next_question_id(question_type):
  """Sorular için otomatik ID üretir."""

- def clear_screen():
  """Konsolu temizler."""

- def validate_input(prompt, valid_options):
  """Kullanıcıdan geçerli bir giriş alır."""
- def format_time(seconds):
  """Saniye cinsinden verilen süreyi dakika ve saniye olarak formatlar."""

- def generate_random_number(start, end):
  """Belirtilen aralıkta rastgele bir sayı üretir."""

4. Şifreleme Fonksiyonları (encryption.py)
   Verilerin güvenliğini sağlamak için şifreleme ve deşifreleme işlemlerini gerçekleştiren fonksiyonları oluşturduk:

- def pad(s):
  """Veriyi 16'nın katları olacak şekilde doldurur."""

- def unpad(s):
  """Doldurulmuş veriyi orijinal haline getirir."""
- def encrypt(data):
  """Veriyi AES ile şifreler."""
- def decrypt(data):
  """Şifrelenmiş veriyi AES ile çözer."""

5. Kullanıcı Yönetimi (user.py)
   Kullanıcı hesaplarının oluşturulması, girişi ve sınav denemelerinin yönetimi için User sınıfını oluşturduk:

- def get_user_info(self):
  """Kullanıcıdan isim, soyisim ve telefon numarası alır."""
- def load_user(self):
  """Kullanıcı bilgilerini users.json dosyasından yükler."""

- def save_user(self):
  """Kullanıcı bilgilerini users.json dosyasına kaydeder."""

- def can_attempt_exam(self):
  """Kullanıcının sınava girme hakkı olup olmadığını kontrol eder."""
- def increment_attempts(self):
  """Sınav giriş sayısını bir artırır ve kaydeder."""

- def to_dict(self):
  """Kullanıcı nesnesini sözlük formatına dönüştürür."""

  # CRUD İşlemleri

@staticmethod

- def list_users():
  """Tüm kullanıcıları listeler."""

@staticmethod

- def delete_user(user_id):
  """Belirtilen ID'ye sahip kullanıcıyı siler."""

@staticmethod

- def update_user(user_id, updated_data):

6. Admin Yönetimi (admin.py)
   Adminlerin soruları yönetmesi, kullanıcıları yönetmesi ve yeni adminler oluşturması için Admin sınıfını oluşturduk:

- def get_admin_info(self):
  """Admin bilgilerini alır ve doğrular."""

- def load_admin(self):
  """Admin bilgilerini admins.json dosyasından yükledik."""

- def save_admin(self):
  """Admin bilgilerini admins.json dosyasına kaydettik."""

- def get_next_admin_id(self):
  """Adminler için otomatik ID üretir."""

- def to_dict(self):
  """Admin nesnesini sözlük formatına dönüştürdük."""

- def admin_menu(self):
  """Admin işlemleri menüsünü yönettik."""

- def list_questions_menu(self, qm):
  """Soruları listelemek için menü sunduk."""

- def create_admin(self):
  """Yeni bir admin oluşturduk, master şifre doğrulaması ile."""

7. Soru Yönetimi (question.py)
   Adminlerin soruları eklemesi, güncellemesi, silmesi ve listelemesi için QuestionManager sınıfını oluşturduk:

- def add_question(self):
  """Yeni bir soru ekler."""

- def list_questions(self, question_type):
  """Belirtilen tipteki veya tüm soruları listeler."""

- def delete_question(self, question_id):
  """Belirtilen ID'ye sahip soruyu siler."""

- def update_question(self, question_id):
  """Belirtilen ID'ye sahip soruyu günceller."""

8. Sınav Yönetimi (exam.py)
   Kullanıcıların sınava girmesini, süreyi yönetmesini ve sonuçları kaydetmesini sağlayan Exam sınıfını oluşturduk:

- def start_exam(self):
  """Sınavı başlatır."""

- def is_time_up(self):
  """Sınav süresinin dolup dolmadığını kontrol eder."""

- def load_questions(self):
  """Tüm soruları yükler ve soru tiplerine göre gruplar."""

- def select_questions_for_section(self, all_questions):
  """Her bölüm için soruları seçer."""

- def present_question(self, question):
  """Kullanıcıya soruyu sunar ve cevabını alır."""

- def get_char(self):
  """Kullanıcıdan non-blocking şekilde karakter okur."""

- def process_input(self, user_input, question):
  """Kullanıcının girdiği cevabı işler."""

- def end_exam(self):
  """Sınavı sonlandırır ve sonuçları hesaplar."""

9. Sonuç Yönetimi (result.py)
   Sınav sonuçlarının yönetimi için ResultManager sınıfını oluşturduk:

- def save_result(self, result):
  """Sınav sonucunu kaydettik."""

- def get_user_results(self, user_id):
  """Belirtilen kullanıcıya ait tüm sınav sonuçlarını getirdik."""

- def list_all_results(self):
  """Tüm sınav sonuçlarını listeledik."""

10. Admin Kurulum (setup_admin.py)
    İlk admin hesabını oluşturmak için setup_admin.py betiğini oluşturduk:

- def create_initial_admin():

11. Ana Program (main.py)
    Projenin giriş noktası olan main.py dosyasını oluşturduk. Kullanıcı veya admin girişi yapma seçeneklerini sunduk:

- def main():

12. Testler (test/ Dizini)
    Projeyi düzgün çalıştırdığımızdan emin olmak için testler yazdık. test/ dizininde her modül için ayrı test dosyaları oluşturduk.

        a. test_encryption.py
        Şifreleme ve deşifreleme fonksiyonlarını test ettik:

        -    def test_encrypt_decrypt(self):

        -    def test_encrypt_different_outputs(self):

        b. test_user.py
        Kullanıcı sınıfının işlevlerini test ettik:
        def setUp(self):

        -   def tearDown(self):
            # Test sırasında oluşturulan dosyayı sil

        -   def test_load_user(self):

        -   def test_can_attempt_exam(self):

        -   def test_increment_attempts(self):

        ....

## Sınıflar ve Fonksiyonlar

### `src/main.py`

- **`main()`**: Uygulamanın giriş noktasıdır. Kullanıcı veya admin girişi seçeneklerini sunmuştur.

### `src/admin.py`

- **`Admin` Sınıfı**: Admin kullanıcılarının giriş yapmasını, soru ve kullanıcı yönetimini sağlamıştır.
  - **`get_admin_info()`**: Admin bilgilerini almış ve doğrulamıştır.
  - **`admin_menu()`**: Admin menüsünü yönetmiştir.
  - **`create_admin()`**: Yeni admin oluşturmuştur.
  - **`list_questions_menu(qm)`**: Soruları listeleme menüsünü sunmuştur.

### `src/user.py`

- **`User` Sınıfı**: Kullanıcıların giriş yapmasını, sınava girmesini ve bilgilerini yönetmiştir.
  - **`get_user_info()`**: Kullanıcı bilgilerini almış ve doğrulamıştır.
  - **`can_attempt_exam()`**: Kullanıcının sınava girip giremeyeceğini kontrol etmiştir.
  - **`list_users()`**: Tüm kullanıcıları listelemiştir.
  - **`delete_user(user_id)`**: Belirtilen kullanıcıyı silmiştir.
  - **`update_user(user_id, updated_data)`**: Belirtilen kullanıcıyı güncellemiştir.

### `src/question.py`

- **`QuestionManager` Sınıfı**: Soruların eklenmesi, güncellenmesi, silinmesi ve listelenmesini sağlamıştır.
  - **`add_question()`**: Yeni soru eklemiştir.
  - **`list_questions(question_type)`**: Belirli bir türde veya tüm soruları listelemiştir.
  - **`delete_question(question_id)`**: Belirli bir ID'ye sahip soruyu silmiştir.
  - **`update_question(question_id)`**: Belirli bir ID'ye sahip soruyu güncellemiştir.

### `src/exam.py`

- **`Exam` Sınıfı**: Sınavın başlatılması, süre yönetimi ve sonuçların kaydedilmesini sağlamıştır.
  - **`start_exam()`**: Sınavı başlatmış ve kullanıcıya soruları sunmuştur.

### `src/result.py`

- **`ResultManager` Sınıfı**: Sınav sonuçlarının yönetilmesini sağlamıştır.
  - **`save_result(result)`**: Sınav sonucunu kaydetmiştir.
  - **`get_user_results(user_id)`**: Belirtilen kullanıcıya ait tüm sınav sonuçlarını getirmiştir.
  - **`list_all_results()`**: Tüm sınav sonuçlarını listelemiştir.

### `src/encryption.py`

- **`encrypt(data)`**: Veriyi şifrelemiştir.
- **`decrypt(data)`**: Şifreli veriyi çözmüştür.
- **Anahtar yönetimi:** `generate_key()`, `load_key()` fonksiyonlarını içerir.

### `src/utils.py`

- **`read_json(file_path)`**: JSON dosyasını okumuş ve veriyi döndürmüştür.
- **`write_json(data, file_path)`**: Veriyi JSON dosyasına şifreleyerek yazmıştır.
- **Diğer yardımcı fonksiyonlar:** `clear_screen()`, `validate_input()`, `format_time()`, `generate_random_number()`.

### `src/setup_admin.py`

- **`setup_initial_admin()`**: İlk admin hesabını oluşturmak için kullanılmıştır.

## Testler

Projeyi düzgün çalıştırdığımızdan emin olmak için testler yazdık. `test/` dizininde her modül için ayrı test dosyaları oluşturduk:

- **`test_encryption.py`**: Şifreleme fonksiyonlarının doğruluğunu test etmiştir.
- **`test_exam.py`**: Sınav sınıfının işlevlerini test etmiştir.
- **`test_integration.py`**: Modüller arası entegrasyonu test etmiştir.
- **`test_question.py`**: Soru yönetim fonksiyonlarını test etmiştir.
- **`test_result.py`**: Sonuçların doğru şekilde kaydedilip kaydedilmediğini test etmiştir.
- **`test_user.py`**: Kullanıcı yönetim fonksiyonlarını test etmiştir.

### Testleri Çalıştırma

Testleri çalıştırmak için aşağıdaki komutu kullandık:

```bash
python -m unittest discover -s test

```
