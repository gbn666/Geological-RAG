# modules/chat.py
import uuid, os
import torch
from flask import Blueprint, request, jsonify
import app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import Session, Image, Question
from modules.image_recognition.image_module import load_model as load_img_model, get_dataloaders, image_classification_module
from modules.text_processing.text_module import load_text_model, extract_text_features
from modules.kg_query.kg_module import query_knowledge_graph
from modules.llm_inference.inference import llm_inference

chat_bp = Blueprint("chat", __name__, url_prefix="/api/session")

@chat_bp.route("/new", methods=["POST"])
@jwt_required()
def new_session():
    user_id = get_jwt_identity()
    session_id = str(uuid.uuid4())
    sess = Session(user_id=user_id, session_id=session_id)
    db.session.add(sess); db.session.commit()
    return jsonify({"session_id": session_id})

@chat_bp.route("/<session_id>/chat", methods=["POST"])
@jwt_required()
def chat(session_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    question = data.get("question","").strip()
    image_path = data.get("image_path")  # 前端先调用 /upload 拿到路径
    # 1. 校验会话归属
    sess = Session.query.filter_by(session_id=session_id, user_id=user_id).first()
    if not sess:
        return jsonify({"error":"Session not found"}), 404

    # 2. 处理图像或文本候选
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    _,_,classes = get_dataloaders(app.config["TRAIN_DIR"], app.config["VAL_DIR"])
    candidates = []
    if image_path:
        model = load_img_model().to(device)
        model.load_state_dict(torch.load(app.config["IMG_MODEL_PATH"], map_location=device))
        for name, prob in image_classification_module(image_path, model, classes, device):
            kg_info = query_knowledge_graph(name)
            candidates.append((name, prob, kg_info))
        # 记录图片关联
        img = Image(user_id=user_id, session_id=sess.id, image_path=image_path)
        db.session.add(img)
    else:
        # 纯文本模式：从问题中匹配类别
        for name in classes:
            if name in question:
                kg_info = query_knowledge_graph(name)
                candidates.append((name, 1.0, kg_info))

    # 3. 文本特征摘要
    text_model, text_tokenizer = load_text_model(device)
    feats = extract_text_features(question, text_model, text_tokenizer, max_length=128, device=device)
    summary = f"维度:{feats.shape}, 均值:{feats.mean().item():.4f}"

    # 4. 构造并调用 LLM
    from modules.intergation.test_inference import build_prompt  # 复用你定义的 prompt 构造函数
    prompt = build_prompt(candidates, question, summary)
    # 如果已有上下文，叠加
    context = sess.context or ""
    full_prompt = context + "\n" + prompt if context else prompt
    answer = llm_inference(full_prompt)

    # 5. 更新会话上下文与记录问题
    sess.context = full_prompt + "\n回答:" + answer
    db.session.add(Question(session_id=sess.id, user_question=question, answer=answer))
    db.session.commit()

    return jsonify({
        "answer": answer,
        "kg_candidates": [
            {"name":n, "prob":p, "kg_info":k} for n,p,k in candidates
        ]
    })
