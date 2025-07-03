FROM python:3.9-slim-bullseye

# تثبيت تبعيات النظام
RUN apt-get update && apt-get install -y \
    openjdk-17-jre-headless \
    wget \
    && rm -rf /var/lib/apt/lists/*

# تعيين متغيرات البيئة
ENV PORT=8080
ENV JAVA_OPTS="-Xms512m -Xmx1024m"

# إعداد بيئة العمل
WORKDIR /app
COPY . .

# تثبيت تبعيات بايثون
RUN pip install --no-cache-dir -r requirements.txt

# نقل الملفات التنفيذية وإعداد الأذونات
RUN chmod +x baksmali.jar smali.jar && \
    mv baksmali.jar /usr/local/bin/ && \
    mv smali.jar /usr/local/bin/

# تهيئة مجلد التحميلات
RUN mkdir -p /tmp && chmod 777 /tmp

# الأمر التشغيلي مع إعدادات متقدمة
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-8080} --timeout 600 --workers 2 --limit-request-line 0 --limit-request-field_size 0 --access-logfile - --error-logfile - server:app"]