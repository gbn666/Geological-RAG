import torch

# 导入图像识别模块函数
from modules.image_recognition.image_module import load_model as load_img_model, get_dataloaders, image_classification_module
# 导入文本处理模块函数
from modules.text_processing.text_module import load_text_model, extract_text_features
# 导入知识图谱查询模块函数
from modules.kg_query.kg_module import query_knowledge_graph
# 导入 LLM 推理模块函数（例如 DeepSeek API 或其他接口）
from modules.llm_inference.inference import llm_inference


def build_prompt(candidate_info_list, user_question, text_feature_summary, extra_context=None):
    """
    构建综合 Prompt，将图像候选信息、用户提问和文本特征摘要整合起来。

    参数:
      candidate_info_list (list of tuple): 每个元素为 (candidate_name, prob, kg_info)。
      user_question (str): 用户提问或描述文本。
      text_feature_summary (str): 用户文本提取的特征摘要。
      extra_context (str, optional): 其他额外上下文信息。

    返回:
      str: 构造好的 Prompt 字符串。
    """
    prompt = "候选矿物信息（来自图像识别及知识图谱）：\n"
    for candidate, prob, kg_info in candidate_info_list:
        prompt += f"名称: {candidate}, 置信度: {prob:.2f}, 详情: {kg_info}\n"

    prompt += "\n用户提问：\n" + user_question + "\n"
    prompt += "\n文本特征摘要：\n" + text_feature_summary + "\n"
    if extra_context:
        prompt += "\n额外信息：\n" + extra_context + "\n"
    prompt += "\n请结合以上信息，给出最终判断和详细解释。"
    return prompt


def multimodal_inference(image_path, user_question):
    """
    整合图像识别、知识图谱推理、文本处理和 LLM 推理，实现问答系统。

    参数:
      image_path (str): 用户上传图片的文件路径。
      user_question (str): 用户的提问或描述文本。

    返回:
      str: 最终问答结果。
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # --- 图像识别部分 --- #
    train_loader, _, classes = get_dataloaders("F:/data1/train", "F:/data1/val")
    img_model = load_img_model().to(device)
    # 这里假设模型权重已经训练好，加载权重
    img_model.load_state_dict(torch.load("F:/pycharm/RAG/modules/image_recognition/convit_mineral.pth", map_location=device))
    topk_candidates = image_classification_module(image_path, img_model, classes, device, topk=3)
    print("图像识别候选结果:", topk_candidates)

    # --- 知识图谱查询 --- #
    candidate_info_list = []
    for candidate, prob in topk_candidates:
        kg_info = query_knowledge_graph(candidate)
        # 打印知识图谱查询结果
        print(f"知识图谱查询 [{candidate}]: {kg_info}")
        candidate_info_list.append((candidate, prob, kg_info))

    # --- 文本处理部分 --- #
    text_model, text_tokenizer = load_text_model(device)
    text_features = extract_text_features(user_question, text_model, text_tokenizer, max_length=128, device=device)
    text_feature_summary = (
        f"维度: {text_features.shape}, 均值: {text_features.mean().item():.4f}, "
        f"标准差: {text_features.std().item():.4f}"
    )

    # --- 构建综合 Prompt --- #
    prompt = build_prompt(candidate_info_list, user_question, text_feature_summary, extra_context="暂无额外信息")
    print("构造的 Prompt：\n", prompt)

    # --- LLM 推理部分 --- #
    final_result = llm_inference(prompt)
    return final_result


if __name__ == "__main__":
    # 示例调用：请替换 image_path 为实际图片路径，user_question 为用户的提问
    image_path = "F:/pycharm/RAG/api/uploads/47851f4424fe4462bd932c977f687cc9.jpg"
    user_question = "这块岩石的形成环境是怎样的？"
    result = multimodal_inference(image_path, user_question)
    print("最终问答结果：")
    print(result)
