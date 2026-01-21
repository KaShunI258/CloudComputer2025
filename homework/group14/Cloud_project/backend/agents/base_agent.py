from langchain_openai import ChatOpenAI
from backend.config import AppConfig

class BaseAgent:
    def __init__(self, temperature=0.7):
        AppConfig.validate()
        print(f"🤖 初始化 Agent: {self.__class__.__name__} (Model: {AppConfig.CHAT_MODEL})")
        
        self.llm = ChatOpenAI(
            model=AppConfig.CHAT_MODEL,
            temperature=temperature,
            openai_api_key=AppConfig.API_KEY,
            openai_api_base=AppConfig.API_BASE,
            max_tokens=None
        )