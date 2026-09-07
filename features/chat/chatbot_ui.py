import streamlit as st
from .chatbot_service import ChatbotService


def show(service: ChatbotService, docs_loaded: bool, index_loaded: bool):
    st.title("💬 AI 쇼핑 어시스턴트")

    # 상태 표시
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"📄 문서: {'✅ 로드됨' if docs_loaded else '❌ 미로드'}")
    with col2:
        st.info(f"🔍 인덱스: {'✅ 생성됨' if index_loaded else '❌ 미생성'}")

    st.divider()

    # 사용자 입력
    if docs_loaded and index_loaded:
        user_input = st.chat_input("질문을 입력하세요...")

        if user_input:
            st.write(f"**사용자:** {user_input}")

            try:
                with st.spinner("답변 생성 중..."):
                    response = service.process_message(user_input)
                st.write(f"**AI:** {response}")
                st.rerun()
            except Exception as e:
                st.error(f"오류 발생: {str(e)}")
    else:
        st.warning("먼저 설정 페이지에서 문서를 로드하고 인덱스를 생성해주세요.")
        st.stop()

    st.divider()

    # 히스토리
    chat_history = service.get_history()

    if not chat_history:
        st.info("아직 대화가 없습니다.")

    for chat in chat_history:
        with st.container(border=True):
            st.write(f"**사용자:** {chat['user_message']}")
            st.write(f"**AI:** {chat['assistant_message']}")

            if chat['rating'] is not None:
                rating_emoji = {1: "👍", 0: "😐", -1: "👎"}.get(chat['rating'], "")
                st.caption(f"평가: {rating_emoji}")
            else:
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("👍", key=f"like_{chat['id']}"):
                        service.rate_message(chat['id'], 1)
                        st.rerun()
                with col2:
                    if st.button("😐", key=f"neutral_{chat['id']}"):
                        service.rate_message(chat['id'], 0)
                        st.rerun()
                with col3:
                    if st.button("👎", key=f"dislike_{chat['id']}"):
                        service.rate_message(chat['id'], -1)
                        st.rerun()
