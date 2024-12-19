FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Uygulama ilk defa başlarken migrate_questions.py çalıştırması için entrypoint veya command kullanılabilir.
# Ancak biz docker-compose.yml içinden halledeceğiz.

CMD ["python", "main.py"]
