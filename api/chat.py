# api/chat.py

import os
import uuid
import traceback
import torch
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename

from app import db
from models import Session, Image, Question
from modules.image_recognition.image_module import (
    load_model as load_img_model,
    get_dataloaders,
    image_classification_module
)
from modules.llm_inference.inference import llm_inference
from modules.intergation.test_inference import build_prompt

chat_bp = Blueprint("chat", __name__, url_prefix="/api/session")


@chat_bp.route("/new", methods=["POST"])
@jwt_required()
def new_session():
    user_id = get_jwt_identity()
    session_id = str(uuid.uuid4())
    sess = Session(user_id=user_id, session_id=session_id)
    db.session.add(sess)
    db.session.commit()
    return jsonify({"session_id": session_id}), 201


@chat_bp.route("/<session_id>/chat", methods=["POST"])
@jwt_required()
def chat(session_id):
    try:
        # 1. 解析输入：支持 multipart/form-data 或 JSON（image_url/imageUrl/image_path）
        question = ""
        image_url = None

        if request.content_type and request.content_type.startswith("multipart/"):
            # multipart：一次性上传文件
            question = (request.form.get("question") or "").strip()
            uploaded = request.files.get("file")
            if uploaded:
                fn = f"{uuid.uuid4().hex}_{secure_filename(uploaded.filename)}"
                dest = os.path.join(current_app.config["UPLOAD_FOLDER"], fn)
                uploaded.save(dest)
                image_url = os.path.join(current_app.config["UPLOAD_URL_PATH"], fn)
                db.session.add(Image(
                    user_id=get_jwt_identity(),
                    session_id=Session.query.filter_by(
                        session_id=session_id,
                        user_id=get_jwt_identity()
                    ).first().id,
                    image_path=dest
                ))
        else:
            # JSON：前端两步走模式，也可能上传 image_path
            data = request.get_json(force=True)
            question   = (data.get("question")   or "").strip()
            # 支持下划线、驼峰，以及老版 image_path
            image_url  = data.get("image_url") or data.get("imageUrl") or data.get("image_path")

        if not question and not image_url:
            return jsonify({"error": "请提供 question 或 image_url/imageUrl/image_path"}), 422

        # 2. 校验会话
        user_id = get_jwt_identity()
        sess = Session.query.filter_by(session_id=session_id, user_id=user_id).first()
        if not sess:
            return jsonify({"error": "Session not found"}), 404

        # 3. 准备类别 & 设备
        _, _, classes = get_dataloaders(
            current_app.config["TRAIN_DIR"],
            current_app.config["VAL_DIR"]
        )
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        candidates = []

        # 4. 只要 image_url 存在，就跑 Top-K 图像分类
        raw = []
        if image_url:
            img_name = os.path.basename(image_url)
            img_path = os.path.join(current_app.config["UPLOAD_FOLDER"], img_name)
            if not os.path.isfile(img_path):
                return jsonify({"error": "图片文件不存在", "path": img_path}), 400

            model = load_img_model().to(device)
            model.load_state_dict(torch.load(
                current_app.config["IMG_MODEL_PATH"],
                map_location=device
            ))

            raw = image_classification_module(img_path, model, classes, device)
            for name, prob in raw:
                candidates.append((name, prob, None))

        # 5. 纯文本回退
        if not candidates and question:
            for name in classes:
                if name in question:
                    candidates.append((name, 1.0, None))

        # 6. 构造 Prompt 并调用 LLM
        text_summary = ""  # 如需摘要，可插入 extract_text_features 逻辑
        prompt = build_prompt(candidates, question, text_summary)
        context = sess.context or ""
        full_prompt = f"{context}\n{prompt}"
        answer = llm_inference(full_prompt)

        # 7. 持久化
        sess.context = f"{full_prompt}\nassistant: {answer}"
        db.session.add(Question(session_id=sess.id, user_question=question, answer=answer))
        db.session.commit()

        # 8. 返回 Top-K 列表
        return jsonify({
            "answer": answer,
            "kg_candidates": [
                {"name": n, "prob": p, "kg_info": k}
                for n, p, k in candidates
            ]
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500
