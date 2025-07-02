from flask import Flask, request, send_file, jsonify
import os
import shutil
import subprocess
import uuid
import zipfile
import logging

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
UPLOAD_DIR = "/tmp"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BAKSMALI_PATH = os.path.join(BASE_DIR, "baksmali.jar")
SMALI_PATH = os.path.join(BASE_DIR, "smali.jar")

# تسجيل الطلبات
@app.before_request
def log_request_info():
    logger.info(f"Request: {request.method} {request.path}")
    logger.info(f"Headers: {dict(request.headers)}")
    if request.files:
        logger.info(f"Files: {list(request.files.keys())}")

@app.after_request
def log_response_info(response):
    logger.info(f"Response status: {response.status}")
    return response

@app.route("/")
def home():
    return "DEX API Server is running!", 200

@app.route("/upload", methods=["POST"])
def upload_apk():
    logger.info("Upload request started")
    # ... بقية الكود كما كان ...

@app.route("/health", methods=["GET"])
def health_check():
    # ... بقية الكود كما كان ...

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))  # تم التغيير إلى 8080
    logger.info(f"Starting server on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)