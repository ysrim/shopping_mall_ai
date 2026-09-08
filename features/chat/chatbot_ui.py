import streamlit as st
from .chatbot_service import ChatbotService
import time


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

            # ✅ 스핀 아이콘 표시 (컨테이너 사용)
            status_placeholder = st.empty()
            result_placeholder = st.empty()

            try:
                with status_placeholder.container():
                    with st.spinner("⏳ 답변 요청 중..."):
                        # 응답 생성
                        response = service.process_message(user_input)
                        time.sleep(0.5)  # 스핀 아이콘이 보이도록 약간의 대기

                # ✅ 스핀 아이콘 제거 후 완료 메시지 표시
                status_placeholder.empty()

                with result_placeholder.container():
                    st.success("✅ 답변 완료!")
                    st.write(f"**AI:** {response}")

                st.rerun()

            except Exception as e:
                status_placeholder.empty()
                st.error(f"❌ 오류 발생: {str(e)}")
    else:
        st.warning("먼저 설정 페이지에서 문서를 로드하고 인덱스를 생성해주세요.")
        st.stop()

    st.divider()

    # 히스토리 로드 (에러 처리 개선)
    try:
        chat_history = service.get_history()

        if not chat_history:
            st.info("아직 대화가 없습니다.")
        else:
            st.subheader("📋 대화 히스토리")
            for chat in chat_history:
                with st.container(border=True):
                    st.write(f"**사용자:** {chat.get('user_message', 'N/A')}")
                    st.write(f"**AI:** {chat.get('assistant_message', 'N/A')}")

                    if chat.get('rating') is not None:
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
    except KeyError as e:
        st.error(f"❌ 히스토리 로드 오류: 데이터 형식이 맞지 않습니다 (누락된 필드: {str(e)})")
        st.info("설정 페이지에서 '히스토리 초기화'를 클릭하고 다시 시도해주세요.")
    except Exception as e:
        st.error(f"❌ 히스토리 로드 오류: {str(e)}")
