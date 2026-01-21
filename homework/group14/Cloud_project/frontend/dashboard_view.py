import streamlit as st

def render_dashboard(db):
    st.header("3. 个性化错题本")
    if st.button("刷新错题数据"):
        mistakes = db.get_mistakes()
        if not mistakes:
            st.info("暂无错题记录")
        else:
            for m in mistakes:
                with st.container(border=True):
                    col_a, col_b = st.columns([3, 1])
                    with col_a:
                        st.markdown(f"**题目**: {m['question']}")
                        st.error(f"解析: {m['analysis']}")
                    with col_b:
                        st.metric("错误次数", m['error_times'])
                        st.caption(f"难度: {m['difficulty']}")