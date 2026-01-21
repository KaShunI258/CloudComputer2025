import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

# ❌ 删除本地模型引用: from langchain_huggingface import HuggingFaceEmbeddings
# ✅ 换回 OpenAI 兼容接口
from langchain_openai import OpenAIEmbeddings

# 引入摄入服务
from backend.ingestion_service import IngestionService
# 引入配置
from backend.config import AppConfig

class RAGService:
    def __init__(self):
        # 1. 加载 Embedding 模型 (远程 API)
        print(f"🔄 连接远程 Embedding 模型: {AppConfig.EMBEDDING_MODEL} ...")
        print(f"   API Base: {AppConfig.API_BASE}")
        
        # ✅ 使用 OpenAIEmbeddings 调用 ECNU 接口
        self.embeddings = OpenAIEmbeddings(
            model=AppConfig.EMBEDDING_MODEL,      # ecnu-embedding-small
            openai_api_key=AppConfig.API_KEY,     # 你的 API Key
            openai_api_base=AppConfig.API_BASE,   # ECNU API 地址
            check_embedding_ctx_length=False      # 关键：关闭本地 token 检查，防止报错
        )
        
        self.vector_store = None
        
        # 2. 初始化切分器
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=600, 
            chunk_overlap=100
        )
        
        # 3. 初始化多模态摄入服务
        self.ingestion = IngestionService()

    def build_index(self, file_path, file_type="pdf", use_ocr=False):
        """
        构建知识库索引 (支持 PDF 和 Audio)
        """
        docs = []
        
        # A. 根据类型调用摄入服务
        if file_type == "pdf":
            print(f"📄 开始解析 PDF: {file_path} (OCR={use_ocr})")
            docs = self.ingestion.process_pdf(file_path, use_ocr=use_ocr)
            
        elif file_type == "audio":
            print(f"🔊 开始解析录音: {file_path}")
            text = self.ingestion.process_audio(file_path)
            if text:
                docs = [Document(page_content=text, metadata={"source": file_path, "type": "audio"})]

        # B. 数据清洗
        valid_docs = [d for d in docs if d.page_content and d.page_content.strip()]
        
        if not valid_docs:
            print("⚠️ 未提取到有效文本，跳过索引构建。")
            return 0
            
        # C. 文本切分
        splits = self.text_splitter.split_documents(valid_docs)
        print(f"✂️ 文本切分完成，共 {len(splits)} 个片段。")
        
        if not splits:
            return 0

        # D. 向量化并建立索引 (远程 API)
        try:
            print(f"🚀 正在调用 API ({AppConfig.EMBEDDING_MODEL}) 构建向量索引...")
            # 这一步会发起网络请求
            self.vector_store = FAISS.from_documents(splits, self.embeddings)
            print("✅ 索引构建成功！")
            return len(splits)
        except Exception as e:
            print(f"❌ 向量化失败 (请检查 API Key 或 网络): {e}")
            # 抛出异常以便前端捕获
            raise e

    def retrieve_relevant_content(self, query, k=3):
        """
        根据 Query 检索相关背景知识
        """
        if not self.vector_store:
            return ""
        
        try:
            # 相似度搜索 (也会调用 API 将 query 向量化)
            docs = self.vector_store.similarity_search(query, k=k)
            context = "\n\n".join([d.page_content for d in docs])
            return context
        except Exception as e:
            print(f"❌ 检索失败: {e}")
            return ""