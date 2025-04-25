# modules/upload.py
import os, uuid
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename

upload_bp = Blueprint("upload", __name__, url_prefix="/api")

ALLOWED_EXT = {"jpg","jpeg","png"}


def allowed_file(fn):
    return "." in fn and fn.rsplit(".",1)[1].lower() in ALLOWED_EXT

@upload_bp.route("/upload", methods=["POST"])
@jwt_required()
def upload():
    if "file" not in request.files:
        return jsonify({"error":"no file part"}), 400
    file = request.files["file"]
    if file.filename == "" or not allowed_file(file.filename):
        return jsonify({"error":"invalid file"}), 400

    filename = secure_filename(f"{uuid.uuid4().hex}_{file.filename}")
    save_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    file.save(save_path)
    # 返回相对或可访问 URL
    return jsonify({"image_path": save_path})
