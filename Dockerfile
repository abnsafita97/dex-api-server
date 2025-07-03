# استخدم صورة أساسية تحتوي على Python و JDK
FROM python:3.9-slim-bullseye

# تثبيت تبعيات النظام (احتفظنا بـ wget لأغراض أخرى)
RUN apt-get update && apt-get install -y \
    openjdk-17-jre-headless \
    wget \
    && rm -rf /var/lib/apt/lists/*

# تعيين متغيرات البيئة الافتراضية
ENV PORT=8080
ENV JAVA_OPTS="-Xms512m -Xmx1024m"

# نسخ الملفات (يشمل smali.jar و baksmali.jar)
WORKDIR /app
COPY . .

# تثبيت تبعيات بايثون
RUN pip install --no-cache-dir -r requirements.txt

# نقل ملفات smali و baksmali إلى مسار ثابت وإعطاء أذونات التنفيذ
RUN chmod +x baksmali.jar smali.jar && \
    mv baksmali.jar /usr/local/bin/ && \
    mv smali.jar /usr/local/bin/

# الأمر التشغيلي المعدل
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-8080} --timeout 600 --workers 2 --access-logfile - --error-logfile - server:app"]