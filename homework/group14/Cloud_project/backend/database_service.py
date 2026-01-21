import redis
from pymongo import MongoClient
from datetime import datetime
from backend.config import AppConfig

class DBManager:
    def __init__(self):
        # 连接 MongoDB
        self.mongo_client = MongoClient(AppConfig.MONGO_URI)
        self.db = self.mongo_client["study_agent_db"]
        self.exam_col = self.db["exam_records"]
        self.mistake_col = self.db["error_questions"]
        
        # 连接 Redis
        self.redis_client = redis.Redis(
            host=AppConfig.REDIS_HOST, 
            port=AppConfig.REDIS_PORT, 
            decode_responses=True
        )

    def save_exam_record(self, questions, user_answers, total_score, details):
            # ✅ 修复：将 user_answers 的 Key 转换为字符串 (MongoDB 不允许整数作为 Key)
            # 原始 user_answers 可能是 {1: "A", 2: "B"} -> 导致报错
            # 转换后 user_answers_str 为 {"1": "A", "2": "B"} -> MongoDB 支持
            user_answers_str = {str(k): v for k, v in user_answers.items()}

            record = {
                "timestamp": datetime.now(),
                "total_score": total_score,
                "questions": questions,
                "user_answers": user_answers_str, # 使用转换后的字典
                "grading_details": details
            }
            self.exam_col.insert_one(record)

    def add_mistake(self, question_data, user_ans, grading_result):
        existing = self.mistake_col.find_one({"question": question_data['question']})
        if existing:
            self.mistake_col.update_one(
                {"_id": existing["_id"]},
                {
                    "$inc": {"error_times": 1},
                    "$set": {"last_error_time": datetime.now(), "latest_feedback": grading_result['feedback']}
                }
            )
        else:
            record = {
                "question": question_data['question'],
                "type": question_data.get('type', 'choice'),
                "difficulty": question_data.get('difficulty', 'Unknown'),
                "standard_answer": question_data['answer'],
                "user_answer": user_ans,
                "analysis": grading_result.get('analysis', ''),
                "error_times": 1,
                "create_time": datetime.now(),
                "last_error_time": datetime.now()
            }
            self.mistake_col.insert_one(record)

    def get_mistakes(self):
        return list(self.mistake_col.find({}, {"_id": 0}).sort("error_times", -1))