# استخدم صورة Python الرسمية مع Bullseye
FROM python:3.11-slim-bullseye

# تثبيت تبعيات النظام (OpenJDK 17 بدلاً من default-jre)
RUN apt-get update && apt-get install -y \
    openjdk-17-jre-headless \
    unzip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# تعيين متغيرات البيئة لزيادة ذاكرة جافا
ENV JAVA_OPTS="-Xms512m -Xmx1024m"

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

# تهيئة مجلد التحميلات مع أذونات صحيحة
RUN mkdir -p /tmp && chmod 777 /tmp

# كشف البورت الذي يستخدمه Railway
EXPOSE 8080

# تشغيل التطبيق باستخدام gunicorn مع إعدادات المهلة والأداء
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--timeout", "600", "--workers", "2", "--worker-class", "gthread", "--threads", "4", "--access-logfile", "-", "--error-logfile", "-", "server:app"]