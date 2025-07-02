# ✅ صورة رسمية خفيفة تحتوي على JDK
FROM openjdk:17-slim

# إعداد المتطلبات الأساسية
RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-venv gcc unzip wget curl \
    && rm -rf /var/lib/apt/lists/*

# إنشاء مجلد العمل
WORKDIR /app

# نسخ ملفات متطلبات بايثون أولاً (للاستفادة من caching)
COPY requirements.txt .

# إنشاء بيئة بايثون الافتراضية وتثبيت التبعيات
RUN python3 -m venv /opt/venv && \
    . /opt/venv/bin/activate && \
    pip install --no-cache-dir -r requirements.txt

# نسخ ملفات المشروع (server.py و smali.jar و baksmali.jar فقط مثلاً)
COPY server.py .
COPY smali.jar .
COPY baksmali.jar .

# إعداد أمر التشغيل
CMD ["sh", "-c", ". /opt/venv/bin/activate && gunicorn -w 2 -b 0.0.0.0:$PORT server:app"]
