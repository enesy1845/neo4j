# MultiPartQuizApp

**MultiPartQuizApp**, kullanıcıların sınava girebildiği ve adminlerin sınav içeriklerini yönetebildiği güvenli, çok bölümlü bir sınav yönetim sistemidir. Şifrelenmiş veri işleme özelliğine sahip olan sistem, farklı soru türlerini destekler ve her kullanıcı için ayrıntılı sonuçlar tutar.

## İçindekiler

- [Proje Genel Bakış](#proje-genel-bakış)
- [Dizin Yapısı](#dizin-yapısı)
- [Ana İşlevler](#ana-işlevler)
- [Kurulum ve Yükleme](#kurulum-ve-yükleme)
  - [1. Gereksinimler](#1-gereksinimler)
  - [2. Projenin Klonlanması](#2-projenin-klonlanması)
  - [3. Sanal Ortam Oluşturma](#3-sanal-ortam-oluşturma)
  - [4. Gerekli Paketlerin Yüklenmesi](#4-gerekli-paketlerin-yüklenmesi)
  - [5. Ortam Değişkenlerinin Ayarlanması (.env Dosyası)](#5-ortam-değişkenlerinin-ayarlanması-env-dosyası)
  - [6. İlk Admin Hesabının Oluşturulması](#6-ilk-admin-hesabının-oluşturulması)
  - [7. Uygulamanın Çalıştırılması](#7-uygulamanın-çalıştırılması)
- [Testler](#testler)
- [En İyi Uygulamalar ve İpuçları](#en-iyi-uygulamalar-ve-ipuçları)
- [Lisans](#lisans)

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
├── .env                      # Ortam değişkenleri (git tarafından izlenmez)
├── LICENSE
├── requirements.txt          # Gerekli Python paketleri
└── README.md                 # Proje dokümantasyonu
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

Bu bölümde, projeyi sıfırdan bilgisayarınıza nasıl kuracağınızı ve çalıştıracağınızı adım adım anlatacağız.

### **1. Gereksinimler**

Projeyi çalıştırmak için aşağıdaki yazılımların bilgisayarınızda kurulu olması gerekmektedir:

- **Python 3.8 veya üzeri**
- **Git**

**Kontrol Etme:**

```bash
python --version
git --version
```

Eğer bu komutlar sürüm bilgisi döndürüyorsa, yazılımlar yüklüdür. Aksi halde, resmi sitelerinden indirip kurmanız gerekir:

- Python: [https://www.python.org/downloads/](https://www.python.org/downloads/)
- Git: [https://git-scm.com/downloads](https://git-scm.com/downloads)

### **2. Projenin Klonlanması**

Terminal veya komut istemini açarak aşağıdaki adımları izleyin:

1. **Projenin Klonlanacağı Dizine Geçin:**

   ```bash
   cd Desktop  # Veya istediğiniz başka bir dizin
   ```

2. **Projeyi Klonlayın:**

   ```bash
   git clone https://github.com/username/MultiPartQuizApp.git
   ```

   **Not:** `username` kısmını projenin gerçek GitHub kullanıcı adıyla değiştirin.

3. **Proje Dizinine Girin:**

   ```bash
   cd MultiPartQuizApp
   ```

### **3. Sanal Ortam Oluşturma**

Sanal ortamlar, projelerin bağımlılıklarını izole etmek için kullanılır.

1. **Sanal Ortamı Oluşturun:**

   ```bash
   python -m venv myenv
   ```

2. **Sanal Ortamı Etkinleştirin:**

   - **Windows:**

     ```bash
     myenv\Scripts\activate
     ```

   - **macOS/Linux:**

     ```bash
     source myenv/bin/activate
     ```

   Etkinleştirme başarılı olursa, terminal satırının başında `(myenv)` ifadesini görürsünüz.

### **4. Gerekli Paketlerin Yüklenmesi**

1. **pip'i Güncelleyin:**

   ```bash
   pip install --upgrade pip
   ```

2. **Gerekli Paketleri Yükleyin:**

   ```bash
   pip install -r requirements.txt
   ```

   **requirements.txt** dosyasının içeriği:

   ```
   bcrypt==4.0.1
   inputimeout==1.0.4
   pycryptodome==3.9.9
   python-dotenv==1.0.0
   ```

### **5. Ortam Değişkenlerinin Ayarlanması (.env Dosyası)**

1. **.env Dosyasını Oluşturun:**

   ```bash
   touch .env
   ```

2. **SECRET_KEY Oluşturun:**

   ```bash
   python
   ```

   Ardından, Python konsolunda:

   ```python
   import secrets
   secret_key = secrets.token_hex(32)
   print(secret_key)
   exit()
   ```

   Çıktı olarak uzun bir hexadecimal string alacaksınız. Örneğin:

   ```
   9f8e7d6c5b4a39281716253445362728f9e8d7c6b5a49382716253445362728
   ```

3. **.env Dosyasına Değişkenleri Ekleyin:**

   `.env` dosyasını açın ve aşağıdaki gibi doldurun:

   ```env
   SECRET_KEY=9f8e7d6c5b4a39281716253445362728f9e8d7c6b5a49382716253445362728
   DEBUG=True
   ```

4. **.env Dosyasını Versiyon Kontrolünden Hariç Tutun:**

   `.gitignore` dosyanıza `.env` satırını ekleyin:

   ```
   .env
   ```

### **6. İlk Admin Hesabının Oluşturulması**

1. **setup_admin.py Scriptini Çalıştırın:**

   ```bash
   python src/setup_admin.py
   ```

2. **Admin Bilgilerini Girin:**

   Script size admin oluşturmak için gerekli bilgileri soracaktır:

   - Kullanıcı adı
   - Şifre
   - Adınız
   - Soyadınız
   - Telefon numaranız

### **7. Uygulamanın Çalıştırılması**

1. **Ana Programı Başlatın:**

   ```bash
   python src/main.py
   ```

2. **Giriş Yapın:**

   Uygulama çalıştığında size giriş tipi sorulacaktır:

   - `1`: Kullanıcı Girişi
   - `2`: Admin Girişi

**Admin İşlemleri:**

- Admin olarak giriş yapıp soru ekleyebilir, güncelleyebilir veya silebilirsiniz.
- Kullanıcıları yönetebilir, listeler ve gerektiğinde silebilirsiniz.

**Kullanıcı İşlemleri:**

- Kullanıcı olarak giriş yapıp sınava katılabilirsiniz.
- Sınav sonucunda puanlarınız hesaplanır ve kaydedilir.

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

## En İyi Uygulamalar ve İpuçları

### 1. Pip Güncellemesi

Her zaman en son pip sürümünü kullanmak için:

```bash
pip install --upgrade pip
```

### 2. Bağımlılıkların Yönetimi

Yeni paketler yükledikten sonra `requirements.txt` dosyasını güncelleyin:

```bash
pip freeze > requirements.txt
```

### 3. Sanal Ortamların Kullanımı

- Proje bağımlılıklarını izole etmek için sanal ortamları kullanın.
- Sanal ortamı etkinleştirmek için:

  - **Windows:**

    ```bash
    myenv\Scripts\activate
    ```

  - **macOS/Linux:**

    ```bash
    source myenv/bin/activate
    ```

- Sanal ortamdan çıkmak için:

  ```bash
  deactivate
  ```

### 4. Güvenlik ve Gizlilik

- **.env Dosyası**: Hassas bilgileri `.env` dosyasında saklayın ve bu dosyayı versiyon kontrolüne dahil etmeyin.
- **SECRET_KEY**: Şifreleme için kullanılan anahtarın güvenli ve rastgele olmasına dikkat edin.

### 5. Hata Ayıklama

- **DEBUG Modu**: Geliştirme aşamasında `DEBUG=True` ayarını kullanabilirsiniz. Üretim ortamında `DEBUG=False` yapmanız önerilir.

## Lisans

Bu proje MIT Lisansı ile lisanslanmıştır. Daha fazla bilgi için [LICENSE](LICENSE) dosyasına bakınız.

---

Bu rehber ile **MultiPartQuizApp** projenizi başarıyla kurabilir ve çalıştırabilirsiniz. Herhangi bir sorunuz veya katkınız olursa lütfen bizimle iletişime geçin.

---

**Not:** Bu proje şu an bir veritabanı kullanmamaktadır. İleride veritabanı entegrasyonu düşünüyorsanız, yapılandırma ayarlarınızı ve kodunuzu buna göre güncelleyebilirsiniz.

---

**Sorun Giderme**

- **Modül Bulunamadı Hataları:**

  - Eğer `ModuleNotFoundError` alıyorsanız, gerekli paketlerin yüklendiğinden emin olun.
  - Sanal ortamın etkin olduğundan emin olun.

- **Sanal Ortam Aktifleştirme Sorunları:**

  - Eğer sanal ortamı etkinleştiremiyorsanız, doğru dizinde olup olmadığınızı kontrol edin.
  - Windows'ta bazen Güvenlik Duvarı veya Antivirüs yazılımları engelleyebilir.

- **Şifreleme Hataları:**

  - `SECRET_KEY`'in doğru şekilde ayarlandığından ve en az 32 bayt (64 karakter) olduğundan emin olun.
  - `.env` dosyasının doğru dizinde olduğundan ve yüklenebildiğinden emin olun.

- **İzin Hataları:**

  - Bazı dosya veya klasörlere erişimde sorun yaşıyorsanız, dosya izinlerini kontrol edin.

- **Diğer Hatalar:**

  - Hata mesajlarını dikkatlice okuyun ve hangi dosyada veya satırda hata olduğunu belirleyin.
  - Gerekirse, Stack Overflow veya benzeri platformlarda hata mesajınızı aratarak çözüme ulaşabilirsiniz.

---

**Proje Hakkında**

Bu proje, Python kullanılarak geliştirilmiş ve konsol tabanlı bir uygulamadır. Kullanıcı arayüzü komut satırı üzerinden etkileşimlidir. Uygulama, eğitim amaçlı sınavlar düzenlemek ve yönetmek için basit ve güvenli bir çözüm sunar.

---

**Destek ve Katkı**

Projeye katkıda bulunmak veya sorularınızı iletmek isterseniz, lütfen GitHub üzerinden iletişime geçin.

---

**Teşekkürler ve İyi Çalışmalar!**
