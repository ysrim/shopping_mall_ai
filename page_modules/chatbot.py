import streamlit as st
from datetime import datetime
from modules.rag import RAGPipeline
from modules.db import ChatDatabase
from config import TEMPERATURE, MAX_TOKENS

st.markdown("# 💬 AI 쇼핑 어시스턴트")

# ============ Session State 초기화 ============
if "rag" not in st.session_state:
    st.session_state.rag = RAGPipeline()

if "db" not in st.session_state:
    st.session_state.db = ChatDatabase()

if "temperature" not in st.session_state:
    st.session_state.temperature = TEMPERATURE

if "max_tokens" not in st.session_state:
    st.session_state.max_tokens = MAX_TOKENS

if "rating_submitted" not in st.session_state:
    st.session_state.rating_submitted = {}

if "pending_rating" not in st.session_state:
    st.session_state.pending_rating = None


# ============ 확인 창 함수 ============
def show_rating_confirmation(chat_id, rating_value, rating_text):
    """평가 확인 창"""
    st.warning(f"**{rating_text}로 평가하시겠습니까?**")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ 확인", key=f"confirm_{chat_id}_{rating_value}", use_container_width=True):
            st.session_state.db.save_rating(chat_id, rating_value)
            st.session_state.rating_submitted[chat_id] = rating_value
            st.session_state.pending_rating = None
            st.success("✅ 평가 저장됨")
            st.rerun()

    with col2:
        if st.button("❌ 취소", key=f"cancel_{chat_id}_{rating_value}", use_container_width=True):
            st.session_state.pending_rating = None
            st.rerun()


# ============ 상태 정보 표시 ============
st.markdown("---")

col1, col2, col3 = st.columns(3)
with col1:
    st.success("✅ 문서 로드 완료") if st.session_state.documents_loaded else st.warning("⚠️ 문서 미로드")
with col2:
    st.success("✅ 인덱싱 완료") if st.session_state.index_loaded else st.warning("⚠️ 인덱싱 미완료")
with col3:
    st.info("⚙️ 설정은 우측 메뉴 '설정'에서")

st.markdown("---")

# ============ 채팅 히스토리 표시 ============
if st.session_state.chat_history:
    for chat_id, timestamp, user_msg, assistant_msg, rating in st.session_state.chat_history:
        # 채팅 컨테이너
        with st.container():
            # 사용자 메시지
            st.markdown(f"**👤 사용자**")
            st.markdown(f"> {user_msg}")

            # 어시스턴트 메시지
            st.markdown(f"**🤖 어시스턴트**")
            st.markdown(f"> {assistant_msg}")

            # 평가 섹션 (심플 UI)
            col1, col2, col3 = st.columns([1, 1, 1], gap="small")

            with col1:
                if st.button("👍", key=f"good_{chat_id}", use_container_width=True):
                    st.session_state.pending_rating = (chat_id, 1, "👍 도움됨")

            with col2:
                if st.button("😐", key=f"normal_{chat_id}", use_container_width=True):
                    st.session_state.pending_rating = (chat_id, 3, "😐 보통")

            with col3:
                if st.button("👎", key=f"bad_{chat_id}", use_container_width=True):
                    st.session_state.pending_rating = (chat_id, 5, "👎 도움 안됨")

            # 확인 창 표시
            if st.session_state.pending_rating and st.session_state.pending_rating[0] == chat_id:
                show_rating_confirmation(chat_id, st.session_state.pending_rating[1],
                                         st.session_state.pending_rating[2])

            # 평가 상태 표시
            if chat_id in st.session_state.rating_submitted:
                rating_val = st.session_state.rating_submitted[chat_id]
                rating_icon = "👍" if rating_val == 1 else "😐" if rating_val == 3 else "👎"
                st.caption(f"평가: {rating_icon}")
            elif rating:
                rating_icon = "👍" if rating == 1 else "😐" if rating == 3 else "👎"
                st.caption(f"평가: {rating_icon}")

            st.markdown("---")
else:
    st.info("아직 질문이 없습니다. 아래에 질문을 입력해주세요.")

# ============ 사용자 입력 ============
user_input = st.chat_input("질문을 입력하세요...")

if user_input:
    if not st.session_state.documents_loaded:
        st.warning("⚠️ 먼저 '설정' 메뉴에서 문서를 로드하세요")
    elif not st.session_state.index_loaded:
        st.warning("⚠️ 먼저 '설정' 메뉴에서 인덱싱을 완료하세요")
    else:
        with st.spinner("🤖 응답 생성 중..."):
            try:
                results = st.session_state.rag.search(user_input, top_k=3)
                prompt = st.session_state.rag.generate_prompt(user_input, results)
                response = st.session_state.rag.generate_response(
                    prompt,
                    temperature=st.session_state.temperature,
                    max_tokens=st.session_state.max_tokens
                )

                chat_id = st.session_state.db.save_chat(user_input, response)
                st.session_state.chat_history.append(
                    (chat_id, datetime.now().isoformat(), user_input, response, None)
                )

                # 응답 표시
                st.markdown(f"**👤 사용자**")
                st.markdown(f"> {user_input}")

                st.markdown(f"**🤖 어시스턴트**")
                st.markdown(f"> {response}")

                # 평가 버튼 (새 답변)
                st.markdown("**이 답변이 도움이 되었나요?**")
                col1, col2, col3 = st.columns([1, 1, 1], gap="small")

                with col1:
                    if st.button("👍", key=f"new_good_{chat_id}", use_container_width=True):
                        st.session_state.pending_rating = (chat_id, 1, "👍 도움됨")
                        st.rerun()

                with col2:
                    if st.button("😐", key=f"new_normal_{chat_id}", use_container_width=True):
                        st.session_state.pending_rating = (chat_id, 3, "😐 보통")
                        st.rerun()

                with col3:
                    if st.button("👎", key=f"new_bad_{chat_id}", use_container_width=True):
                        st.session_state.pending_rating = (chat_id, 5, "👎 도움 안됨")
                        st.rerun()

                # 확인 창 표시 (새 답변)
                if st.session_state.pending_rating and st.session_state.pending_rating[0] == chat_id:
                    show_rating_confirmation(chat_id, st.session_state.pending_rating[1],
                                             st.session_state.pending_rating[2])

            except Exception as e:
                st.error(f"❌ 오류: {e}")
                import traceback

                traceback.print_exc()
