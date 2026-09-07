import streamlit as st
from features.shared.db import ChatDatabase


def show(db: ChatDatabase):
    st.title("📊 대시보드")

    stats = db.get_statistics()

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("총 대화", stats['total_chats'])
    with col2:
        st.metric("평균 평가", f"{stats['avg_rating']:.2f}")
    with col3:
        st.metric("👍 좋음", stats['like_count'])
    with col4:
        st.metric("😐 보통", stats['neutral_count'])
    with col5:
        st.metric("👎 나쁨", stats['dislike_count'])

    st.divider()

    if st.button("모든 대화 삭제"):
        db.clear_history()
        st.success("삭제되었습니다.")
        st.rerun()
