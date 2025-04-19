import torch
import os

# 导入各模块函数
from modules.image_recognition.image_module import load_model as load_img_model, get_dataloaders, \
    image_classification_module
from modules.text_processing.text_module import load_text_model, extract_text_features
from modules.kg_query.kg_module import query_knowledge_graph
from modules.llm_inference.inference import llm_inference

# 全局变量保存对话上下文
conversation_context = ""


def build_prompt(candidate_info_list, user_question, text_feature_summary, extra_context=None):
    """
    构建综合 Prompt，将图像候选信息（或知识图谱查询候选）、用户提问和文本特征摘要整合起来。

    参数:
      candidate_info_list (list of tuple): 每个元素为 (candidate_name, prob, kg_info)。
      user_question (str): 用户提问或描述文本。
      text_feature_summary (str): 用户文本提取的特征摘要。
      extra_context (str, optional): 额外上下文信息。

    返回:
      str: 构造好的 Prompt 字符串。
    """
    prompt = "候选矿物信息（来自图像识别及知识图谱）：\n"
    if candidate_info_list:
        for candidate, prob, kg_info in candidate_info_list:
            prompt += f"名称: {candidate}, 置信度: {prob:.2f}, 详情: {kg_info}\n"
    else:
        prompt += "（无图像或文本候选信息）\n"

    prompt += "\n用户提问：\n" + user_question + "\n"
    prompt += "\n文本特征摘要：\n" + text_feature_summary + "\n"
    if extra_context:
        prompt += "\n额外信息：\n" + extra_context + "\n"
    prompt += "\n请结合以上所有信息，给出最终判断和详细解释。"
    return prompt


def extract_candidates_from_text(user_question, classes):
    """
    简单匹配：遍历已知类别，检查用户问题中是否包含这些矿物名称，
    如果包含，则返回 (名称, 1.0) 作为候选项，置信度设置为1.0（代表确定性）。
    """
    candidates_found = []
    for candidate in classes:
        # 如果用户问题中包含候选名称（大小写敏感或不敏感可以根据需求调整）
        if candidate in user_question:
            candidates_found.append((candidate, 1.0))
    return candidates_found


def process_image_part(image_path, device, classes):
    """
    如果提供了图片路径，则调用图像识别模块和知识图谱查询获取候选信息，
    否则返回空列表。
    """
    if image_path is None or image_path.strip() == "":
        return []

    # 加载数据集获取类别列表（此处 classes 已经作为参数传入）
    # 加载图像识别模型（确保已训练好且保存的权重已加载）
    img_model = load_img_model().to(device)
    # 加载训练后模型权重
    img_model.load_state_dict(
        torch.load("F:/pycharm/RAG/modules/image_recognition/convit_mineral.pth", map_location=device))
    topk_candidates = image_classification_module(image_path, img_model, classes, device, topk=3)
    print("图像识别候选结果:", topk_candidates)

    candidate_info_list = []
    for candidate, prob in topk_candidates:
        kg_info = query_knowledge_graph(candidate)
        print(f"知识图谱查询 [{candidate}]: {kg_info}")
        candidate_info_list.append((candidate, prob, kg_info))
    return candidate_info_list


def process_text_part(user_question, device):
    """
    调用文本处理模块提取用户文本特征，生成摘要信息。
    """
    text_model, text_tokenizer = load_text_model(device)
    text_features = extract_text_features(user_question, text_model, text_tokenizer, max_length=128, device=device)
    summary = (
        f"维度: {text_features.shape}, "
        f"均值: {text_features.mean().item():.4f}, "
        f"标准差: {text_features.std().item():.4f}"
    )
    return summary


def chat_step(image_path, user_question, classes):
    """
    单轮问答处理：
      - 如果提供图片，则调用图像识别和知识图谱查询
      - 如果不提供图片，则从用户问题中提取候选实体进行知识图谱查询
      - 提取文本特征，构造综合 prompt
      - 调用 LLM 推理生成回答，并更新全局对话上下文
    返回 LLM 的回答。
    """
    global conversation_context
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    if image_path:
        candidate_info_list = process_image_part(image_path, device, classes)
    else:
        candidate_info_list = []
        extracted = extract_candidates_from_text(user_question, classes)
        for candidate, prob in extracted:
            kg_info = query_knowledge_graph(candidate)
            print(f"知识图谱查询 [{candidate}]: {kg_info}")
            candidate_info_list.append((candidate, prob, kg_info))

    text_feature_summary = process_text_part(user_question, device)
    current_prompt = build_prompt(candidate_info_list, user_question, text_feature_summary, extra_context="无额外信息")
    print("构造的 Prompt：\n", current_prompt)

    # 合并对话历史
    if conversation_context:
        full_prompt = conversation_context + "\n" + current_prompt
    else:
        full_prompt = current_prompt

    answer = llm_inference(full_prompt)

    conversation_context += "\n" + current_prompt + "\n回答: " + answer
    return answer


def chat_system():
    """
    交互式问答系统主函数，
    - 用户可以选择是否上传图片，
    - 支持纯文本输入和文本+图片混合输入，
    - 支持重新开启新会话，清空对话上下文。
    """
    global conversation_context
    print("欢迎使用问答系统！")
    print("若不上传图片，请直接按回车。")
    image_path = input("请输入图片路径（或直接按回车跳过）：").strip()
    if image_path == "":
        image_path = None

    # 加载数据集以获取类别列表（无需训练数据，只需类别信息）
    _, _, classes = get_dataloaders("F:/data1/train", "F:/data1/val")

    print("输入 '退出' 或 'quit' 结束会话；输入 '新会话' 或 'new' 开启新的会话。")

    while True:
        user_question = input("请输入问题：").strip()
        if user_question.lower() in ["退出", "quit"]:
            print("会话结束。")
            break
        if user_question.lower() in ["新会话", "new"]:
            conversation_context = ""
            print("已清空对话上下文，开启新会话。")
            continue

        answer = chat_step(image_path, user_question, classes)
        print("\n最终回答：")
        print(answer)
        print("\n-------------------------------\n")


if __name__ == "__main__":
    chat_system()
