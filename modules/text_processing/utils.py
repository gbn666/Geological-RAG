# modules/text_processing/utils.py

from transformers import BertTokenizer
import torch

# 选择预训练模型名称（如果处理中文可以选择 'bert-base-chinese'）
MODEL_NAME = 'bert-base-uncased'

# 初始化 Tokenizer
tokenizer = BertTokenizer.from_pretrained(MODEL_NAME)

def preprocess_text(text, max_length=128, device=torch.device("cpu")):
    """
    将输入文本进行分词、padding 和 truncation，
    返回模型所需的字典格式输入张量。

    参数:
      text (str): 待处理的文本。
      max_length (int): 序列最大长度。
      device (torch.device): 张量所在设备。

    返回:
      dict: 包含 input_ids、attention_mask 等张量。
    """
    inputs = tokenizer(
        text,
        max_length=max_length,
        padding='max_length',
        truncation=True,
        return_tensors="pt"
    )
    # 移动到指定设备
    inputs = {k: v.to(device) for k, v in inputs.items()}
    return inputs
