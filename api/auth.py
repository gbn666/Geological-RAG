# modules/auth.py

import random
import time
from flask import Blueprint, request, jsonify, current_app
from flask_mail import Message
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity
)
from flask_cors import cross_origin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, mail
from models import User

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

# 临时存储验证码，正式环境建议放Redis
verify_codes = {}


@auth_bp.route("/sendCode", methods=["POST"])
@cross_origin()
def send_code():
    data = request.get_json() or {}
    email = data.get("email")
    if not email:
        return jsonify({"error": "缺少邮箱地址"}), 400

    # 生成6位验证码
    code = random.randint(100000, 999999)
    expire_ts = time.time() + 300  # 5分钟有效

    verify_codes[email] = {"code": code, "expire": expire_ts}

    # 发邮件
    try:
        with mail.connect() as conn:  # 使用上下文管理器自动连接
            msg = Message(
                subject="【矿物识别系统】验证码",
                recipients=[email],
                body=f"您的验证码是：{code}，有效期5分钟。",
                sender="861191839@qq.com"  # 设置发送者邮件地址
            )
            conn.send(msg)  # 通过连接发送邮件
    except Exception as e:
        current_app.logger.error(f"发送邮件失败: {e}")
        return jsonify({"error": f"邮件发送失败，错误信息: {str(e)}"}), 500

    return jsonify({"msg": f"验证码已发送至 {email}"}), 200


@auth_bp.route("/register", methods=["POST"])
@cross_origin()
def register():
    data = request.get_json() or {}
    # 参数检查
    for field in ("email", "password", "verificationCode"):
        if not data.get(field):
            return jsonify({"error": f"缺少字段 {field}"}), 400

    email = data["email"]
    password = data["password"]
    input_code = data["verificationCode"]

    # 校验验证码
    record = verify_codes.get(email)
    if not record:
        return jsonify({"error": "请先发送验证码"}), 400
    if time.time() > record["expire"]:
        verify_codes.pop(email, None)
        return jsonify({"error": "验证码已过期"}), 400
    if str(record["code"]) != str(input_code):
        return jsonify({"error": "验证码错误"}), 400

    # 验证码正确后，删除验证码
    verify_codes.pop(email, None)

    # 检查邮箱是否已注册
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "邮箱已被注册"}), 400

    # 创建用户
    username = email.split("@")[0]  # 用邮箱前缀作为默认用户名
    user = User(username=username, email=email)
    user.password_hash = generate_password_hash(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({"msg": "注册成功"}), 201


@auth_bp.route("/login", methods=["POST"])
@cross_origin()
def login():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "缺少邮箱或密码"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "邮箱或密码错误"}), 401

    token = create_access_token(identity=user.id)
    expires = current_app.config.get("JWT_ACCESS_TOKEN_EXPIRES")
    expires_in = expires.total_seconds() if expires else None

    return jsonify({
        "access_token": token,
        "expires_in": expires_in
    }), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
@cross_origin()
def me():
    uid = get_jwt_identity()
    user = User.query.get(uid)
    if not user:
        return jsonify({"error": "用户不存在"}), 404
    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email
    }), 200
