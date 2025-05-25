# File: session_routes.py

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import Session, Question, Image
import uuid
import os

session_bp = Blueprint("session", __name__, url_prefix="/api/session")


@session_bp.route("/new", methods=["POST"])
@jwt_required()
def new_session():
    """
    创建一个新的对话 Session，返回 session_id 给前端
    """
    user_id = get_jwt_identity()
    session_id = str(uuid.uuid4())
    sess = Session(user_id=user_id, session_id=session_id)
    db.session.add(sess)
    db.session.commit()
    return jsonify({"session_id": session_id}), 201


@session_bp.route("/list", methods=["GET"])
@jwt_required()
def list_sessions():
    """
    获取当前用户的所有会话列表
    """
    user_id = get_jwt_identity()
    sessions = (
        Session.query
        .filter_by(user_id=user_id)
        .order_by(Session.id.desc())
        .all()
    )

    def generate_title(session):
        try:
            if session.context:
                ctx = session.context.strip()
                # 提取首个用户提问作为标题关键词
                # 假设 context 格式里 “用户提问：xxx\n” 可提取
                for line in ctx.splitlines():
                    if line.startswith("用户提问") or line.startswith("user_question"):
                        parts = line.split("：", 1)
                        if len(parts) == 2 and parts[1].strip():
                            t = parts[1].strip()
                            return t if len(t) <= 12 else t[:12] + "..."
                # fallback: 前 10 个字符
                return ctx[:10] + ("..." if len(ctx) > 10 else "")
            return f"会话于 {session.started_at.strftime('%Y-%m-%d')}"
        except Exception as e:
            current_app.logger.error(f"生成标题出错：{e}")
            return "未命名会话"

    return jsonify({
        "sessions": [
            {
                "session_id": s.session_id,
                "started_at": s.started_at.isoformat(),
                "title": generate_title(s)
            }
            for s in sessions
        ]
    }), 200


@session_bp.route("/messages", methods=["GET"])
@jwt_required()
def get_messages():
    """
    根据 session_id 拉取该会话的所有问答和图片记录
    前端调用示例：GET /api/session/messages?session_id=<id>
    """
    user_id = get_jwt_identity()
    session_uuid = request.args.get("session_id", "").strip()
    if not session_uuid:
        return jsonify({"error": "缺少 session_id 参数"}), 400

    # 查 Session
    sess = Session.query.filter_by(
        user_id=user_id,
        session_id=session_uuid
    ).first()
    if not sess:
        return jsonify({"error": "Session 未找到"}), 404

    # 查所有图片记录（按ID升序）
    images = (
        Image.query
        .filter_by(session_id=sess.id)
        .order_by(Image.id)
        .all()
    )

    # 查所有问答记录（按时间或ID）
    questions = (
        Question.query
        .filter_by(session_id=sess.id)
        .order_by(Question.asked_at)
        .all()
    )

    history = []
    img_idx = 0

    # 如果有 created_at，推荐按时间合并；这里按逻辑顺序简单 interleave
    for q in questions:
        # 先把所有在此之前上传的图片加入
        while img_idx < len(images):
            img = images[img_idx]
            history.append({
                "type": "image",
                "sender": "user",
                "content": current_app.config["UPLOAD_URL_PATH"] + "/" + os.path.basename(img.image_path),
                "timestamp": img.uploaded_at.isoformat() if hasattr(img, "uploaded_at") else None
            })
            img_idx += 1

        # 然后加入这条问答
        history.append({
            "type": "text",
            "sender": "user",
            "content": q.user_question,
            "timestamp": q.asked_at.isoformat()
        })
        history.append({
            "type": "text",
            "sender": "bot",
            "content": q.answer,
            "timestamp": q.asked_at.isoformat()
        })

    # 如果还有剩余图片
    while img_idx < len(images):
        img = images[img_idx]
        history.append({
            "type": "image",
            "sender": "user",
            "content": current_app.config["UPLOAD_URL_PATH"] + "/" + os.path.basename(img.image_path),
            "timestamp": img.uploaded_at.isoformat() if hasattr(img, "uploaded_at") else None
        })
        img_idx += 1

    return jsonify({"messages": history}), 200
