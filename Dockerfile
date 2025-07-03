# استخدم صورة أساسية تحتوي على Python و JDK
FROM python:3.9-slim-bullseye

# تثبيت JDK وأدوات النظام
RUN apt-get update && apt-get install -y \
    openjdk-17-jre-headless \
    wget \
    && rm -rf /var/lib/apt/lists/*

# نسخ الملفات
WORKDIR /app
COPY . .

# تثبيت تبعيات Python مباشرة (بدون venv)
RUN pip install --no-cache-dir -r requirements.txt

# تنزيل smali/baksmali إذا لم تكن موجودة
RUN if [ ! -f baksmali.jar ]; then \
        wget -q https://github.com/JesusFreke/smali/releases/download/v2.5.2/baksmali-2.5.2.jar -O baksmali.jar; \
    fi

RUN if [ ! -f smali.jar ]; then \
        wget -q https://github.com/JesusFreke/smali/releases/download/v2.5.2/smali-2.5.2.jar -O smali.jar; \
    fi

# الأمر التشغيلي المعدل (بدون تفعيل venv)
CMD ["gunicorn", "--bind", "0.0.0.0:${PORT}", "--timeout", "300", "--workers", "1", "--access-logfile", "-", "--error-logfile", "-", "server:app"]