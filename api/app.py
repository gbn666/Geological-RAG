import os
from flask import Flask, jsonify,request
from flask_jwt_extended import JWTManager
from models import db
from config import Config
from flask_cors import CORS
from flask_mail import Mail

# ✨ 在全局创建 Mail 实例
mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    @app.after_request
    def add_cors_headers(response):
        if request.path.startswith("/api/"):
            response.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
            response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
        return response
    # 初始化各个扩展
    db.init_app(app)
    JWTManager(app)
    mail.init_app(app)  # —— 这里初始化 Flask-Mail

    # 跨域
    CORS(
        app,
        resources={r"/api/*": {"origins": "http://172.20.65.4:3000"}},
        supports_credentials=False,
    )

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
        return jsonify({"error": "Bad Request"}), 400

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not Found"}), 404

    return app


if __name__ == "__main__":
    app = create_app()

    # 使用应用上下文初始化数据库
    with app.app_context():
        db.create_all()  # 初始化数据库表

    # 启动应用
    try:
        app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
    except Exception as e:
        # 捕获启动时的异常
        print(f"Flask 启动时发生错误: {e}")
