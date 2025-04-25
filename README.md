**# 多模态地质矿物智能问答系统**  
集成图像识别、文本处理、知识图谱与大模型推理的多模态问答平台，专为矿物岩石分析与地质知识查询设计。  

---

## 🎯 项目概述
- **目标**：为地质学家、学生和爱好者提供一个可上传岩石/矿物图片并提出自然语言问题的智能问答系统。  
- **核心能力**：  
  1. 图像识别：ConViT 预训练模型微调，实现矿物分类。  
  2. 文本处理：BERT 提取用户提问特征，生成语义摘要。  
  3. 知识图谱：基于 Neo4j 存储与查询矿物属性与关系。  
  4. LLM 推理：调用 DeepSeek API（或其他大模型），结合多模态信息给出高质量回答。  
  5. 会话管理：支持注册/登录、会话上下文、多轮对话与新会话切换。  

## ✨ 主要功能
- 用户**注册**/登录 并获取 JWT Token；  
- 可选**上传图片** 或纯文本提问；  
- 图像识别候选 Top‑k 矿物，并自动从知识图谱补充背景信息；  
- 文本特征摘要及深度融合 Prompt 构造；  
- 调用 LLM 完成答案生成并可连续追问；  
- Flask RESTful API 封装，前端可快速集成；  
- MySQL 存储用户、会话、上传记录与问答日志；  

## 🏗️ 系统架构
```
[Web/Client]
     ↓ REST API (JWT)
   [Flask 后端]
     ├── Auth（用户注册/登录）
     ├── Upload（图片接收）
     ├── Session（会话管理）
     ├── Chat  （多模态问答）
     │     ├─ 图像模块 → ConViT 微调模型
     │     ├─ 文本模块 → BERT 特征提取
     │     ├─ KG 模块   → Neo4j 查询
     │     └─ LLM 模块  → DeepSeek API
     └── 数据库（MySQL）

[MySQL]    [Neo4j]    [Model Weights]
```

## 🛠️ 技术栈
- **后端框架**：Flask + Flask‑SQLAlchemy + Flask‑JWT‑Extended  
- **图像识别**：PyTorch + timm(convit_tiny) + safetensors  
- **文本处理**：Transformers(BERT)  
- **知识图谱**：Neo4j (Bolt), py2neo  
- **LLM 推理**：DeepSeek API（基于 OpenAI SDK）  
- **数据库**：MySQL (用户 & 会话 & 日志)  
- **环境管理**：venv / pip  

## ⚙️ 环境搭建指南
1. **克隆仓库**  
   ```bash
   git clone <仓库地址>
   cd <项目目录>
   ```
2. **创建虚拟环境 & 安装依赖**  
   ```bash
   python -m venv .venv
   source .venv/bin/activate     # Linux/macOS
   .\.venv\Scripts\activate    # Windows
   pip install -r requirements.txt
   ```
3. **配置环境变量**  
   创建 `.env`：
   ```ini
   FLASK_APP=app.py
   FLASK_ENV=development
   JWT_SECRET_KEY=your_jwt_secret
   MYSQL_URI=mysql://user:pass@host/dbname
   NEO4J_URI=bolt://host:7687
   NEO4J_USER=neo4j
   NEO4J_PASS=yourpassword
   DEEPSEEK_API_KEY=sk-xxxxx
   ```
4. **初始化数据库**  
   ```bash
   flask db upgrade    # 或者在 app.py 中触发 create_all()
   ```
5. **下载预训练模型权重**  
   - 手动下载 `convit_tiny` safetensors 权重到 `models/convit_tiny/`  
   - 准备 BERT 本地缓存目录：`models/bert-base-uncased/`  

## 🚀 启动服务
```bash
flask run --host=0.0.0.0 --port=5000
```

## 🔍 API 文档
| 名称         | 方法 | URL                                   | Auth    | 请求示例                                 | 返回示例                             | 说明                                    |
|--------------|------|---------------------------------------|---------|------------------------------------------|--------------------------------------|-----------------------------------------|
| 用户注册     | POST | `/api/auth/register`                  | 无      | `{username,email,password}`             | `{msg: "注册成功"}`                 | 注册新用户                               |
| 用户登录     | POST | `/api/auth/login`                     | 无      | `{username,password}`                   | `{access_token,expires_in}`          | 登录并获取 JWT                          |
| 当前用户     | GET  | `/api/auth/me`                        | Bearer  | Header: Authorization: Bearer <token>   | `{id,username,email}`                | 获取登录用户信息                         |
| 新建会话     | POST | `/api/session/new`                   | Bearer  | `{user_id}`                             | `{session_id}`                       | 创建新会话                               |
| 上传图片     | POST | `/api/upload`                         | Bearer  | FormData `file`                         | `{image_path}`                       | 上传并保存图片                           |
| 多模态问答   | POST | `/api/session/<id>/chat`             | Bearer  | `{question,image_path?}`                | `{answer,kg_candidates}`             | 图像/纯文本问答，多轮上下文管理           |

詳見 [API 文档](docs/API.md)。

## 📂 项目结构
```
├── app.py                  # Flask 应用入口
├── modules/                # 各功能模块
│   ├── image_recognition/  # 图像分类
│   ├── text_processing/    # 文本特征提取
│   ├── kg_query/           # 知识图谱查询
│   └── llm_inference/      # LLM 调用
├── models/                 # 预训练模型权重目录
├── uploads/                # 用户上传图片存储
├── migrations/             # 数据库迁移脚本
├── requirements.txt        # Python 依赖
└── README.md               # 项目说明（本文件）
```

## 🤝 贡献与许可
欢迎提交 Issue／PR，或在邮件列表讨论。  
**License:** MIT

