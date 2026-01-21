import streamlit as st

def render_exam_page(agent_generator, agent_grader, knowledge_base, db):
    st.header("2. 智能考核 (梯度试卷)")
    
    # 生成试卷按钮
    if st.button("生成一套梯度试卷 (基础/进阶/挑战)"):
        with st.spinner("正在分析考点并出题..."):
            context = knowledge_base.retrieve_relevant_content("核心考点 summarize")
            quiz_list = agent_generator.generate_comprehensive_exam(context)
            if quiz_list:
                st.session_state.current_exam = quiz_list
                st.session_state.user_answers = {}
                st.session_state.exam_submitted = False
            else:
                st.error("出题失败")

    # 渲染试卷表单
    if 'current_exam' in st.session_state:
        exam = st.session_state.current_exam
        with st.form("exam_form"):
            for q in exam:
                st.markdown(f"**[{q['difficulty']}] 第 {q['id']} 题 ({q['type']})**")
                st.write(q['question'])
                if q['type'] == 'choice':
                    st.session_state.user_answers[q['id']] = st.radio(
                        f"请选择 (Q{q['id']}):", q['options'], key=f"q_{q['id']}"
                    )
                else:
                    st.session_state.user_answers[q['id']] = st.text_area(
                        f"请输入答案 (Q{q['id']}):", key=f"q_{q['id']}"
                    )
                st.markdown("---")
            
            if st.form_submit_button("提交试卷"):
                _handle_submission(exam, agent_grader, knowledge_base, db)

    # 结果展示
    if st.session_state.get('exam_submitted'):
        _render_results()

def _handle_submission(exam, grader, kb, db):
    st.session_state.exam_submitted = True
    st.session_state.grading_results = []
    total_score = 0
    
    for q in exam:
        u_ans = st.session_state.user_answers.get(q['id'], "")
        res = grader.grade_submission(
            q['type'], q['question'], q['answer'], u_ans, 
            kb.retrieve_relevant_content(q['question'])
        )
        res['id'] = q['id']
        res['user_ans'] = u_ans
        st.session_state.grading_results.append(res)
        total_score += res['score']
        
        if res['score'] < 6:
            db.add_mistake(q, u_ans, res)
            
    st.session_state.total_score = total_score
    db.save_exam_record(exam, st.session_state.user_answers, total_score, st.session_state.grading_results)

def _render_results():
    st.divider()
    st.subheader(f"📊 判卷报告 (总分: {st.session_state.total_score})")
    for res in st.session_state.grading_results:
        color = "green" if res['score'] >= 8 else "red"
        with st.expander(f"第 {res['id']} 题得分: :{color}[{res['score']}] - {res['feedback']}"):
            st.write(f"**你的回答**: {res['user_ans']}")
            st.write(f"**深度解析**: {res['analysis']}")