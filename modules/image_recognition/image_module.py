import os
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.optim.lr_scheduler import CosineAnnealingLR
from PIL import Image
import timm
from torchvision.datasets import ImageFolder
from torch.utils.data import DataLoader
from safetensors.torch import load_file  # 用于加载 safetensors 格式的权重

from modules.image_recognition.utils import get_transform
from modules.image_recognition import config

# 强制离线模式，确保不会联网下载
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_OFFLINE"] = "1"


##########################################
# EarlyStopping 类定义
##########################################
class EarlyStopping:
    """
    如果验证损失在连续 `patience` 个 epoch 内没有改善，则提前停止训练。
    """

    def __init__(self, patience=5, verbose=False, delta=0):
        """
        参数:
          patience (int): 等待多少个 epoch 后停止训练
          verbose (bool): 是否打印信息
          delta (float): 改善的最小变化量
        """
        self.patience = patience
        self.verbose = verbose
        self.delta = delta
        self.best_score = None
        self.counter = 0
        self.early_stop = False

    def __call__(self, val_loss):
        score = -val_loss  # 监控验证损失，损失越低越好
        if self.best_score is None:
            self.best_score = score
        elif score < self.best_score + self.delta:
            self.counter += 1
            if self.verbose:
                print(f"早停计数器: {self.counter} / {self.patience}")
            if self.counter >= self.patience:
                self.early_stop = True
        else:
            self.best_score = score
            self.counter = 0


##########################################
# 模型加载与权重加载
##########################################
def load_model(num_classes=config.NUM_CLASSES):
    """
    从本地路径加载预训练的 ConViT 模型，并根据类别数调整最后一层输出。
    这里使用 safetensors 格式加载权重，确保你已将权重文件下载到指定目录 local_model_path 中。
    """
    local_model_path = "F:/pycharm/RAG/modules/convit_tiny"  # 修改为你的本地模型路径
    weight_file = os.path.join(local_model_path, "model.safetensors")
    if not os.path.exists(weight_file):
        raise FileNotFoundError(f"权重文件未找到: {weight_file}")

    # 创建模型但不加载在线预训练权重
    model = timm.create_model(config.MODEL_NAME, pretrained=False, num_classes=1000)
    # 使用 safetensors 加载权重
    state_dict = load_file(weight_file)
    model.load_state_dict(state_dict)

    # 替换分类头：保持原始预训练结构的输入特征维度，输出改为实际类别数
    in_features = model.head.in_features
    model.head = nn.Linear(in_features, num_classes)
    nn.init.kaiming_normal_(model.head.weight, mode='fan_out', nonlinearity='relu')
    if model.head.bias is not None:
        nn.init.constant_(model.head.bias, 0)
    return model


##########################################
# 数据加载器
##########################################
def get_dataloaders(train_dir, val_dir):
    """
    利用 ImageFolder 加载训练和验证数据集，并返回 DataLoader 及类别列表。
    """
    transform = get_transform()
    train_dataset = ImageFolder(root=train_dir, transform=transform)
    val_dataset = ImageFolder(root=val_dir, transform=transform)
    # 检查训练集和验证集类别一致性
    assert train_dataset.classes == val_dataset.classes, "训练集和验证集类别不一致！"
    assert len(train_dataset.classes) == config.NUM_CLASSES, \
        f"数据集类别数 ({len(train_dataset.classes)}) 不等于配置的 {config.NUM_CLASSES}"

    train_loader = DataLoader(train_dataset, batch_size=config.BATCH_SIZE, shuffle=True, num_workers=4)
    val_loader = DataLoader(val_dataset, batch_size=config.BATCH_SIZE, shuffle=False, num_workers=4)
    return train_loader, val_loader, train_dataset.classes


