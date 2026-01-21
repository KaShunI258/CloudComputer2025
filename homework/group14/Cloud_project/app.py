import streamlit as st
from backend.database_service import DBManager
from backend.rag_service import RAGService
from backend.agents.quiz_generator import QuizGenerator
from backend.agents.quiz_grader import QuizGrader

# 导入前端组件
from frontend.sidebar import render_sidebar
from frontend.exam_view import render_exam_page
from frontend.dashboard_view import render_dashboard

# 初始化 Session State
if 'db' not in st.session_state: 
    st.session_state.db = DBManager()
if 'kb' not in st.session_state: 
    st.session_state.kb = RAGService() # 注意：这里引用改名的服务
if 'generator' not in st.session_state: 
    st.session_state.generator = QuizGenerator()
if 'grader' not in st.session_state: 
    st.session_state.grader = QuizGrader()

# 页面配置
st.set_page_config(page_title="智能学习闭环系统", layout="wide")
st.title("📚 学习效果评估与巩固智能体 (Enterprise Edition)")

# 1. 渲染侧边栏
render_sidebar(st.session_state.kb)

# 2. 渲染主界面
tab1, tab2 = st.tabs(["📝 智能考核", "📊 错题仪表盘"])

with tab1:
    if st.session_state.get('file_ready'):
        render_exam_page(
            st.session_state.generator, 
            st.session_state.grader, 
            st.session_state.kb, 
            st.session_state.db
        )
    else:
        st.info("👈 请先在左侧上传学习资料")

with tab2:
    render_dashboard(st.session_state.db)