from flask import Flask, request, send_file, jsonify
import os
import shutil
import subprocess
import uuid
import zipfile
import logging
import traceback
from datetime import datetime

# ===== إعداد نظام التسجيل =====
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# ===== تعريف التطبيق والتهيئة =====
app = Flask(__name__)
UPLOAD_DIR = "/tmp"
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BAKSMALI_PATH = os.path.join(BASE_DIR, "baksmali.jar")
SMALI_PATH = os.path.join(BASE_DIR, "smali.jar")

# ===== تسجيل معلومات البداية =====
logger.info("Starting server with configuration:")
logger.info("Base directory: %s", BASE_DIR)
logger.info("Files in directory: %s", os.listdir(BASE_DIR))
logger.info("Baksmali path exists: %s", os.path.exists(BAKSMALI_PATH))
logger.info("Smali path exists: %s", os.path.exists(SMALI_PATH))

# ===== تسجيل الطلبات والاستجابات =====
@app.before_request
def log_request_info():
    logger.info("Request: %s %s", request.method, request.url)
    logger.info("Headers: %s", dict(request.headers))
    if request.files:
        logger.info("Files received: %s", list(request.files.keys()))

@app.after_request
def log_response_info(response):
    logger.info("Response status: %s", response.status)
    return response

# ===== نقطة البداية =====
@app.route("/")
def home():
    return "DEX API Server is running!", 200

# ===== رفع وتفكيك APK =====
@app.route("/upload", methods=["POST"])
def upload_apk():
    try:
        logger.info("Upload request started")
        
        # التحقق من وجود ملف APK
        if 'apk' not in request.files:
            logger.error("Missing 'apk' field")
            return jsonify(error="'apk' field is required"), 400
        
        apk_file = request.files['apk']
        
        # التحقق من اسم الملف
        if apk_file.filename == '':
            logger.error("No file selected")
            return jsonify(error="No selected file"), 400
        
        # إنشاء مجلد مؤقت
        job_id = str(uuid.uuid4())
        job_dir = os.path.join(UPLOAD_DIR, f"apkjob_{job_id}")
        os.makedirs(job_dir, exist_ok=True)
        logger.info("Created job directory: %s", job_dir)
        
        try:
            # حفظ ملف الـ APK
            apk_path = os.path.join(job_dir, "input.apk")
            apk_file.save(apk_path)
            file_size = os.path.getsize(apk_path)
            logger.info("APK saved: %s (%d bytes)", apk_path, file_size)
            
            # استخراج جميع ملفات DEX
            dex_files = []
            with zipfile.ZipFile(apk_path, 'r') as zip_ref:
                for name in zip_ref.namelist():
                    if name.startswith('classes') and name.endswith('.dex'):
                        dex_files.append(name)
                
                logger.info("Found DEX files: %s", dex_files)
                
                if not dex_files:
                    logger.error("No DEX files found in APK")
                    return jsonify(error="APK does not contain any DEX files"), 400
                
                # استخراج جميع ملفات DEX
                for dex in dex_files:
                    zip_ref.extract(dex, path=job_dir)
                    logger.info("Extracted DEX: %s", dex)
            
            # إنشاء مجلد الإخراج
            out_dir = os.path.join(job_dir, "smali_out")
            os.makedirs(out_dir, exist_ok=True)
            logger.info("Created output directory: %s", out_dir)
            
            # تفكيك كل ملفات DEX
            for dex in dex_files:
                dex_path = os.path.join(job_dir, dex)
                logger.info("Disassembling %s", dex_path)
                
                # تفكيك DEX
                try:
                    result = subprocess.run(
                        ["java", "-jar", BAKSMALI_PATH, "d", dex_path, "-o", out_dir],
                        capture_output=True,
                        text=True,
                        timeout=300  # 5 دقائق لكل ملف DEX
                    )
                    
                    if result.returncode != 0:
                        logger.error("Baksmali failed for %s: %s", dex_path, result.stderr)
                        return jsonify(error=f"DEX disassembly failed: {result.stderr}"), 500
                    
                    logger.info("Baksmali completed for %s", dex)
                
                except subprocess.TimeoutExpired:
                    logger.error("Baksmali timed out for %s", dex_path)
                    return jsonify(error="DEX disassembly timed out"), 500
            
            # ضغط النتيجة
            zip_path = os.path.join(job_dir, "smali_out.zip")
            logger.info("Creating ZIP archive at: %s", zip_path)
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(out_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, out_dir)
                        zipf.write(file_path, arcname)
                        logger.debug("Added to ZIP: %s as %s", file_path, arcname)
            
            logger.info("ZIP created successfully, size: %d bytes", os.path.getsize(zip_path))
            
            # إرسال الملف
            return send_file(
                zip_path,
                as_attachment=True,
                download_name="smali_out.zip",
                mimetype='application/zip'
            )
        
        except zipfile.BadZipFile:
            logger.exception("Invalid APK file")
            return jsonify(error="Invalid APK file format"), 400
        except Exception as e:
            logger.exception("APK processing error")
            return jsonify(error=f"Internal server error: {str(e)}"), 500
        finally:
            shutil.rmtree(job_dir, ignore_errors=True)
    
    except Exception as e:
        logger.error("Unhandled error in upload_apk: %s", traceback.format_exc())
        return jsonify(error="Internal server error"), 500

