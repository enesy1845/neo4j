FROM python:3.10-slim

WORKDIR /app

# Gereksinimleri kopyala ve yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Tüm dosyaları kopyala
COPY . .

# wait-for-it.sh betiğini kopyala ve çalıştırılabilir hale getir
COPY tools/wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

# Uygulama ilk defa başlarken migrate_questions.py çalıştırması için
# Ancak şu anki docker-compose.yml içinde test_scenario.py çalıştırılıyor, bu yüzden CMD yerine bu betiği kullanacağız
# CMD ["python", "main.py"]

# Eğer test senaryosunu çalıştırmak istiyorsanız, aşağıdaki komutu kullanın
CMD ["sh", "-c", "/wait-for-it.sh db:5432 -- python tests/test_scenario.py"]
