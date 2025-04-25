# app.py
import os
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from models import db
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # 初始化插件
    db.init_app(app)
    jwt = JWTManager(app)

    # 确保上传目录存在
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # 注册蓝图
    from api.auth import auth_bp
    from api.upload import upload_bp
    from api.chat import chat_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(chat_bp)

    # 全局错误处理（可选）
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"error":"Bad Request"}), 400

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error":"Not Found"}), 404

    return app

if __name__ == "__main__":
    # 在第一次启动时创建数据库表
    app = create_app()
    with app.app_context():
        db.create_all()
    # 启动
    app.run(host="0.0.0.0", port=5000)
