import torch
from modules.image_recognition.image_module import (
    load_model as load_img_model,
    get_dataloaders,
    image_classification_module,
)
from modules.text_processing.text_module import load_text_model, extract_text_features
from modules.kg_query.kg_module import query_knowledge_graph
from modules.llm_inference.inference import llm_inference

# — 全局对话状态
session_state = {
    "candidates": None,   # 本轮或历史的视觉/Text 候选 [(name, prob, kg_info), …]
    "history": [],        # LLM 消息历史 [{'role':…, 'content':…}, …]
    "last_image": None,   # 上次使用的图片路径
}

# — 图片相关意图关键词
IMAGE_INTENT_KEYWORDS = {
    "颜色", "色泽", "形状", "纹理", "大小", "尺寸",
    "颗粒", "晶体", "结构", "表面", "纹路", '是啥', '是什么'
}


def needs_image_processing(user_question: str) -> bool:
    """判断用户问题里是否出现图片属性关键词，需要重新运行图像模型"""
    return any(kw in user_question for kw in IMAGE_INTENT_KEYWORDS)


def extract_candidates_from_text(user_question: str, classes):
    """
    纯文本提问时，简单匹配类别名称作为候选，置信度设为1.0 并查询知识图谱。
    """
    return [(c, 1.0) for c in classes if c in user_question]


def process_image_part(image_path, device, classes):
    """
    调用已训练的图像模型，拿 Top-k 候选并查询 KG，返回 [(name, prob, kg_info), …]
    """
    img_model = load_img_model(num_classes=len(classes)).to(device)
    img_model.load_state_dict(torch.load(
        "F:/pycharm/RAG/modules/image_recognition/convit_mineral.pth",
        map_location=device
    ))
    raw = image_classification_module(image_path, img_model, classes, device, topk=3)
    results = []
    for name, prob in raw:
        try:
            kg_info = query_knowledge_graph(name)
        except Exception:
            kg_info = None
        results.append((name, prob, kg_info))
    return results


def process_text_part(user_question, device):
    """提取文本特征并返回一个简单的统计摘要"""
    text_model, text_tokenizer = load_text_model(device)
    feats = extract_text_features(
        user_question, text_model, text_tokenizer,
        max_length=128, device=device
    )
    return (
        f"维度: {tuple(feats.shape)}, "
        f"均值: {feats.mean().item():.4f}, "
        f"标准差: {feats.std().item():.4f}"
    )


def build_prompt(candidate_info_list, user_question, text_summary, extra_context=None):
    """整合候选信息、用户问句、文本摘要，生成 LLM Prompt，采用结构化标签和输出格式要求"""
    prompt = []
    # 系统角色指令
    prompt.append("系统：你是一位资深地质与矿物学专家，擅长结合图像识别和专业知识回答矿物鉴定问题。")
    prompt.append("\n---\n")
    # 识别结果
    prompt.append("【图像识别结果】")
    if candidate_info_list:
        for name, prob, kg in candidate_info_list:
            prompt.append(f"- {name} (置信度 {prob:.2f}) → {kg or 'KG unavailable'}")
    else:
        prompt.append("（无候选信息）")
    prompt.append("\n---\n")
    # 用户提问
    prompt.append(f"【用户提问】\n{user_question}")
    # 文本摘要
    if text_summary:
        prompt.append(f"\n---\n【文本特征摘要】\n{text_summary}")
    # 输出格式要求
    prompt.append("\n---\n请严格按照以下格式输出：")
    prompt.append("1. 直接结论：一句话总结最可能的矿物。")
    prompt.append("2. 专业验证步骤：最多4条，列表形式。")
    prompt.append("3. 误判风险：一句话说明潜在误判原因。")
    prompt.append("4. 下一步建议：一句话总结后续操作。\n---\n")
    return "\n".join(prompt)


def chat_step(image_path, user_question, classes):
    """
    单轮问答逻辑：
    1. 如果是新图片或首次，重新提取视觉/Text 候选；
    2. 如果问题触发图片意图，再次提取视觉候选；
    3. 文本特征摘要；
    4. 构造带格式化要求的 Prompt，并调用 LLM；
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # 1) 新图或首次
    if session_state["candidates"] is None or image_path != session_state["last_image"]:
        if image_path:
            session_state["candidates"] = process_image_part(image_path, device, classes)
        else:
            txt = extract_candidates_from_text(user_question, classes)
            session_state["candidates"] = [
                (c, p, query_knowledge_graph(c)) for c, p in txt
            ]
        session_state["last_image"] = image_path

    # 2) 图片意图触发重识别
    if image_path and needs_image_processing(user_question):
        session_state["candidates"] = process_image_part(image_path, device, classes)

    # 3) 文本摘要
    text_summary = process_text_part(user_question, device)

    # 4) 构造 Prompt
    prompt = build_prompt(session_state["candidates"], user_question, text_summary)

    # 初始化 system 消息
    if not session_state["history"]:
        session_state["history"].append({"role": "system", "content": prompt})

    # 添加 user 消息
    session_state["history"].append({"role": "user", "content": prompt})

    # 合并调用 LLM
    merged = "\n".join(msg["content"] for msg in session_state["history"])
    answer = llm_inference(merged)

    # 追加 assistant 消息
    session_state["history"].append({"role": "assistant", "content": answer})
    return answer


def new_conversation():
    """清空会话状态"""
    session_state["candidates"] = None
    session_state["history"].clear()
    session_state["last_image"] = None


def chat_system():
    print("=== 多模态问答系统 ===")
    _, _, classes = get_dataloaders("F:/data1/train", "F:/data1/val")

    print("输入 'new' 新会话；'quit' 退出。")
    while True:
        img_in = input("本轮是否上传图片？（路径或回车跳过）: ").strip()
        if img_in.lower() in ("quit", "退出"): break
        if img_in.lower() == "new": new_conversation(); print("会话已重置。"); continue

        image_path = img_in or None
        question = input("请输入问题：").strip()
        if question.lower() in ("quit", "退出"): break
        if question.lower() == "new": new_conversation(); print("会话已重置。"); continue

        ans = chat_step(image_path, question, classes)
        print(f"\n回答：\n{ans}\n")

if __name__ == "__main__":
    chat_system()
