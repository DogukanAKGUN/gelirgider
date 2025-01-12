# Python bazlı bir imaj kullan
FROM python:3.10-slim

# Çalışma dizinini ayarla
WORKDIR /app

# Bağımlılıkları yükle
COPY app/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Uygulamayı kopyala
COPY app/ .

# Flask uygulamasını çalıştır
CMD ["python", "app.py"]
