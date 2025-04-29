import os
import uuid
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from PIL import Image

upload_bp = Blueprint("upload", __name__, url_prefix="/api")

# 支持的扩展名
ALLOWED_EXT = {"jpg", "jpeg", "png"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT

@upload_bp.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(e):
    return jsonify({"error": "文件过大，最大允许5MB"}), 413

@upload_bp.route("/upload", methods=["POST"])
@jwt_required()
def upload():
    # 确保上传目录存在
    upload_folder = current_app.config.get("UPLOAD_FOLDER")
    os.makedirs(upload_folder, exist_ok=True)

    if "file" not in request.files:
        return jsonify({"error": "no file part"}), 400
    file = request.files["file"]
    if file.filename == "" or not allowed_file(file.filename):
        return jsonify({"error": "invalid file"}), 400

    # 校验图片文件
    try:
        file.stream.seek(0)
        img = Image.open(file.stream)
        img.verify()
    except Exception:
        return jsonify({"error": "invalid image file"}), 400
    finally:
        file.stream.seek(0)

    # 生成安全文件名，仅使用 UUID + 原始扩展名
    ext = secure_filename(file.filename).rsplit(".", 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    save_path = os.path.join(upload_folder, filename)

    try:
        file.save(save_path)
    except Exception as e:
        current_app.logger.error(f"Upload failed: {e}")
        return jsonify({"error": "upload failed"}), 500

    # 返回可公开访问的 URL
    public_path = f"/uploads/{filename}"
    return jsonify({"image_url": public_path}), 201
