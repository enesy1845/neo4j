Elbette, `README.md` dosyanızı `rich` kütüphanesinin `requirements.txt` üzerinden yüklenememesi sorununu ve olası çözümleri içerecek şekilde güncelleyebilirim. Aşağıda, mevcut içeriğinize ek olarak bu sorunu ele alan bir bölüm eklenmiştir.

---

# Exam Management System

## Genel Bakış

Bu proje, öğrenci ve öğretmenlerin sınavlara katılabileceği, yöneticilerin ise kullanıcıları ve istatistikleri yönetebileceği basit bir sınav yönetim sistemidir.

## Kurulum

1. **MiniConda Ortamını Oluşturma**

   ```bash
   conda env create -f environment.yml
   conda activate exam_project
   ```

2. **Gerekli Bağımlılıkların Yüklenmesi**
   ```bash
   pip install -r requirements.txt
   ```

## Kullanım

Ana programı çalıştırmak için:

```bash
python main.py
```

Test senaryosunu çalıştırmak için:

```bash
python tests/test_scenario.py
```

## Docker Kullanımı

Projeyi Docker kullanarak çalıştırmak için aşağıdaki adımları takip edebilirsiniz:

1. **Docker İmajını Oluşturma**

   Proje dizininizde terminal veya komut istemcisini açın ve aşağıdaki komutu çalıştırın:

   ```bash
   docker-compose build
   ```

2. **Konteyneri Başlatma**

   İmaj oluşturulduktan sonra, konteynerinizi başlatmak için aşağıdaki komutu çalıştırın:

   ```bash
   docker-compose up
   ```

   Test senaryosunu çalıştırmak için, Dockerfile'da `CMD` satırını `python tests/test_scenario.py` olarak ayarladığınızdan emin olun. Ana uygulamayı çalıştırmak isterseniz, `CMD ["python", "main.py"]` olarak değiştirebilirsiniz.

3. **Arka Planda Çalıştırma**

   Konteyneri arka planda çalıştırmak için:

   ```bash
   docker-compose up -d
   ```

4. **Konteyneri Durdurma**

   Çalışan konteyneri durdurmak için:

   ```bash
   docker-compose down
   ```

## Gereksinimler

- Python 3.10
- Docker ve Docker Compose

## Proje Yapısı

```
proje_dizini/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── main.py
├── tools/
│   ├── __init__.py
│   ├── user.py
│   ├── exam.py
│   ├── result.py
│   └── utils.py
├── tests/
│   ├── __init__.py
│   └── test_scenario.py
├── users/
│   ├── users.json
│   ├── statistics.json
│   └── user_answers.json
├── answers/
│   └── answers.json
└── questions/
    ├── questions_section1.json
    ├── questions_section2.json
    ├── questions_section3.json
    └── questions_section4.json
```

## Sorun Giderme

### Rich Kütüphanesinin `requirements.txt` Üzerinden Yüklenememesi

Projeyi kurarken `rich` kütüphanesinin `requirements.txt` dosyasından yüklenememesi durumuyla karşılaşabilirsiniz. Bu sorunu çözmek için aşağıdaki adımları izleyebilirsiniz:

1. **Pip Sürümünü Güncelleme**

   İlk olarak, pip'in en son sürümüne sahip olduğunuzdan emin olun:

   ```bash
   pip install --upgrade pip
   ```

2. **Rich Kütüphanesini Manuel Olarak Yükleme**

   `rich` kütüphanesini doğrudan pip ile yüklemeyi deneyin:

   ```bash
   pip install rich
   ```

3. **Doğru Kütüphane Adını ve Sürümünü Kontrol Etme**

   `requirements.txt` dosyanızda `rich` kütüphanesinin doğru şekilde yazıldığından ve uygun bir sürüm numarası içerdiğinden emin olun. Örneğin:

   ```txt
   rich==13.3.2
   ```

   Veya sürüm belirtmek istemiyorsanız:

   ```txt
   rich
   ```

4. **Python Sürümünü Kontrol Etme**

   `rich` kütüphanesinin Python 3.10 ile uyumlu olduğundan emin olun. Genel olarak, `rich` Python 3.6 ve üzeri sürümlerle uyumludur.

5. **Ağ Bağlantısını Kontrol Etme**

   İnternet bağlantınızın aktif ve istikrarlı olduğundan emin olun. Bazen ağ sorunları paketlerin indirilmesini engelleyebilir.

6. **PyPI Mirror Kullanma**

   Eğer PyPI'nin varsayılan mirror'unda sorun yaşıyorsanız, farklı bir mirror kullanarak `rich` kütüphanesini yüklemeyi deneyebilirsiniz:

   ```bash
   pip install rich --index-url https://pypi.org/simple
   ```

7. **Virtual Environment Kullanma**

   Bağımlılıkların çakışmasını önlemek için bir sanal ortam (virtual environment) kullanmayı deneyin:

   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   pip install -r requirements.txt
   ```

8. **Cache Temizleme**

   Pip önbelleğini temizleyerek yükleme sorunlarını çözebilirsiniz:

   ```bash
   pip cache purge
   pip install --no-cache-dir -r requirements.txt
   ```

### Diğer Yaygın Sorunlar ve Çözümleri

- **Bağımlılık Çakışmaları:**
  
  Farklı paketlerin farklı sürümlerini gerektirmesi durumunda çakışmalar olabilir. Bu durumda, `requirements.txt` dosyasındaki paket sürümlerini uyumlu hale getirmeyi deneyin.

- **İzin Problemleri:**
  
  Yükleme sırasında izin hataları alıyorsanız, komutları `sudo` ile çalıştırmayı deneyin (Linux/Mac için) veya yönetici olarak komut istemcisini açın (Windows için).

- **Eksik Sistem Bağımlılıkları:**
  
  Bazı Python paketleri, sistem seviyesinde bağımlılıklara ihtiyaç duyabilir. Örneğin, `bcrypt` kütüphanesi için `libffi` ve `openssl` gibi kütüphanelerin yüklü olması gerekebilir.

  **Linux İçin:**
  ```bash
  sudo apt-get update
  sudo apt-get install build-essential libffi-dev python3-dev
  ```

  **Mac İçin:**
  ```bash
  brew install libffi
  ```

  **Windows İçin:**
  - Visual Studio Build Tools yükleyin: [Visual Studio Build Tools](https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022)
  
## Katkıda Bulunma

Katkıda bulunmak isterseniz, lütfen [CONTRIBUTING.md](CONTRIBUTING.md) dosyasını inceleyin.

## Lisans

Bu proje MIT Lisansı ile lisanslanmıştır. Daha fazla bilgi için [LICENSE](LICENSE) dosyasına bakabilirsiniz.

---

Bu güncellemelerle, `README.md` dosyanız `rich` kütüphanesi ile ilgili yaşanabilecek kurulum sorunlarını ve çözüm önerilerini içermektedir. Ayrıca, Docker kullanımına dair temel adımlar da eklenmiştir. Bu sayede, kullanıcılarınız projeyi kurarken karşılaşabilecekleri sorunları kolayca çözebilirler.

Başka bir konuda yardıma ihtiyacınız olursa, lütfen çekinmeden sorun!