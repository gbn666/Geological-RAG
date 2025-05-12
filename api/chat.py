# File: api/chat.py

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
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def allowed_file(filename):
    return os.path.splitext(filename)[1].lower() in ALLOWED_EXTENSIONS


def validate_upload(file_storage):
    if not allowed_file(file_storage.filename):
        return False, f"Unsupported file type: {file_storage.filename}"
    file_storage.stream.seek(0, os.SEEK_END)
    size = file_storage.stream.tell()
    file_storage.stream.seek(0)
    if size > MAX_FILE_SIZE:
        return False, "File too large (max 5MB)"
    return True, None


@chat_bp.route("/<session_id>/chat", methods=["POST"])
@jwt_required()
def chat(session_id):
    try:
        # 1. Validate session
        user_id = get_jwt_identity()
        sess = Session.query.filter_by(session_id=session_id, user_id=user_id).first()
        if not sess:
            return jsonify({"error": "Session not found or expired."}), 404

        # 2. Parse inputs: handle multipart first
        uploaded_file = request.files.get('file')
        if uploaded_file:
            question = request.form.get('question', '').strip() or None
        else:
            data = request.get_json(silent=True) or {}
            question = (data.get('question') or '').strip() or None

        image_url = None
        img_path = None

        current_app.logger.info(f"[DEBUG] chat(): question={question!r}, uploaded_file={bool(uploaded_file)}")

        # 3. Handle upload if file provided
        if uploaded_file:
            valid, err = validate_upload(uploaded_file)
            if not valid:
                return jsonify({"error": err}), 400
            filename = f"{uuid.uuid4().hex}_{secure_filename(uploaded_file.filename)}"
            save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            uploaded_file.save(save_path)
            # record upload
            db.session.add(Image(user_id=user_id, session_id=sess.id, image_path=save_path))
            db.session.commit()
            img_path = save_path
            image_url = os.path.join(current_app.config['UPLOAD_URL_PATH'], filename)
        else:
            # if no file, try JSON image_url
            data = data if uploaded_file else (request.get_json(silent=True) or {})
            image_url = data.get('image_url') or data.get('imageUrl') or data.get('image_path')

        # 4. Require at least text or image
        if not (question or img_path or image_url):
            return jsonify({"error": "请提供文本(question)或图片。"}), 422

        # 5. Load classes and device
        _, _, classes = get_dataloaders(
            current_app.config['TRAIN_DIR'],
            current_app.config['VAL_DIR']
        )
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        # 6. Image classification
        candidates = []
        raw_preds = []
        if img_path or image_url:
            if not img_path and image_url:
                name = os.path.basename(image_url)
                img_path = os.path.join(current_app.config['UPLOAD_FOLDER'], name)
            if os.path.isfile(img_path):
                try:
                    model = load_img_model().to(device)
                    model.load_state_dict(torch.load(
                        current_app.config['IMG_MODEL_PATH'], map_location=device
                    ))
                    preds = image_classification_module(img_path, model, classes, device, topk=3)
                    raw_preds = preds
                    current_app.logger.info(f"[DEBUG] chat(): raw_preds={preds}")
                    for name, prob in preds:
                        try:
                            kg_info = query_knowledge_graph(name)
                        except:
                            kg_info = None
                        candidates.append((name, prob, kg_info))
                except Exception as e:
                    current_app.logger.error(f"[ERROR] chat(): classification failed: {e}")
            else:
                current_app.logger.warning(f"[WARNING] chat(): image file not found: {img_path}")

        # 7. Text-only fallback
        if not candidates and question:
            for cname in classes:
                if cname.lower() in question.lower():
                    try:
                        kg_info = query_knowledge_graph(cname)
                    except:
                        kg_info = None
                    candidates.append((cname, 1.0, kg_info))

        # 8. Text features
        text_summary = ''
        if question:
            text_model, text_tokenizer = load_text_model(device)
            feats = extract_text_features(question, text_model, text_tokenizer, max_length=128, device=device)
            text_summary = f"维度: {tuple(feats.shape)}, 均值: {feats.mean().item():.4f}, 标准差: {feats.std().item():.4f}"

        # 9. Construct prompt
        prompt_lines = [
            "系统：你是地质与矿物学专家。",
            ("本平台“岩识”致力于为用户提供高效、精准的多模态矿物鉴定与咨询服务，"
             "同时为地质学家、学生和爱好者提供一个可上传岩石/矿物图片并提出自然语言问题的智能问答系统。"),
            "纯图像分类结果（仅类别+置信度）：",
        ]
        if raw_preds:
            for name, prob in raw_preds:
                prompt_lines.append(f"- {name}：{prob:.2f}")
        else:
            prompt_lines.append("- 无（未检测到图像或分类失败）")
        prompt_lines.append("候选矿物信息（图像识别＋知识图谱）：")
        if candidates:
            for name, prob, kg in candidates:
                info = kg or '无知识图谱信息'
                prompt_lines.append(f"- {name}，置信度 {prob:.0%}，详情：{info}")
        else:
            prompt_lines.append("（无候选信息，请确保图片清晰或补充文字描述）")
        if question:
            prompt_lines.append("用户提问：")
            prompt_lines.append(question)
        elif img_path:
            prompt_lines.append("用户未提供文本，仅上传图片，请仅根据图像信息给出专业判断。")
        if text_summary:
            prompt_lines.append("文本特征摘要：")
            prompt_lines.append(text_summary)
        prompt_lines.append(
            "请在最终回答中使用有趣有准确科学的语言描述，可以加入一些表情符号，"
            "仅给出对用户问题的专业判断和详细解释，"
            "并使用清晰的缩进和换行来组织你的答案。"
        )
        prompt = "\n".join(prompt_lines)

        # 10. LLM inference
        answer = llm_inference(prompt)

        # 11. Persist
        sess.context = (sess.context or '') + '\n' + prompt + f"\n回答：{answer}"
        db.session.add(Question(session_id=sess.id, user_question=question or '', answer=answer))
        db.session.commit()

        # 12. Response
        return jsonify({
            "answer": answer,
            "kg_candidates": [{"name": n, "prob": p, "kg_info": k} for n, p, k in candidates],
            "raw_preds": [{"name": n, "prob": p} for n, p in raw_preds]
        })
    except Exception:
        current_app.logger.error(traceback.format_exc())
        return jsonify({"error": "内部服务器错误，请稍后重试。"}), 500
