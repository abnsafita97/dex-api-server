# استخدم صورة Python الرسمية مع Bullseye
FROM python:3.11-slim-bullseye

# تثبيت تبعيات النظام (OpenJDK 17 بدلاً من default-jre)
RUN apt-get update && apt-get install -y \
    openjdk-17-jre-headless \
    unzip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# تعيين متغيرات بيئة جافا
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH="${JAVA_HOME}/bin:${PATH}"

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

# التحقق من وجود ملفات JAR
RUN ls -la /usr/local/bin
RUN chmod +x /usr/local/bin/baksmali.jar
RUN chmod +x /usr/local/bin/smali.jar

# تهيئة مجلد التحميلات مع أذونات صحيحة
RUN mkdir -p /tmp && chmod 777 /tmp

# كشف البورت الذي يستخدمه Railway
EXPOSE 8080

# تشغيل التطبيق باستخدام gunicorn مع إعدادات المهلة والأداء
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-8080} --timeout 600 --workers 1 --worker-class sync --access-logfile - --error-logfile - server:app"]