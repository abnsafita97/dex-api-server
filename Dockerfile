FROM openjdk:17-slim

# تثبيت تبعيات النظام
RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-venv gcc unzip wget curl \
    && rm -rf /var/lib/apt/lists/*

# إنشاء مجلد العمل
WORKDIR /app

# نسخ ملفات متطلبات بايثون أولاً
COPY requirements.txt .

# تثبيت تبعيات بايثون
RUN pip install --no-cache-dir -r requirements.txt

# نسخ ملفات المشروع
COPY . .

# الأمر التشغيلي
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "--access-logfile", "-", "--error-logfile", "-", "server:app"]