# ===== تجميع Smali إلى DEX =====
@app.route("/assemble", methods=["POST"])
def assemble_smali():
    try:
        logger.info("Assemble request started")
        
        # التحقق من وجود ملف Smali
        if 'smali' not in request.files:
            logger.error("Missing 'smali' field")
            return jsonify(error="'smali' field is required"), 400
        
        smali_zip = request.files['smali']
        
        # إنشاء مجلد مؤقت
        job_id = str(uuid.uuid4())
        job_dir = os.path.join(UPLOAD_DIR, f"assemblejob_{job_id}")
        os.makedirs(job_dir, exist_ok=True)
        logger.info("Created job directory: %s", job_dir)
        
        try:
            # حفظ ملف الـ ZIP
            zip_path = os.path.join(job_dir, "smali.zip")
            smali_zip.save(zip_path)
            logger.info("Saved smali ZIP: %s", zip_path)
            
            # استخراج ملفات Smali
            smali_dir = os.path.join(job_dir, "smali")
            os.makedirs(smali_dir, exist_ok=True)
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(smali_dir)
                logger.info("Extracted smali files to: %s", smali_dir)
            
            # تجميع ملف DEX
            dex_output = os.path.join(job_dir, "classes.dex")
            logger.info("Assembling DEX to: %s", dex_output)
            
            result = subprocess.run(
                ["java", "-jar", SMALI_PATH, "a", smali_dir, "-o", dex_output],
                capture_output=True,
                text=True,
                timeout=300  # 5 دقائق
            )
            
            if result.returncode != 0:
                logger.error("Smali assembly failed: %s", result.stderr)
                return jsonify(error=f"DEX assembly failed: {result.stderr}"), 500
            
            logger.info("Smali assembly succeeded")
            return send_file(
                dex_output,
                as_attachment=True,
                download_name="classes.dex",
                mimetype='application/octet-stream'
            )
        except Exception as e:
            logger.exception("Assembly error")
            return jsonify(error=f"Internal server error: {str(e)}"), 500
        finally:
            shutil.rmtree(job_dir, ignore_errors=True)
    
    except Exception as e:
        logger.error("Unhandled error in assemble_smali: %s", traceback.format_exc())
        return jsonify(error="Internal server error"), 500

# ===== فحص صحة الخادم =====
@app.route("/health", methods=["GET"])
def health_check():
    try:
        jar_checks = {
            "baksmali": os.path.exists(BAKSMALI_PATH),
            "smali": os.path.exists(SMALI_PATH)
        }
        
        # الحصول على إصدار جافا
        java_version = subprocess.check_output(
            ["java", "-version"],
            stderr=subprocess.STDOUT,
            text=True
        )
        
        return jsonify({
            "status": "OK",
            "server_time": datetime.utcnow().isoformat(),
            "java_version": java_version,
            "jar_files": jar_checks,
            "base_dir_files": os.listdir(BASE_DIR)
        })
    except Exception as e:
        return jsonify({
            "status": "ERROR",
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500

# ===== نقطة الدخول للتشغيل المحلي =====
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    logger.info("Starting local development server on port %d", port)
    app.run(host="0.0.0.0", port=port, debug=False)