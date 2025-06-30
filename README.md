
# Dex API Server (Render / Flask)

خادم بسيط لفك ضغط ملفات dex باستخدام `baksmali.jar`.

## الاستخدام:
أرسل ملف `classes.dex` عبر POST إلى:

    /upload

وسيعود السيرفر بملف `smali_out.zip`.

### تشغيل محليًا:
```bash
pip install flask
wget https://github.com/JesusFreke/smali/releases/download/v2.5.2/baksmali-2.5.2.jar -O baksmali.jar
python3 server.py
```
