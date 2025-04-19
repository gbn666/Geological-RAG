# modules/image_recognition/utils.py

from torchvision import transforms

def get_transform():
    return transforms.Compose([
        # 随机裁剪和缩放，输出 224x224 图像
        transforms.RandomResizedCrop(224, scale=(0.8, 1.0), ratio=(0.9, 1.1)),
        # 随机水平翻转
        transforms.RandomHorizontalFlip(),
        # 随机旋转 - 最大旋转角度为 15 度
        transforms.RandomRotation(15),
        # 随机调整亮度、对比度和饱和度
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
        # 转换为 tensor
        transforms.ToTensor(),
        # 标准化
        transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
    ])
