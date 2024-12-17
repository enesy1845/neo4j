# Python 3.10 Slim imajını kullan
FROM python:3.10-slim

# Çalışma dizinini ayarla
WORKDIR /app

# Gereksinim dosyasını kopyala
COPY requirements.txt .

# Gereksinimleri yükle
RUN pip install --no-cache-dir -r requirements.txt

# Tüm proje dosyalarını kopyala
COPY . .

# Uygulamanın çalıştırılacağı komut
# Örneğin, test senaryosunu çalıştırmak için:
#CMD ["python", "tests/test_scenario.py"]

# Veya ana uygulamayı çalıştırmak için:
 CMD ["python", "main.py"]
