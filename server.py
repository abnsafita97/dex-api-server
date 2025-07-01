from flask import Flask, request, send_file
import os
import shutil
import subprocess
import uuid
import zipfile

app = Flask(__name__)
UPLOAD_DIR = "/tmp"

@app.route("/upload", methods=["POST"])
def upload_apk():
    if 'apk' not in request.files:
        return "'apk' field not found. Found: " + str(list(request.files.keys())), 400

    apk_file = request.files['apk']
    job_id = str(uuid.uuid4())
    job_dir = os.path.join(UPLOAD_DIR, f"apkjob_{job_id}")
    os.makedirs(job_dir, exist_ok=True)

    apk_path = os.path.join(job_dir, "input.apk")
    dex_path = os.path.join(job_dir, "classes.dex")
    out_dir = os.path.join(job_dir, "smali_out")

    try:
        # حفظ ملف الـ APK
        apk_file.save(apk_path)

        # استخراج classes.dex من داخل ملف الـ APK
        with zipfile.ZipFile(apk_path, 'r') as zip_ref:
            if "classes.dex" not in zip_ref.namelist():
                return "APK does not contain classes.dex", 400
            zip_ref.extract("classes.dex", path=job_dir)

        # تفكيك ملف dex باستخدام baksmali
        subprocess.check_call([
            "java", "-jar", "baksmali.jar", "d", dex_path, "-o", out_dir
        ])

        # ضغط smali_out إلى ملف ZIP
        zip_path = shutil.make_archive(out_dir, "zip", out_dir)
        return send_file(zip_path, as_attachment=True)

    except Exception as e:
        return f"Error during APK processing: {str(e)}", 500

    finally:
        shutil.rmtree(job_dir, ignore_errors=True)

@app.route("/assemble", methods=["POST"])
def assemble_smali():
    if 'smali' not in request.files:
        return "'smali' field not found. Found: " + str(list(request.files.keys())), 400

    smali_zip = request.files['smali']
    job_id = str(uuid.uuid4())
    job_dir = os.path.join(UPLOAD_DIR, f"assemblejob_{job_id}")
    os.makedirs(job_dir, exist_ok=True)

    zip_path = os.path.join(job_dir, "smali.zip")
    smali_zip.save(zip_path)

    smali_out = os.path.join(job_dir, "smali")
    os.makedirs(smali_out, exist_ok=True)

    try:
        shutil.unpack_archive(zip_path, smali_out)
        dex_output = os.path.join(job_dir, "classes.dex")
        subprocess.check_call([
            "java", "-jar", "smali.jar", "a", smali_out, "-o", dex_output
        ])
        return send_file(dex_output, as_attachment=True)
    except Exception as e:
        return f"Error during assembly: {str(e)}", 500
    finally:
        shutil.rmtree(job_dir, ignore_errors=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
