import torch
from modules.image_recognition.image_module import (
    load_model as load_img_model,
    get_dataloaders,
    image_classification_module
)
from modules.text_processing.text_module import load_text_model, extract_text_features
from modules.kg_query.kg_module import query_knowledge_graph
from modules.llm_inference.inference import llm_inference

# 全局对话状态
session_state = {
    "candidates": None,   # 保存第一次提取或按需重新提取的 (name, prob, kg_info) 列表
    "history": []         # 保存传入 LLM 的消息流
}

# 图片相关意图关键词
IMAGE_INTENT_KEYWORDS = {
    "颜色", "色泽", "形状", "纹理", "大小", "尺寸",
    "颗粒", "晶体", "结构", "表面", "纹路"
}


def needs_image_processing(user_question: str) -> bool:
    """判断用户问题是否包含图片相关关键词，决定是否重新运行图像模型"""
    return any(kw in user_question for kw in IMAGE_INTENT_KEYWORDS)


def extract_candidates_from_text(user_question: str, classes):
    """
    纯文本情况下，简单匹配类别名作为候选，置信度设为1.0
    """
    return [(c, 1.0) for c in classes if c in user_question]


def process_image_part(image_path, device, classes):
    """调用图像模型并查询 KG，返回完整的候选信息列表"""
    img_model = load_img_model(num_classes=len(classes)).to(device)
    img_model.load_state_dict(torch.load(
        "F:/pycharm/RAG/modules/image_recognition/convit_mineral.pth",
        map_location=device
    ))
    topk = image_classification_module(image_path, img_model, classes, device, topk=3)
    results = []
    for name, prob in topk:
        kg_info = query_knowledge_graph(name)
        results.append((name, prob, kg_info))
    return results


def process_text_part(user_question, device):
    """提取文本特征并生成摘要"""
    text_model, text_tokenizer = load_text_model(device)
    feats = extract_text_features(user_question, text_model, text_tokenizer,
                                  max_length=128, device=device)
    return (
        f"维度: {tuple(feats.shape)}, "
        f"均值: {feats.mean().item():.4f}, "
        f"标准差: {feats.std().item():.4f}"
    )


def build_prompt(candidate_info_list, user_question, text_summary, extra_context=None):
    """整合候选信息、用户提问及文本摘要，构造 LLM Prompt"""
    prompt = "候选矿物信息（图像识别＋知识图谱）：\n"
    if candidate_info_list:
        for name, prob, kg in candidate_info_list:
            prompt += f"- {name} (置信度: {prob:.2f}) → {kg}\n"
    else:
        prompt += "（无候选信息）\n"
    prompt += f"\n用户提问：\n{user_question}\n"
    prompt += f"\n文本特征摘要：\n{text_summary}\n"
    if extra_context:
        prompt += f"\n额外信息：\n{extra_context}\n"
    prompt += "\n请结合以上信息，给出详细回答："
    return prompt


def chat_step(image_path, user_question, classes):
    """
    单轮问答：
    - 第一次或按需重新识别图片
    - 文本候选提取（无图时）
    - 文本特征摘要
    - 构造并更新 LLM 会话历史
    - 返回 LLM 回答
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # 第一次提取候选
    if session_state["candidates"] is None:
        if image_path:
            session_state["candidates"] = process_image_part(image_path, device, classes)
        else:
            txt_cands = extract_candidates_from_text(user_question, classes)
            session_state["candidates"] = [
                (c, p, query_knowledge_graph(c)) for c, p in txt_cands
            ]

    # 如果问题涉及图片属性，则重新提取
    if image_path and needs_image_processing(user_question):
        session_state["candidates"] = process_image_part(image_path, device, classes)

    # 文本摘要
    text_summary = process_text_part(user_question, device)

    # 构造本轮 Prompt
    prompt = build_prompt(session_state["candidates"], user_question, text_summary)

    # 初始化 LLM 消息列表
    if not session_state["history"]:
        session_state["history"].append({
            "role": "system",
            "content": "你是地质和矿物领域专家，结合候选矿物信息回答用户问题。"
        })

    # 添加用户消息
    session_state["history"].append({"role": "user", "content": prompt})

    # 调用 LLM
    answer = llm_inference(messages=session_state["history"])

    # 添加模型回复到历史
    session_state["history"].append({"role": "assistant", "content": answer})

    return answer


def new_conversation():
    """清空会话状态，开始新的问答"""
    session_state["candidates"] = None
    session_state["history"].clear()


def chat_system():
    """CLI 演示"""
    print("=== 多模态问答系统 ===")
    img = input("请输入图片路径（留空仅文本）：").strip() or None
    _, _, classes = get_dataloaders("F:/data1/train", "F:/data1/val")

    print("输入 'new' 开启新会话；输入 'quit' 退出。")
    while True:
        q = input("\n问题：").strip()
        if q.lower() in ("quit", "退出"):
            break
        if q.lower() == "new":
            new_conversation()
            print("已重置会话。")
            continue

        ans = chat_step(img, q, classes)
        print(f"\n回答：\n{ans}\n")


if __name__ == "__main__":
    chat_system()
