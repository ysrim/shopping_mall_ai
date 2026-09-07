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

    # 사용자 입력 (맨 위)
    if docs_loaded and index_loaded:
        user_input = st.chat_input("질문을 입력하세요...")

        if user_input:
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

                # DB 저장
                st.session_state.db.save_chat(user_input, response)
                st.rerun()

            except Exception as e:
                st.error(f"오류 발생: {str(e)}")
    else:
        st.warning("먼저 설정 페이지에서 문서를 로드하고 인덱스를 생성해주세요.")
        st.stop()

    st.divider()

    # 채팅 히스토리 (맨 아래) - 오래된 것부터
    chat_history = st.session_state.db.get_chat_history()

    if not chat_history:
        st.info("아직 대화가 없습니다.")

    for chat in chat_history:
        with st.container(border=True):
            st.write(f"**사용자:** {chat['user_message']}")
            st.write(f"**AI:** {chat['assistant_message']}")

            # 평가 표시
            if chat['rating'] is not None:
                rating_emoji = {1: "👍", 0: "😐", -1: "👎"}.get(chat['rating'], "")
                st.caption(f"평가: {rating_emoji}")
            else:
                # 평가 버튼
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("👍", key=f"like_{chat['id']}"):
                        st.session_state.db.save_rating(chat['id'], 1)
                        st.success("평가 저장!")
                        st.rerun()
                with col2:
                    if st.button("😐", key=f"neutral_{chat['id']}"):
                        st.session_state.db.save_rating(chat['id'], 0)
                        st.success("평가 저장!")
                        st.rerun()
                with col3:
                    if st.button("👎", key=f"dislike_{chat['id']}"):
                        st.session_state.db.save_rating(chat['id'], -1)
                        st.success("평가 저장!")
                        st.rerun()
