# modules/auth.py
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from app import db
from models import User  # 你在 models.py 中定义的 User 类

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    # 1. 参数校验
    for field in ("username","email","password"):
        if not data.get(field):
            return jsonify({"error": f"缺少字段 {field}"}), 400
    # 2. 唯一性检查
    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"error":"用户名已存在"}), 400
    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error":"邮箱已被注册"}), 400
    # 3. 创建用户、哈希密码
    user = User(username=data["username"], email=data["email"])
    user.password_hash = generate_password_hash(data["password"])
    db.session.add(user); db.session.commit()
    return jsonify({"msg":"注册成功"}), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data.get("username")).first()
    if not user or not check_password_hash(user.password_hash, data.get("password","")):
        return jsonify({"error":"用户名或密码错误"}), 401
    # 4. 签发 JWT
    token = create_access_token(identity=user.id)
    return jsonify({"access_token": token, "expires_in": app.config["JWT_ACCESS_TOKEN_EXPIRES"]})

@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    uid = get_jwt_identity()
    user = User.query.get(uid)
    return jsonify({"id": user.id, "username": user.username, "email": user.email})
