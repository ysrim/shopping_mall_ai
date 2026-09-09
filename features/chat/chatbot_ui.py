import streamlit as st
import time
from features.chat.chatbot_service import ChatbotService
from features.shared.ui_utils import (
    show_status_cards,
    render_chat_card,
    render_rating_buttons,
    handle_error
)


def show(service: ChatbotService, docs_loaded: bool, index_loaded: bool):
    st.title("💬 AI 쇼핑 어시스턴트")

    # ==================== 상태 표시 ====================
    show_status_cards(docs_loaded, index_loaded)

    # ==================== 문서 및 인덱스 체크 ====================
    if not show_status_cards(docs_loaded, index_loaded):
        st.stop()

    print("\n" + "=" * 60)
    print("📄 채팅 페이지 진입")
    print("=" * 60 + "\n")

    # ==================== Session State 초기화 ====================
    if "chat_response" not in st.session_state:
        st.session_state.chat_response = None
    if "show_response" not in st.session_state:
        st.session_state.show_response = False

    # ==================== 대화 히스토리 (맨 위) ====================
    st.subheader("📋 대화 히스토리 (최신순)")

    def load_history():
        chat_history = service.get_history()
        return list(reversed(chat_history)) if chat_history else []

    chat_history = handle_error(
        load_history,
        error_message="히스토리 로드 실패"
    )

    if chat_history:
        print(f"✅ 히스토리 로드 완료: {len(chat_history)}개\n")
        for chat in chat_history:
            render_chat_card(chat, service, show_buttons=True, show_delete=True)
    else:
        st.info("아직 대화가 없습니다.")
        print("ℹ️ 대화 히스토리가 비어있습니다")

    st.divider()

    # ==================== 사용자 입력 및 답변 (맨 아래) ====================
    st.subheader("💬 새로운 질문")

    user_input = st.chat_input("질문을 입력하세요...")

    if user_input:
        print(f"✅ 사용자 입력 감지: {user_input}\n")

        # 사용자 메시지 표시
        with st.chat_message("user"):
            st.write(user_input)

        # 로딩 중 표시
        print("⏳ 스핀 시작...")
        with st.spinner("⏳ 답변 요청 중..."):
            time.sleep(0.3)

            def process_input():
                return service.process_message(user_input)

            response = handle_error(
                process_input,
                error_message="메시지 처리 실패"
            )

            if response:
                st.session_state.chat_response = response
                st.session_state.show_response = True
                print(f"✅ process_message 완료: {response[:50] if response else 'None'}...\n")

    # Session State에서 응답 표시
    if st.session_state.show_response and st.session_state.chat_response:
        st.success("✅ 답변 완료!")

        with st.chat_message("assistant"):
            st.write(st.session_state.chat_response)

        # 평가 버튼
        st.subheader("이 답변이 도움이 되었나요?")
        render_rating_buttons(chat_id=-1, service=service, button_style="new")
