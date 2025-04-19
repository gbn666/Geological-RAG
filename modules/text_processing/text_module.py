# modules/text_processing/model.py
from transformers import BertModel, BertTokenizer
import torch

# 本地模型路径
model_path = "F:/pycharm/RAG/modules/bert-base-uncased/"


def load_text_model(device=torch.device("cpu")):
    """
    加载预训练的 BERT 模型，并设置为评估模式。

    参数:
      device (torch.device): 模型所在设备。

    返回:
      BertModel: 加载好的 BERT 模型。
      BertTokenizer: 加载好的 BERT 分词器。
    """
    model = BertModel.from_pretrained(model_path)
    model.to(device)
    model.eval()
    tokenizer = BertTokenizer.from_pretrained(model_path)
    return model, tokenizer


def extract_text_features(text, model, tokenizer, max_length=128, device=torch.device("cpu")):
    """
    提取输入文本的特征向量，取 [CLS] token 的隐藏状态作为句子表示。

    参数:
      text (str): 用户输入文本描述。
      model (BertModel): 已加载的预训练 BERT 模型。
      tokenizer (BertTokenizer): BERT 分词器。
      max_length (int): 输入文本最大长度。
      device (torch.device): 计算设备。

    返回:
      torch.Tensor: 文本特征向量，形状为 [1, hidden_dim]。
    """
    # 预处理文本
    inputs = tokenizer(text, return_tensors="pt", padding="max_length", max_length=max_length, truncation=True)
    inputs = {k: v.to(device) for k, v in inputs.items()}

    # 提取特征
    with torch.no_grad():
        outputs = model(**inputs)

    # 取 [CLS] token 对应的输出
    cls_features = outputs.last_hidden_state[:, 0, :]  # shape: [1, hidden_dim]
    return cls_features


if __name__ == '__main__':
    print("Start")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    text_model, text_tokenizer = load_text_model(device)
    sample_text = "I love you"
    features = extract_text_features(sample_text, text_model, text_tokenizer, max_length=128, device=device)
    print("文本特征向量形状：", features.shape)
    print(features)
