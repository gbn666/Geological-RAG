from dotenv import load_dotenv
import os
# 配置上传文件夹路径
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')  # 上传的文件将保存在当前目录下的 'uploads' 文件夹
load_dotenv()  # 加载 .env 文件
class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("MYSQL_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    TRAIN_DIR = os.getenv("TRAIN_DIR")
    VAL_DIR = os.getenv("VAL_DIR")
    IMG_MODEL_PATH = os.getenv("IMG_MODEL_PATH")

    UPLOAD_FOLDER = UPLOAD_FOLDER
