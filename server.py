from flask import Flask, request, send_file
import os
import shutil
import subprocess
import uuid

app = Flask(__name__)

@app.route("/upload", methods=["POST"])
def upload():
    # ✅ تحقق من وجود ملفات في الطلب
    if not request.files:
        return f"No files uploaded at all. Received: {request.files}", 400

    # ✅ تحقق من وجود حقل dex تحديداً
    if 'dex' not in request.files:
        return f"'dex' field not found. Found fields: {list(request.files.keys())}", 400

    dex_file = request.files['dex']
    job_id = str(uuid.uuid4())
    job_dir = f"/tmp/dexjob_{job_id}"
    os.makedirs(job_dir, exist_ok=True)

    dex_path = os.path.join(job_dir, "classes.dex")
    out_dir = os.path.join(job_dir, "smali_out")
    dex_file.save(dex_path)

    try:
        # ✅ نفذ عملية التفكيك باستخدام baksmali
        subprocess.check_call([
            "java", "-jar", "baksmali.jar", "d", dex_path, "-o", out_dir
        ])
        shutil.make_archive(out_dir, "zip", out_dir)
        return send_file(out_dir + ".zip", as_attachment=True)
    except Exception as e:
        return f"Error during processing: {str(e)}", 500
    finally:
        shutil.rmtree(job_dir, ignore_errors=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
