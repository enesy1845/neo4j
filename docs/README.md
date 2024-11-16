# MultiPartQuizApp

**MultiPartQuizApp**, kullanıcıların sınava girebildiği ve adminlerin sınav içeriklerini yönetebildiği güvenli, çok bölümlü bir sınav yönetim sistemidir. Şifrelenmiş veri işleme özelliğine sahip olan sistem, farklı soru türlerini destekler ve her kullanıcı için ayrıntılı sonuçlar tutar..

## İçindekiler

- [Proje Genel Bakış](#proje-genel-bakış)
- [Dizin Yapısı](#dizin-yapısı)
- [Ana İşlevler](#ana-işlevler)
- [Kurulum ve Yükleme](#kurulum-ve-yükleme)
- [Uygulamanın Çalıştırılması](#uygulamanın-çalıştırılması)
- [Testler](#testler)

## Proje Genel Bakış

Uygulama aşağıdaki ana özelliklerden oluşmaktadır:

- **Kullanıcı Yönetimi**: Kullanıcı kaydı, sınav denemelerinin takibi ve erişim yönetimi.
- **Admin Yönetimi**: Adminlerin soru ekleyip, güncelleyip, silebildiği ve kullanıcıları yönetebildiği sistem.
- **Soru Yönetimi**: Farklı soru türlerinin (Doğru/Yanlış, Tek Seçimlik, Çok Seçimlik) yönetimi.
- **Sınav Yönetimi**: Süre sınırlı sınav yönetimi ve sonuç kaydı.
- **Şifreleme**: Tüm kullanıcı ve sınav verilerinin güvenliğini sağlamak için AES şifreleme.

## Dizin Yapısı

```
MultiPartQuizApp/
├── data/                     # JSON veri depolama
│   ├── admins/               # Admin verileri
│   │   └── admins.json       # Admin bilgilerini saklayan JSON dosyası
│   ├── answers/              # Doğru cevaplar
│   │   └── answers.json      # Soruların doğru cevaplarını içeren JSON dosyası
│   ├── questions/            # Soru dosyaları
│   │   ├── multiple_choice_questions.json  # Çoktan seçmeli sorular
│   │   ├── single_choice_questions.json    # Tek seçimli sorular
│   │   └── true_false_questions.json       # Doğru/Yanlış soruları
│   └── users/                # Kullanıcı verileri
│       └── users.json        # Kullanıcı bilgilerini saklayan JSON dosyası
├── docs/                     # Dokümantasyon
│   └── README.md
├── src/                      # Kaynak kod dosyaları
│   ├── admin.py              # Admin yönetimi
│   ├── encryption.py         # Şifreleme işlevleri
│   ├── exam.py               # Sınav yönetimi
│   ├── main.py               # Uygulamanın giriş noktası
│   ├── question.py           # Soru yönetimi
│   ├── result.py             # Sonuç işleme
│   ├── setup_admin.py        # İlk admin kurulumu
│   ├── user.py               # Kullanıcı yönetimi
│   └── utils.py              # Yardımcı işlevler
├── test/                     # Birim testler
│   ├── test_encryption.py    # Şifreleme testleri
│   ├── test_exam.py          # Sınav işlevlerinin testleri
│   ├── test_integration.py   # Entegrasyon testleri
│   ├── test_question.py      # Soru yönetimi testleri
│   ├── test_result.py        # Sonuç işleme testleri
│   └── test_user.py          # Kullanıcı yönetimi testleri
├── .gitignore
├── LICENSE
└── requirements.txt          # Gerekli Python paketleri
```

## Ana İşlevler

### 1. Kullanıcı Yönetimi (`user.py`)

- **Kayıt & Giriş**: Kullanıcılar kayıt olabilir, giriş yapabilir ve sınav denemeleri takip edilebilir.
- **CRUD İşlemleri**: Kullanıcı bilgilerini listeleme, güncelleme ve silme.

### 2. Admin Yönetimi (`admin.py`)

- **Soru ve Kullanıcı Yönetimi**: Adminler soru ekleyebilir, güncelleyebilir, silebilir ve kullanıcıları yönetebilir.
- **Admin Doğrulama**: Admin erişimi, ana parola doğrulaması gerektirir.

### 3. Soru Yönetimi (`question.py`)

- **Çoklu Soru Türleri Desteği**: Doğru/Yanlış, Tek Seçimlik ve Çok Seçimlik sorular.
- **CRUD İşlemleri**: Soruları oluşturma, listeleme, güncelleme ve silme.

### 4. Sınav Yönetimi (`exam.py`)

- **Süreli Sınavlar**: Kullanıcılar, belirli sürelerle sınavlara katılabilir.
- **Sonuç Hesaplama**: Her bölüm için puan hesaplanır ve kaydedilir.

### 5. Şifreleme (`encryption.py`)

- **Veri Güvenliği**: Kullanıcı verileri, sorular ve sonuçlar AES şifreleme ile korunur.
- **Şifreleme Yöntemleri**: Verilerin güvenli işlenmesi için `encrypt` ve `decrypt` fonksiyonları kullanılır.

### 6. Sonuç Yönetimi (`result.py`)

- **Sonuç Takibi**: Kullanıcı sonuçları, her bölüm için kaydedilir ve takip edilir.
- **Başarı/Başarısızlık Değerlendirmesi**: Kullanıcının geçme kriterlerini karşılayıp karşılamadığı kontrol edilir.

## Kurulum ve Yükleme

1. **Projeyi Klonlayın**:

   ```bash
   git clone https://github.com/username/MultiPartQuizApp.git
   cd MultiPartQuizApp
   ```

2. **Gereksinimleri Yükleyin**:

   ```bash
   pip install -r requirements.txt
   ```

3. **İlk Admin Kurulumu**:
   Başlangıçta bir admin hesabı oluşturmak için scripti çalıştırın.
   ```bash
   python src/setup_admin.py
   ```

## Uygulamanın Çalıştırılması

Uygulamayı başlatmak için:

```bash
python src/main.py
```

- **Kullanıcı Girişi**: Kullanıcılar giriş yaparak sınava başlayabilir.
- **Admin Erişimi**: Adminler giriş yaparak kullanıcı ve soru yönetimi işlemlerini gerçekleştirebilir.

## Testler

Tüm testleri çalıştırmak için:

```bash
python -m unittest discover -s test
```

### Test Kapsamı

- **test_encryption.py**: Şifreleme ve deşifre işlemlerini doğrular.
- **test_user.py**: Kullanıcı kaydı, giriş ve deneme takibi testleri.
- **test_exam.py**: Sınav başlatma, süre yönetimi ve soru işleme testleri.
- **test_result.py**: Sonuç hesaplama ve puan kaydı doğruluğunu test eder.
- **test_integration.py**: Modüller arası etkileşimleri test ederek tam iş akışı doğrulaması sağlar.
