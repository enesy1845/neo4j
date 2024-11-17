# MultiPartQuizApp

**MultiPartQuizApp**, kullanıcıların sınava girebildiği ve adminlerin sınav içeriklerini yönetebildiği güvenli, çok bölümlü bir sınav yönetim sistemidir. Şifrelenmiş veri işleme özelliğine sahip olan sistem, farklı soru türlerini destekler ve her kullanıcı için ayrıntılı sonuçlar tutar.

## İçindekiler

- [Proje Genel Bakış](#proje-genel-bakış)
- [Dizin Yapısı](#dizin-yapısı)
- [Ana İşlevler](#ana-işlevler)
- [Kurulum ve Yükleme](#kurulum-ve-yükleme)
  - [1. Gereksinimler](#1-gereksinimler)
  - [2. Projenin Klonlanması](#2-projenin-klonlanması)
  - [3. Conda Ortamının Oluşturulması](#3-conda-ortamının-oluşturulması)
  - [4. Gerekli Paketlerin Yüklenmesi](#4-gerekli-paketlerin-yüklenmesi)
  - [5. İlk Admin Hesabının Oluşturulması](#5-ilk-admin-hesabının-oluşturulması)
  - [6. Uygulamanın Çalıştırılması](#6-uygulamanın-çalıştırılması)
- [Testler](#testler)
- [En İyi Uygulamalar ve İpuçları](#en-iyi-uygulamalar-ve-ipuçları)
- [Lisans](#lisans)
- [Sorun Giderme](#sorun-giderme)
- [Proje Hakkında](#proje-hakkında)
- [Destek ve Katkı](#destek-ve-katkı)

## Proje Genel Bakış

Uygulama aşağıdaki ana özelliklerden oluşmaktadır:

- **Kullanıcı Yönetimi**: Kullanıcı kaydı, sınav denemelerinin takibi ve erişim yönetimi.
- **Admin Yönetimi**: Adminlerin soru ekleyip, güncelleyip, silebildiği ve kullanıcıları yönetebildiği sistem.
- **Soru Yönetimi**: Farklı soru türlerinin (Doğru/Yanlış, Tek Seçimlik, Çok Seçimlik) yönetimi.
- **Sınav Yönetimi**: Süre sınırlı sınav yönetimi ve sonuç kaydı.
- **Şifreleme**: Tüm kullanıcı ve sınav verilerinin güvenliğini sağlamak için şifreleme yöntemleri.

## Dizin Yapısı

```
MultiPartQuizApp/
├── data/                     # JSON veri depolama
│   ├── answers/              # Doğru cevaplar
│   │   └── answers.json      # Soruların doğru cevaplarını içeren JSON dosyası
│   ├── questions/            # Soru dosyaları
│   │   ├── multiple_choice_questions.json  # Çoktan seçmeli sorular
│   │   ├── single_choice_questions.json    # Tek seçimli sorular
│   │   └── true_false_questions.json       # Doğru/Yanlış soruları
│   └── users/                # Kullanıcı verileri
│       └── users.json        # Kullanıcı ve admin bilgilerini saklayan JSON dosyası
├── docs/                     # Dokümantasyon
│   └── README.md
├── src/                      # Kaynak kod dosyaları
│   ├── admin.py              # Admin yönetimi
│   ├── exam.py               # Sınav yönetimi
│   ├── main.py               # Uygulamanın giriş noktası
│   ├── question.py           # Soru yönetimi
│   ├── setup_admin.py        # İlk admin kurulumu
│   ├── user.py               # Kullanıcı yönetimi
│   └── utils.py              # Yardımcı işlevler
├── test/                     # Birim testler
│   ├── test_exam.py          # Sınav işlevlerinin testleri
│   ├── test_integration.py   # Entegrasyon testleri
│   ├── test_question.py      # Soru yönetimi testleri
│   ├── test_user.py          # Kullanıcı yönetimi testleri
├── .gitignore
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
- **Admin Doğrulama**: Admin erişimi, master şifre doğrulaması gerektirir.

### 3. Soru Yönetimi (`question.py`)

- **Çoklu Soru Türleri Desteği**: Doğru/Yanlış, Tek Seçimlik ve Çok Seçimlik sorular.
- **CRUD İşlemleri**: Soruları oluşturma, listeleme, güncelleme ve silme.

### 4. Sınav Yönetimi (`exam.py`)

- **Süreli Sınavlar**: Kullanıcılar, belirli sürelerle sınavlara katılabilir.
- **Sonuç Hesaplama**: Her bölüm için puan hesaplanır ve kaydedilir.

### 5. Sonuç Yönetimi (`utils.py` ve `user.py`)

- **Sonuç Takibi**: Kullanıcı sonuçları, her bölüm için kaydedilir ve takip edilir.
- **Başarı/Başarısızlık Değerlendirmesi**: Kullanıcının geçme kriterlerini karşılayıp karşılamadığı kontrol edilir.

## Kurulum ve Yükleme

Bu bölümde, projeyi sıfırdan bilgisayarınıza nasıl kuracağınızı ve çalıştıracağınızı adım adım anlatacağız.

### **1. Gereksinimler**

Projenin çalışması için aşağıdaki yazılımların bilgisayarınızda kurulu olması gerekmektedir:

- **Miniconda** veya **Anaconda**
- **Python 3.9 veya üzeri**
- **Git**

**Kontrol Etme:**

```bash
conda --version
python --version
git --version
```

Eğer bu komutlar sürüm bilgisi döndürüyorsa, yazılımlar yüklüdür. Aksi halde, resmi sitelerinden indirip kurmanız gerekir:

- Miniconda: [https://docs.conda.io/en/latest/miniconda.html](https://docs.conda.io/en/latest/miniconda.html)
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

### **3. Conda Ortamının Oluşturulması**

Sanal ortamlar, projelerin bağımlılıklarını izole etmek için kullanılır.

1. **Conda Ortamını Oluşturun:**

   ```bash
   conda create -n quiz_app_env python=3.9
   ```

   - `quiz_app_env` ortamın adıdır; isterseniz değiştirebilirsiniz.
   - `python=3.9` kullanmak istediğiniz Python sürümüdür.

2. **Ortamı Aktifleştirin:**

   ```bash
   conda activate quiz_app_env
   ```

   - Ortam başarılı bir şekilde aktifleştirildiyse, terminal satırının başında `(quiz_app_env)` ifadesini görürsünüz.

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
   ```

   **Not:** Projeye eklediğiniz diğer bağımlılıkları da bu dosyaya eklemeyi unutmayın.

### **5. İlk Admin Hesabının Oluşturulması**

Program ilk kez çalıştırıldığında, eğer sistemde admin kullanıcısı yoksa, ilk admin kullanıcısı otomatik olarak oluşturulacaktır.

1. **Uygulamayı Çalıştırın:**

   ```bash
   python ./src/main.py
   ```

2. **Admin Bilgilerini Girin:**

   Program, ilk admin kullanıcısını oluşturmak için sizden gerekli bilgileri isteyecektir:

   - Kullanıcı adı
   - Şifre
   - Adınız
   - Soyadınız
   - Telefon numaranız

   **Not:** Bu işlem sadece ilk çalıştırmada yapılır. Daha sonraki çalıştırmalarda bu adım atlanacaktır.

### **6. Uygulamanın Çalıştırılması**

1. **Ana Programı Başlatın:**

   ```bash
   python main.py
   ```

2. **Giriş Yapın veya Kayıt Olun:**

   Uygulama çalıştığında size seçenekler sunacaktır:

   - `1`: Kayıt Ol
   - `2`: Giriş Yap
   - `3`: Çıkış

   **Admin İşlemleri:**

   - Admin olarak giriş yapıp soru ekleyebilir, güncelleyebilir veya silebilirsiniz.
   - Kullanıcıları yönetebilir, listeler ve gerektiğinde silebilirsiniz.
   - Yeni adminler oluşturabilirsiniz (master şifre gerekebilir).

   **Kullanıcı İşlemleri:**

   - Kullanıcı olarak kayıt olabilir ve giriş yapabilirsiniz.
   - Sınavlara katılabilir ve sonuçlarınızı görüntüleyebilirsiniz.

---

## Testler

Tüm testleri çalıştırmak için:

```bash
python -m unittest discover -s test
```

### Test Kapsamı

- **test_user.py**: Kullanıcı kaydı, giriş ve deneme takibi testleri.
- **test_exam.py**: Sınav başlatma, süre yönetimi ve soru işleme testleri.
- **test_question.py**: Soru yönetimi testleri.
- **test_integration.py**: Modüller arası etkileşimleri test ederek tam iş akışı doğrulaması sağlar.

## En İyi Uygulamalar ve İpuçları

### 1. Conda Ortamlarının Kullanımı

- Proje bağımlılıklarını izole etmek için Conda ortamlarını kullanın.
- Ortamı etkinleştirmek için:

  ```bash
  conda activate quiz_app_env
  ```

- Ortamdan çıkmak için:

  ```bash
  conda deactivate
  ```

### 2. Bağımlılıkların Yönetimi

- Yeni paketler yükledikten sonra `requirements.txt` dosyasını güncelleyin:

  ```bash
  pip freeze > requirements.txt
  ```

### 3. Güvenlik ve Gizlilik

- **Şifreler ve Hassas Bilgiler**: Kullanıcı şifreleri `bcrypt` ile hashlenerek güvenli bir şekilde saklanır.
- **Master Şifre**: Admin oluştururken kullanılan master şifreyi güçlü bir şifreyle değiştirin ve güvenli bir yerde saklayın.

### 4. Hata Ayıklama

- **Günlük Kayıtları**: Hataları tespit etmek için gerektiğinde `print` ifadeleri veya logging kullanabilirsiniz.
- **Kullanıcı Girdileri**: Kullanıcı girdilerini doğrulayarak olası hataların önüne geçebilirsiniz.

## Lisans

Bu proje MIT Lisansı ile lisanslanmıştır. Daha fazla bilgi için [LICENSE](LICENSE) dosyasına bakınız.

---

## Sorun Giderme

- **Conda Komutları Tanınmıyor:**

  - Miniconda veya Anaconda'nın sistem PATH değişkenine eklendiğinden emin olun.
  - Kurulum sırasında 'Add Anaconda3 to my PATH environment variable' seçeneğini işaretleyin.
  - Komut istemini veya PowerShell'i kapatıp yeniden açın.

- **Modül Bulunamadı Hataları:**

  - Gerekli paketlerin yüklendiğinden emin olun:

    ```bash
    pip install -r requirements.txt
    ```

- **Sanal Ortam Aktifleştirme Sorunları:**

  - Ortamı aktifleştirmeden önce `conda init` komutunu çalıştırın ve terminali yeniden başlatın:

    ```bash
    conda init
    ```

- **Python Dosyaları Bulunamıyor:**

  - Uygulamayı çalıştırırken doğru dizinde olduğunuzdan emin olun.
  - `main.py` dosyasının mevcut olup olmadığını kontrol edin.

- **İzin Hataları:**

  - Bazı dosya veya klasörlere erişimde sorun yaşıyorsanız, dosya izinlerini kontrol edin.

---

## Proje Hakkında

Bu proje, Python kullanılarak geliştirilmiş ve konsol tabanlı bir uygulamadır. Kullanıcı arayüzü komut satırı üzerinden etkileşimlidir. Uygulama, eğitim amaçlı sınavlar düzenlemek ve yönetmek için basit ve güvenli bir çözüm sunar.

---

## Destek ve Katkı

Proje ile ilgili geri bildirimleriniz veya katkılarınız için lütfen GitHub üzerinden iletişime geçin.

---

**Teşekkürler ve İyi Çalışmalar!**

---

**Önemli Not:**

- **.env Dosyası Artık Kullanılmıyor:**

  - Önceki sürümlerde kullanılan `.env` dosyası ve ilgili kodlar kaldırılmıştır.
  - Şifreleme işlemleri ve diğer hassas bilgiler, kod içerisinde veya güvenli bir şekilde yönetilmektedir.

- **Kurulum Adımlarının Özeti:**

  1. Projeyi klonlayın.
  2. Conda ortamını oluşturup etkinleştirin.
  3. Gerekli paketleri yükleyin.
  4. Uygulamayı çalıştırın ve ilk admin hesabını oluşturun.

---

**Not:** Bu README dosyası, projeyi sorunsuz bir şekilde kurup çalıştırmanız için gerekli tüm bilgileri içermektedir. Herhangi bir sorunla karşılaşırsanız, [Sorun Giderme](#sorun-giderme) bölümüne göz atabilir veya destek için bizimle iletişime geçebilirsiniz.

---
