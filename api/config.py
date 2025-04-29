# config.py

import os
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

# 项目根目录
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# 上传文件保存目录
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')


class Config:
    # ---------- 数据库配置 ----------
    SQLALCHEMY_DATABASE_URI = os.getenv("MYSQL_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ---------- JWT 配置 ----------
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

    # ---------- 训练与验证数据路径 ----------
    TRAIN_DIR = os.getenv("TRAIN_DIR")
    VAL_DIR = os.getenv("VAL_DIR")
    IMG_MODEL_PATH = os.getenv("IMG_MODEL_PATH")

    # ---------- 文件上传 ----------
    UPLOAD_FOLDER = UPLOAD_FOLDER


    # ---------- 邮件 SMTP 配置（SMTPS） ----------
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.qq.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 465))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "false").lower() in ("true", "1", "yes")
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "true").lower() in ("true", "1", "yes")
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", MAIL_USERNAME)

    # ---------- 跨域配置 ----------
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")                 # 允许的前端域名列表
    MAIL_DEBUG = True

    # ---------- 其他配置（可按需添加） ----------
    # 例如：分页大小、日志路径、第三方 API Key 等
