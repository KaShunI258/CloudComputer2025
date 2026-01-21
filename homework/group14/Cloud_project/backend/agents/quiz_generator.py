import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from backend.agents.base_agent import BaseAgent

class QuizGenerator(BaseAgent):
    def generate_comprehensive_exam(self, context_text):
        """
        生成一套包含10道题目的完整试卷
        分布：6简单 + 3中等 + 1困难
        """
        # 如果上下文太长，稍微截断以防止 Token 溢出，但在生成10题时需要足够的信息
        if len(context_text) > 4000:
            context_text = context_text[:4000] + "..."

        prompt = ChatPromptTemplate.from_template("""
        你是一个专业的云计算课程出题专家。请基于以下[教学内容]，生成一套包含 **10道题目** 的完整试卷。
        
        [教学内容]:
        {context}
        
        [出题结构与要求]:
        请严格按照以下顺序和难度出题，并确保**题目考察的知识点尽量不重复**，覆盖面要广：
        
        1. **题目 1-6 (共6题)**: 
           - 类型: 单选题 (Choice)
           - 难度: 简单 (Easy)
           - 目标: 考察基本概念、定义和术语记忆。
           
        2. **题目 7-9 (共3题)**: 
           - 类型: 单选题 (Choice)
           - 难度: 中等 (Medium)
           - 目标: 考察概念对比、场景应用或简单计算。
           
        3. **题目 10 (共1题)**: 
           - 类型: 简答题 (Short Answer)
           - 难度: 困难 (Hard)
           - 目标: 考察综合理解、架构设计或优缺点深度分析。
        
        [输出格式]:
        请严格返回一个包含10个对象的JSON数组，不要包含Markdown代码块标记(```json)，直接输出JSON字符串。格式范例：
        [
            {{
                "id": 1,
                "type": "choice",
                "difficulty": "Easy",
                "question": "云计算的哪个特性...",
                "options": ["A. 按需自助", "B. 广泛网络接入", "C. ...", "D. ..."],
                "answer": "A",
                "knowledge_point": "云计算特征"
            }},
            ...
            {{
                "id": 10,
                "type": "short_answer",
                "difficulty": "Hard",
                "question": "请阐述...",
                "answer": "核心要点包括...",
                "knowledge_point": "架构设计"
            }}
        ]
        """)
        
        chain = prompt | self.llm | StrOutputParser()
        print("🧠 Agent 正在生成 10 道题目 (6简/3中/1难)...")
        
        try:
            response = chain.invoke({"context": context_text})
            # 数据清洗
            clean_json = response.replace("```json", "").replace("```", "").strip()
            quiz_list = json.loads(clean_json)
            
            # 简单的校验，确保生成了列表
            if isinstance(quiz_list, list):
                print(f"✅ 成功生成 {len(quiz_list)} 道题目")
                return quiz_list
            else:
                print("❌ 生成格式错误: 不是列表")
                return []
                
        except json.JSONDecodeError as e:
            print(f"❌ JSON 解析失败: {e}")
            print(f"原始返回片段: {response[:200]}...")
            return []
        except Exception as e:
            print(f"❌ 试卷生成未知错误: {e}")
            return []