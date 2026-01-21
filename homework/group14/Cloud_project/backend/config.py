import os
from dotenv import load_dotenv

load_dotenv()

class AppConfig:
    # 1. 认证配置
    API_KEY = os.getenv("OPENAI_API_KEY")
    API_BASE = os.getenv("OPENAI_API_BASE")
    
    # 2. 模型配置
    CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "ecnu-plus")
    # ✅ 默认值修改为 ecnu-embedding-small
    EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "ecnu-embedding-small")
    
    # 3. 数据库配置
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

    @staticmethod
    def validate():
        if not AppConfig.API_KEY:
            raise ValueError("❌ 缺少 API Key，请检查 .env 文件")
        if not AppConfig.API_BASE:
            print("⚠️ 警告: 未配置 OPENAI_API_BASE，将默认连接官方 OpenAI")