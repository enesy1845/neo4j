FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

<<<<<<< HEAD
# Uygulama ilk defa başlarken migrate_questions.py çalıştırması için entrypoint veya command kullanılabilir.
# Ancak biz docker-compose.yml içinden halledeceğiz.

CMD ["python", "main.py"]
=======
# Uygulamanın çalıştırılacağı komut
# Örneğin, test senaryosunu çalıştırmak için:
#CMD ["python", "tests/test_scenario.py"]

# Veya ana uygulamayı çalıştırmak için:
 CMD ["python", "main.py"]
>>>>>>> 840ee2b94405be7b3ec10e3999cedf628d7bf517
