# File: session_routes.py
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import Session, Question
import uuid

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
                # 去除首尾空白，截取前 10 个字符
                context = session.context.strip()
                return context[:10] + ("..." if len(context) > 10 else "")
            # 如果 context 为空，使用 started_at 生成标题
            return f"Session from {session.started_at.strftime('%Y-%m-%d')}"
        except Exception as e:
            current_app.logger.error(f"Error generating title: {str(e)}")
            return "Untitled Session"

    return jsonify({
        "sessions": [
            {
                "session_id": s.session_id,
                "started_at": s.started_at.isoformat(),
                "title": generate_title(s)
            }
            for s in sessions
        ]
    })


@session_bp.route("/messages", methods=["GET"])
@jwt_required()
def get_messages():
    """
    根据 session_id 拉取该会话的所有问答记录
    """
    user_id = get_jwt_identity()
    session_uuid = request.args.get("session_id", "")
    # 先按 UUID 查到对应 Session 对象
    sess = (
        Session.query
        .filter_by(user_id=user_id, session_id=session_uuid)
        .first_or_404(description="Session not found")
    )

    # 再用 sess.id 去查 Question
    questions = (
        Question.query
        .filter_by(session_id=sess.id)
        .order_by(Question.asked_at)
        .all()
    )

    messages = []
    for q in questions:
        messages.append({
            "type": "text",
            "sender": "user",
            "content": q.user_question,
            "timestamp": q.asked_at.isoformat()
        })
        messages.append({
            "type": "text",
            "sender": "bot",
            "content": q.answer,
            "timestamp": q.asked_at.isoformat()
        })

    return jsonify({"messages": messages}), 200
