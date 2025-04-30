# modules/chat.py

import uuid
import traceback
import torch
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import Session, Image, Question
from modules.image_recognition.image_module import (
    load_model as load_img_model,
    get_dataloaders,
    image_classification_module
)
from modules.text_processing.text_module import (
    load_text_model,
    extract_text_features
)
from modules.kg_query.kg_module import query_knowledge_graph
from modules.llm_inference.inference import llm_inference
import requests

chat_bp = Blueprint("chat", __name__, url_prefix="/api/session")


@chat_bp.route("/new", methods=["POST"])
@jwt_required()
def new_session():
    user_id = get_jwt_identity()
    session_id = str(uuid.uuid4())
    sess = Session(user_id=user_id, session_id=session_id)
    db.session.add(sess)
    db.session.commit()
    return jsonify({"session_id": session_id})


@chat_bp.route("/<session_id>/chat", methods=["POST"])
@jwt_required()
def chat(session_id):
    try:
        # 1. 解析并验证输入
        data = request.get_json(force=True)
        question = (data.get("question") or "").strip()
        image_path = data.get("image_path")

        if not question and not image_path:
            return jsonify({
                "error": "Either 'question' or 'image_path' must be provided"
            }), 400

        # 2. 校验会话归属
        user_id = get_jwt_identity()
        sess = Session.query.filter_by(
            session_id=session_id, user_id=user_id
        ).first()
        if not sess:
            return jsonify({"error": "Session not found"}), 404

        # 3. 加载类别列表
        train_dir = current_app.config["TRAIN_DIR"]
        val_dir = current_app.config["VAL_DIR"]
        _, _, classes = get_dataloaders(train_dir, val_dir)
        if not classes:
            return jsonify({"error": "No classes in dataset"}), 500

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        candidates = []

        # 4. 图像或文本候选
        if image_path:
            # 4.1 图像模型加载
            model = load_img_model().to(device)
            model.load_state_dict(torch.load(
                current_app.config["IMG_MODEL_PATH"],
                map_location=device
            ))
            # 4.2 图像分类并查询知识图谱
            try:
                for name, prob in image_classification_module(
                    image_path, model, classes, device
                ):
                    kg_info = query_knowledge_graph(name)
                    candidates.append((name, prob, kg_info))
            except requests.exceptions.RequestException as e:
                return jsonify({
                    "error": "Knowledge graph service unreachable",
                    "details": str(e)
                }), 503

            # 4.3 记录图片
            try:
                db.session.add(
                    Image(user_id=user_id,
                          session_id=sess.id,
                          image_path=image_path)
                )
            except Exception:
                # log but continue
                traceback.print_exc()

        else:
            # 纯文本分支
            for name in classes:
                if name in question:
                    try:
                        kg_info = query_knowledge_graph(name)
                    except requests.exceptions.RequestException as e:
                        return jsonify({
                            "error": "Knowledge graph service unreachable",
                            "details": str(e)
                        }), 503
                    candidates.append((name, 1.0, kg_info))

        # 5. 文本特征提取
        text_model, text_tokenizer = load_text_model(device)
        feats = extract_text_features(
            question, text_model, text_tokenizer,
            max_length=128, device=device
        )
        summary = f"维度:{feats.shape}, 均值:{feats.mean().item():.4f}"

        # 6. 构造 Prompt 并调用 LLM
        from modules.intergation.test_inference import build_prompt
        prompt = build_prompt(candidates, question, summary)
        context = sess.context or ""
        full_prompt = f"{context}\n{prompt}" if context else prompt
        answer = llm_inference(full_prompt)

        # 7. 保存上下文与问题记录
        sess.context = f"{full_prompt}\n回答:{answer}"
        db.session.add(
            Question(session_id=sess.id,
                     user_question=question,
                     answer=answer)
        )
        db.session.commit()

        # 8. 返回结果
        return jsonify({
            "answer": answer,
            "kg_candidates": [
                {"name": n, "prob": p, "kg_info": k}
                for n, p, k in candidates
            ]
        })

    except Exception as e:
        # 打印并返回堆栈信息，便于调试
        traceback.print_exc()
        return jsonify({
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500
