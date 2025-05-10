# -*- coding: utf-8 -*-
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
    image_classification_module,
)
from modules.text_processing.text_module import (
    load_text_model,
    extract_text_features,
)
from modules.kg_query.kg_module import query_knowledge_graph
from modules.llm_inference.inference import llm_inference

chat_bp = Blueprint("chat", __name__, url_prefix="/api/session")

ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.bmp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

def allowed_file(filename):
    return os.path.splitext(filename)[1].lower() in ALLOWED_EXTENSIONS

def validate_upload(file):
    if not allowed_file(file.filename):
        return False, f"Unsupported file type: {file.filename}"
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    if size > MAX_FILE_SIZE:
        return False, "File too large (max 5MB)"
    return True, None

@chat_bp.route("/<session_id>/chat", methods=["POST"])
@jwt_required()
def chat(session_id):
    try:
        user_id = get_jwt_identity()
        sess = Session.query.filter_by(session_id=session_id, user_id=user_id).first()
        if not sess:
            return jsonify({"error": "Session not found or expired."}), 404

        question = None
        image_url = None
        uploaded_file = None

        # -- Unified parsing --
        if request.content_type and request.content_type.startswith('multipart'):
            question = request.form.get('question', '').strip() or None
            files = list(request.files.values())
            if files:
                uploaded_file = files[0]
        else:
            data = request.get_json(force=True)
            question = (data.get('question') or '').strip() or None
            image_url = data.get('image_url') or data.get('imageUrl') or data.get('image_path')

        # -- Validate inputs --
        if not question and not (uploaded_file or image_url):
            return jsonify({"error": "请提供文本(question)或上传图片。"}), 422

        # -- Handle upload --
        if uploaded_file:
            valid, error_msg = validate_upload(uploaded_file)
            if not valid:
                return jsonify({"error": error_msg}), 400
            filename = f"{uuid.uuid4().hex}_{secure_filename(uploaded_file.filename)}"
            save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            uploaded_file.save(save_path)
            image_url = os.path.join(current_app.config['UPLOAD_URL_PATH'], filename)
            db.session.add(Image(user_id=user_id, session_id=sess.id, image_path=save_path))
            db.session.commit()

        # -- Load model & classes --
        train_dir = current_app.config.get('TRAIN_DIR')
        val_dir = current_app.config.get('VAL_DIR')
        _, _, classes = get_dataloaders(train_dir, val_dir)
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # -- Image classification --
        candidates = []
        if image_url:
            img_name = os.path.basename(image_url)
            img_path = os.path.join(current_app.config['UPLOAD_FOLDER'], img_name)
            if not os.path.isfile(img_path):
                return jsonify({"error": "图片文件不存在。"}), 400

            img_model = load_img_model().to(device)
            img_model.load_state_dict(torch.load(
                current_app.config['IMG_MODEL_PATH'], map_location=device
            ))
            preds = image_classification_module(img_path, img_model, classes, device)

            for name, prob in preds:
                kg_info = None
                try:
                    kg_info = query_knowledge_graph(name)
                except Exception:
                    current_app.logger.warning(f"KG lookup failed for {name}")
                candidates.append({"name": name, "prob": prob, "kg_info": kg_info})

        # -- Text fallback --
        if not candidates and question:
            for name in classes:
                if name.lower() in question.lower():
                    kg_info = None
                    try:
                        kg_info = query_knowledge_graph(name)
                    except Exception:
                        current_app.logger.warning(f"KG lookup failed for {name}")
                    candidates.append({"name": name, "prob": 1.0, "kg_info": kg_info})

        # -- Build Prompt --
        prompt_parts = [
            "系统：你是地质与矿物学专家。",
            "本平台“岩识”致力于为用户提供高效、精准的多模态矿物鉴定与咨询服务，同时为地质学家、学生和爱好者提供一个可上传岩石/矿物图片并提出自然语言问题的智能问答系统。",
            "请以清晰、美观、对用户友好的格式回复，使用Markdown进行排版，并可适当加入表情符号以增强阅读体验。",
            "回复应包含以下结构：",
            "- **概述**：简要介绍识别结果或问题背景；",
            "- **详细分析**：结合专业术语和通俗解释；",
            "- **建议与推荐**：给出可操作的后续步骤或参考资料；",
        ]
        if candidates:
            prompt_parts.append("【识别候选 Top-K】")
            for c in candidates:
                info = c['kg_info'] or '无知识图谱信息'
                prompt_parts.append(f"- {c['name']} (置信度 {c['prob']:.2%}) → {info}")
        if question:
            prompt_parts.append("【用户提问】")
            prompt_parts.append(question)
        prompt_parts.append("请结合以上信息，给出专业且易读的回答，并使用适当的Markdown格式。")
        system_prompt = "\n".join(prompt_parts)

        # -- LLM Inference --
        answer = llm_inference(system_prompt)

        # -- Persist --
        sess.context = (sess.context or "") + "\n" + system_prompt + f"\nassistant: {answer}"
        db.session.add(Question(session_id=sess.id, user_question=question or '', answer=answer))
        db.session.commit()

        # -- Response --
        return jsonify({
            "answer": answer,
            "kg_candidates": candidates
        })

    except Exception:
        current_app.logger.error(traceback.format_exc())
        return jsonify({"error": "内部服务器错误，请稍后重试。"}), 500
