# استخدم صورة Python الرسمية
FROM python:3.11-slim

# تثبيت Java و unzip (لـ baksmali/smali)
RUN apt-get update && apt-get install -y \
    default-jre \
    unzip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# تعيين مجلد العمل
WORKDIR /app

# نسخ dependencies وتثبيتها
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ ملفات التطبيق
COPY . .

# نسخ ملفات .jar إلى مسار معروف
COPY baksmali.jar /usr/local/bin/baksmali.jar
COPY smali.jar /usr/local/bin/smali.jar

# كشف البورت الذي يستخدمه Railway
EXPOSE 8080

# تشغيل التطبيق باستخدام gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "server:app"]