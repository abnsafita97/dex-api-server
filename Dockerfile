FROM openjdk:17-slim-bullseye

# تثبيت Python و أدوات البناء
RUN apt-get update && \
    apt-get install -y python3 python3-pip python3-venv gcc && \
    rm -rf /var/lib/apt/lists/*

# إنشاء مجلد للعمل
WORKDIR /app

# نسخ فقط الملفات المطلوبة
COPY server.py .
COPY requirements.txt .
COPY baksmali.jar .
COPY smali.jar .

# إنشاء البيئة الافتراضية وتثبيت المتطلبات
RUN python3 -m venv /opt/venv && \
    . /opt/venv/bin/activate && \
    pip install --no-cache-dir -r requirements.txt

# الأمر التشغيلي
CMD ["sh", "-c", ". /opt/venv/bin/activate && gunicorn -w 4 -b 0.0.0.0:$PORT server:app"]
