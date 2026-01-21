import streamlit as st

def render_sidebar(knowledge_base):
    with st.sidebar:
        st.header("1. 资料摄入")
        input_type = st.radio("选择资料类型", ["PDF文档", "录音音频 (Beta)"])
        uploaded_file = st.file_uploader("上传文件", type=["pdf", "wav"])
        use_ocr = st.checkbox("启用视觉OCR (扫描件)", help="调用Vision模型")

        if uploaded_file and st.button("开始处理"):
            # 保存临时文件
            ext = ".pdf" if input_type == "PDF文档" else ".wav"
            file_path = f"temp_input{ext}"
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            with st.spinner("正在解析资料..."):
                ftype = "pdf" if input_type == "PDF文档" else "audio"
                n = knowledge_base.build_index(file_path, file_type=ftype, use_ocr=use_ocr)
                
                if n > 0:
                    st.success(f"解析成功！生成 {n} 个知识片段")
                    st.session_state.file_ready = True
                else:
                    st.error("解析失败")