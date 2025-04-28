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

# 验证码存储，正式环境建议使用Redis
verify_codes = {}
# 忘记密码验证码存储
reset_codes = {}


@auth_bp.route("/sendCode", methods=["POST"])
@cross_origin()
def send_code():
    data = request.get_json() or {}
    email = data.get("email")
    if not email:
        return jsonify({"error": "缺少邮箱地址"}), 400

    # 生成6位验证码
    code = random.randint(100000, 999999)
    expire_ts = time.time() + 300
    verify_codes[email] = {"code": code, "expire": expire_ts}

    # 发送验证码邮件
    try:
        with mail.connect() as conn:
            msg = Message(
                subject="【矿物识别系统】验证码",
                recipients=[email],
                body=f"您的验证码是：{code}，有效期5分钟。",
                sender=current_app.config.get("MAIL_DEFAULT_SENDER")
            )
            conn.send(msg)
    except Exception as e:
        current_app.logger.error(f"注册验证码发送失败: {e}")
        return jsonify({"error": f"验证码发送失败，错误信息: {e}"}), 500

    return jsonify({"msg": f"验证码已发送至 {email}"}), 200


@auth_bp.route("/register", methods=["POST"])
@cross_origin()
def register():
    data = request.get_json() or {}
    for field in ("email", "password", "verificationCode"):
        if not data.get(field):
            return jsonify({"error": f"缺少字段 {field}"}), 400
    email = data["email"]
    password = data["password"]
    input_code = data["verificationCode"]

    record = verify_codes.get(email)
    if not record:
        return jsonify({"error": "请先发送验证码"}), 400
    if time.time() > record["expire"]:
        verify_codes.pop(email, None)
        return jsonify({"error": "验证码已过期"}), 400
    if str(record["code"]) != str(input_code):
        return jsonify({"error": "验证码错误"}), 400
    verify_codes.pop(email, None)

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "邮箱已被注册"}), 400

    user = User(username=email.split("@")[0], email=email)
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
    return jsonify({"access_token": token, "expires_in": expires_in}), 200


@auth_bp.route("/changePassword", methods=["POST"])
@jwt_required()
@cross_origin()
def change_password():
    data = request.get_json() or {}
    current_pwd = data.get("currentPassword")
    new_pwd = data.get("newPassword")
    if not current_pwd or not new_pwd:
        return jsonify({"error": "缺少当前密码或新密码"}), 400

    user = User.query.get(get_jwt_identity())
    if not user:
        return jsonify({"error": "用户不存在"}), 404
    if not check_password_hash(user.password_hash, current_pwd):
        return jsonify({"error": "当前密码错误"}), 401

    user.password_hash = generate_password_hash(new_pwd)
    db.session.commit()
    return jsonify({"msg": "密码修改成功"}), 200


@auth_bp.route("/forgotPassword/sendCode", methods=["POST"])
@cross_origin()
def forgot_send_code():
    data = request.get_json() or {}
    email = data.get("email")
    if not email:
        return jsonify({"error": "缺少邮箱地址"}), 400
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "邮箱未注册"}), 400

    code = random.randint(100000, 999999)
    expire_ts = time.time() + 300
    reset_codes[email] = {"code": code, "expire": expire_ts}

    try:
        with mail.connect() as conn:
            msg = Message(
                subject="【矿物识别系统】密码重置验证码",
                recipients=[email],
                body=f"您的密码重置验证码是：{code}，有效期5分钟。",
                sender=current_app.config.get("MAIL_DEFAULT_SENDER")
            )
            conn.send(msg)
    except Exception as e:
        current_app.logger.error(f"重置验证码发送失败: {e}")
        return jsonify({"error": f"验证码发送失败，错误信息: {e}"}), 500

    return jsonify({"msg": f"重置验证码已发送至 {email}"}), 200


@auth_bp.route("/forgotPassword/reset", methods=["POST"])
@cross_origin()
def forgot_reset():
    data = request.get_json() or {}
    email = data.get("email")
    input_code = data.get("verificationCode")
    new_pwd = data.get("newPassword")
    if not email or not input_code or not new_pwd:
        return jsonify({"error": "缺少邮箱、验证码或新密码"}), 400

    record = reset_codes.get(email)
    if not record:
        return jsonify({"error": "请先获取验证码"}), 400
    if time.time() > record["expire"]:
        reset_codes.pop(email, None)
        return jsonify({"error": "验证码已过期"}), 400
    if str(record["code"]) != str(input_code):
        return jsonify({"error": "验证码错误"}), 400
    reset_codes.pop(email, None)

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "用户不存在"}), 404
    user.password_hash = generate_password_hash(new_pwd)
    db.session.commit()
    return jsonify({"msg": "密码重置成功"}), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
@cross_origin()
def me():
    user = User.query.get(get_jwt_identity())
    if not user:
        return jsonify({"error": "用户不存在"}), 404
    return jsonify({"id": user.id, "username": user.username, "email": user.email}), 200
