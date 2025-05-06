from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import Session
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
    return jsonify({
        "sessions": [
            {"session_id": s.session_id, "created_at": s.created_at.isoformat()}
            for s in sessions
        ]
    })
