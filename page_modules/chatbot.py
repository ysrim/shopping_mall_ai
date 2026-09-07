import streamlit as st
from modules.api import GeminiAPI
from modules.db import ChatDatabase
from modules.rag import RAGPipeline
from modules.state_manager import StateManager


def show():
    st.title("💬 AI 쇼핑 어시스턴트")

    # 초기화
    if "rag" not in st.session_state:
        st.session_state.rag = RAGPipeline()
    if "api" not in st.session_state:
        st.session_state.api = GeminiAPI()
    if "db" not in st.session_state:
        st.session_state.db = ChatDatabase()
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    state = StateManager()
    docs_loaded = state.load_state().get("documents_loaded", False)
    index_loaded = state.load_state().get("index_loaded", False)

    # 상태 표시
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"📄 문서: {'✅ 로드됨' if docs_loaded else '❌ 미로드'}")
    with col2:
        st.info(f"🔍 인덱스: {'✅ 생성됨' if index_loaded else '❌ 미생성'}")

    st.divider()

    # 채팅 히스토리 표시
    st.session_state.chat_history = st.session_state.db.get_chat_history()

    for chat in st.session_state.chat_history:
        with st.container(border=True):
            st.write(f"**사용자:** {chat['user_message']}")
            st.write(f"**AI:** {chat['assistant_message']}")

            if chat['rating']:
                rating_text = {1: "👍 좋음", 0: "😐 보통", -1: "👎 나쁨"}.get(chat['rating'], "평가 없음")
                st.caption(f"평가: {rating_text}")
            else:
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("👍", key=f"like_{chat['id']}"):
                        st.session_state.db.save_rating(chat['id'], 1)
                        st.rerun()
                with col2:
                    if st.button("😐", key=f"neutral_{chat['id']}"):
                        st.session_state.db.save_rating(chat['id'], 0)
                        st.rerun()
                with col3:
                    if st.button("👎", key=f"dislike_{chat['id']}"):
                        st.session_state.db.save_rating(chat['id'], -1)
                        st.rerun()

    st.divider()

    # 사용자 입력
    if docs_loaded and index_loaded:
        user_input = st.chat_input("질문을 입력하세요...")

        if user_input:
            st.write(f"**사용자:** {user_input}")

            try:
                # RAG 검색
                results = st.session_state.rag.retrieve(user_input, top_k=3)
                context = "\n".join([r["content"] for r in results]) if results else "문서에서 관련 정보를 찾을 수 없습니다."

                # 프롬프트 작성
                prompt = f"""다음은 쇼핑몰 정책 문서입니다:

{context}

사용자 질문: {user_input}

위의 문서를 참고하여 친절하게 답변해주세요."""

                # 응답 생성
                response = st.session_state.api.generate(prompt)
                st.write(f"**AI:** {response}")

                # DB 저장
                chat_id = st.session_state.db.save_chat(user_input, response)
                st.rerun()

            except Exception as e:
                st.error(f"오류 발생: {str(e)}")
    else:
        st.warning("먼저 설정 페이지에서 문서를 로드하고 인덱스를 생성해주세요.")
