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
import matplotlib.pyplot as plt

from modules.image_recognition.utils import get_transform
from modules.image_recognition import config

# 强制离线模式，确保不会联网下载
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_OFFLINE"] = "1"
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
##########################################
# EarlyStopping 类定义
##########################################
class EarlyStopping:
    """
    如果验证损失在连续 `patience` 个 epoch 内没有改善，则提前停止训练。
    """

    def __init__(self, patience=5, verbose=False, delta=0):
        self.patience = patience
        self.verbose = verbose
        self.delta = delta
        self.best_score = None
        self.counter = 0
        self.early_stop = False

    def __call__(self, val_loss):
        score = -val_loss
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
    local_model_path = "F:/pycharm/RAG/modules/convit_tiny"
    weight_file = os.path.join(local_model_path, "model.safetensors")
    if not os.path.exists(weight_file):
        raise FileNotFoundError(f"权重文件未找到: {weight_file}")

    model = timm.create_model(config.MODEL_NAME, pretrained=False, num_classes=1000)
    state_dict = load_file(weight_file)
    model.load_state_dict(state_dict)

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
    transform = get_transform()
    train_dataset = ImageFolder(root=train_dir, transform=transform)
    val_dataset = ImageFolder(root=val_dir, transform=transform)
    assert train_dataset.classes == val_dataset.classes, "训练集和验证集类别不一致！"
    assert len(train_dataset.classes) == config.NUM_CLASSES, \
        f"数据集类别数 ({len(train_dataset.classes)}) 不等于配置的 {config.NUM_CLASSES}"

    train_loader = DataLoader(train_dataset, batch_size=config.BATCH_SIZE, shuffle=True, num_workers=4)
    val_loader = DataLoader(val_dataset, batch_size=config.BATCH_SIZE, shuffle=False, num_workers=4)
    return train_loader, val_loader, train_dataset.classes

##########################################
# 训练与验证（含性能记录）
##########################################
def train_model(model, train_loader, val_loader, device):
    model = model.to(device)

    # 冻结预训练层，仅训练分类头
    for param in model.parameters():
        param.requires_grad = False
    for param in model.head.parameters():
        param.requires_grad = True

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.head.parameters(), lr=config.LEARNING_RATE)
    scheduler = CosineAnnealingLR(optimizer, T_max=config.NUM_EPOCHS)

    freeze_epochs = 3
    early_stopping = EarlyStopping(patience=5, verbose=True, delta=0.001)

    train_losses, val_losses, val_accuracies = [], [], []

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
        avg_train_loss = total_loss / len(train_loader)
        print(f"Epoch {epoch+1}/{config.NUM_EPOCHS}, 训练损失: {avg_train_loss:.4f}")
        train_losses.append(avg_train_loss)

        val_loss, val_acc = validate_model(model, val_loader, device)
        val_losses.append(val_loss)
        val_accuracies.append(val_acc)

        early_stopping(val_loss)
        if early_stopping.early_stop:
            print("早停触发，停止训练。")
            break

        if epoch + 1 == freeze_epochs:
            print("解冻所有层，进行联合微调")
            for param in model.parameters():
                param.requires_grad = True
            optimizer = optim.Adam(model.parameters(), lr=config.LEARNING_RATE / 10)
            scheduler = CosineAnnealingLR(optimizer, T_max=config.NUM_EPOCHS - freeze_epochs)

    # 绘制性能曲线
    epochs_range = range(1, len(train_losses) + 1)
    plt.figure()
    plt.plot(epochs_range, train_losses, label='训练损失')
    plt.plot(epochs_range, val_losses, label='验证损失')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.title('Loss 曲线')
    plt.legend()
    plt.show()

    plt.figure()
    plt.plot(epochs_range, val_accuracies, label='验证准确率')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.title('验证准确率曲线')
    plt.legend()
    plt.show()

    return model

##########################################
# 验证函数更新：返回准确率
##########################################
def validate_model(model, val_loader, device):
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
    return avg_loss, acc

##########################################
# 推理函数：对单张图片进行分类
##########################################
def image_classification_module(image_path, model, classes, device, topk=3):
    transform = get_transform()
    image = Image.open(image_path).convert("RGB")
    image_tensor = transform(image).unsqueeze(0).to(device)

    model.eval()
    with torch.no_grad():
        logits = model(image_tensor)
    probabilities = F.softmax(logits, dim=1)
    topk_prob, topk_idx = torch.topk(probabilities, k=topk, dim=1)

    candidates = []
    for i in range(topk):
        idx = topk_idx[0, i].item()
        candidates.append((classes[idx], topk_prob[0, i].item()))
    return candidates

##########################################
# 主流程：训练、保存、加载及推理测试
##########################################
if __name__ == '__main__':
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("PyTorch 正在使用 GPU" if torch.cuda.is_available() else "PyTorch 正在使用 CPU")

    # 数据路径
    train_dir = "F:/data1/train"
    val_dir = "F:/data1/val"

    # 加载数据集
    train_loader, val_loader, classes = get_dataloaders(train_dir, val_dir)

    # 初始化模型
    model = load_model()
    print("模型分类头维度:", model.head.out_features)

    # 训练模型并可视化性能曲线
    trained_model = train_model(model, train_loader, val_loader, device)

    # 保存训练后的权重
    torch.save(trained_model.state_dict(), "convit_mineral.pth")

    # 重新加载模型进行推理
    inference_model = load_model().to(device)
    inference_model.load_state_dict(torch.load("convit_mineral.pth", map_location=device))

    # 测试图片分类
    test_image_path = "C:/Users/郭倍宁/Desktop/53876856790.jpg"
    results = image_classification_module(test_image_path, inference_model, classes, device, topk=3)
    print("Top-k 结果:", results)