##########################################
# 训练与验证
##########################################
def train_model(model, train_loader, val_loader, device):
    """
    在指定设备上训练模型，并在每个 epoch 后在验证集上评估准确率。
    微调策略：初始冻结预训练层，仅训练分类头，达到冻结周期后解冻所有层进行联合微调，
    同时采用 CosineAnnealingLR 调整学习率，并结合 EarlyStopping 机制。
    """
    model = model.to(device)

    # 冻结预训练层，仅训练分类头
    for param in model.parameters():
        param.requires_grad = False
    for param in model.head.parameters():
        param.requires_grad = True

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.head.parameters(), lr=config.LEARNING_RATE)
    scheduler = CosineAnnealingLR(optimizer, T_max=config.NUM_EPOCHS)

    freeze_epochs = 3  # 前3个 epoch 冻结预训练层
    early_stopping = EarlyStopping(patience=5, verbose=True, delta=0.001)

    for epoch in range(config.NUM_EPOCHS):
        model.train()
        total_loss = 0.0
        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

        scheduler.step()
        avg_loss = total_loss / len(train_loader)
        print(f"Epoch {epoch + 1}/{config.NUM_EPOCHS}, Loss: {avg_loss:.4f}")
        val_loss = validate_model(model, val_loader, device)
        early_stopping(val_loss)
        if early_stopping.early_stop:
            print("早停触发，停止训练。")
            break

        # 解冻预训练层后进行联合微调
        if epoch + 1 == freeze_epochs:
            print("解冻所有层，进行联合微调")
            for param in model.parameters():
                param.requires_grad = True
            optimizer = optim.Adam(model.parameters(), lr=config.LEARNING_RATE / 10)
            scheduler = CosineAnnealingLR(optimizer, T_max=config.NUM_EPOCHS - freeze_epochs)

    return model


def validate_model(model, val_loader, device):
    """
    在验证集上计算模型准确率，并输出验证结果。
    同时返回验证集的平均损失，用于 EarlyStopping 监控。
    """
    model.eval()
    correct, total = 0, 0
    total_loss = 0.0
    criterion = nn.CrossEntropyLoss()
    with torch.no_grad():
        for images, labels in val_loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            loss = criterion(outputs, labels)
            total_loss += loss.item()
            _, preds = torch.max(outputs, 1)
            total += labels.size(0)
            correct += (preds == labels).sum().item()
    avg_loss = total_loss / len(val_loader)
    acc = correct / total
    print(f"验证准确率: {acc:.4f}, 验证损失: {avg_loss:.4f}")
    return avg_loss


##########################################
# 推理函数：对单张图片进行分类
##########################################
def image_classification_module(image_path, model, classes, device, topk=3):
    """
    对指定图片进行预处理和模型推理，返回 Top-k 候选类别及对应置信度。
    """
    transform = get_transform()
    image = Image.open(image_path).convert("RGB")
    image_tensor = transform(image).unsqueeze(0).to(device)

    model.eval()
    with torch.no_grad():
        logits = model(image_tensor)
    probabilities = F.softmax(logits, dim=1)
    topk_prob, topk_idx = torch.topk(probabilities, k=topk, dim=1)

    topk_candidates = []
    for i in range(topk):
        idx = topk_idx[0, i].item()
        if idx < len(classes):
            topk_candidates.append((classes[idx], topk_prob[0, i].item()))
        else:
            print(f"警告: 预测索引 {idx} 超出类别列表")
    return topk_candidates


##########################################
# 主流程：训练与推理测试
##########################################
if __name__ == '__main__':
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if torch.cuda.is_available():
        print("PyTorch 正在使用 GPU")
    else:
        print("PyTorch 正在使用 CPU")

    # 加载数据集（确保路径正确、数据集格式符合要求）
    train_loader, val_loader, classes = get_dataloaders(
        "F:/data1/train",
        "F:/data1/val"
    )

    # 初始化模型并训练（训练代码可根据需要开启或注释）：
    model = load_model()
    print("模型分类头维度:", model.head.out_features)  # 应输出配置中的类别数，例如 36
    # # 训练模型并保存权重
    # trained_model = train_model(model, train_loader, val_loader, device)
    # torch.save(trained_model.state_dict(), "convit_mineral.pth")

    # 重新加载模型权重进行推理测试
    model = load_model().to(device)
    model.load_state_dict(torch.load("convit_mineral.pth", map_location=device))

    # 对测试图片进行分类，替换为实际存在的图片路径"C:\Users\郭倍宁\Desktop\18344_853_1309239624.jpg""C:\Users\郭倍宁\Desktop\hematite002.jpg"
    test_image_path = "C:/Users/郭倍宁/Desktop/53876856790.jpg"
    candidates = image_classification_module(test_image_path, model, classes, device, topk=3)
    print("Top-k 结果:", candidates)
