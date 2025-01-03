FROM python:3.10-slim

WORKDIR /app

# Gereksinimleri kopyala ve yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH=/app

COPY . .

# wait-for-it.sh betiğini kopyalayacaksan (örnek):
# COPY tools/wait-for-it.sh /wait-for-it.sh
# RUN chmod +x /wait-for-it.sh

# Uvicorn ile FastAPI başlat:
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
