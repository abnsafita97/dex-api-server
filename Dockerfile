FROM openjdk:17-slim-bullseye

# تثبيت Python وأدوات النظام
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    gcc \
    wget \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# نسخ ملفات المشروع
COPY . .

# إعداد بيئة Python الافتراضية وتثبيت التبعيات
RUN python3 -m venv /opt/venv && \
    . /opt/venv/bin/activate && \
    pip install --no-cache-dir -r requirements.txt

# تحميل ملفات smali و baksmali
RUN wget -q https://github.com/JesusFreke/smali/releases/download/v2.5.2/baksmali-2.5.2.jar -O baksmali.jar && \
    wget -q https://github.com/JesusFreke/smali/releases/download/v2.5.2/smali-2.5.2.jar -O smali.jar

CMD ["sh", "-c", ". /opt/venv/bin/activate && gunicorn -w 4 -b 0.0.0.0:$PORT server:app"]