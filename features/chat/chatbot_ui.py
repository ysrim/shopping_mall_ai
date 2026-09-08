import streamlit as st
import time
from features.chat.chatbot_service import ChatbotService


def show(service: ChatbotService, docs_loaded: bool, index_loaded: bool):
    st.title("💬 AI 쇼핑 어시스턴트")

    # ==================== 상태 표시 ====================
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"📄 문서: {'✅ 로드됨' if docs_loaded else '❌ 미로드'}")
    with col2:
        st.info(f"🔍 인덱스: {'✅ 생성됨' if index_loaded else '❌ 미생성'}")

    st.divider()

    # ==================== 문서 및 인덱스 체크 ====================
    if not docs_loaded or not index_loaded:
        st.warning("⚠️ 먼저 설정 페이지에서 문서를 로드하고 인덱스를 생성해주세요.")
        st.stop()

    # ==================== 사용자 입력 ====================
    print("\n" + "=" * 60)
    print("📄 채팅 페이지 진입")
    print("=" * 60 + "\n")

    user_input = st.chat_input("질문을 입력하세요...")

    print(f"🔍 chat_input 값: {user_input}")

    if user_input:
        print(f"✅ 사용자 입력 감지: {user_input}\n")

        # 사용자 메시지 표시
        with st.chat_message("user"):
            st.write(user_input)

        # 로딩 중 표시
        print("⏳ 스핀 시작...")
        with st.spinner("⏳ 답변 요청 중..."):
            time.sleep(0.3)  # UI 렌더링 보장

            try:
                print("🔄 process_message 호출 중...")
                response = service.process_message(user_input)
                print(f"✅ process_message 완료: {response[:50] if response else 'None'}...\n")

            except Exception as e:
                print(f"❌ process_message 오류: {str(e)}")
                import traceback
                print(traceback.format_exc())
                st.error(f"❌ 오류 발생: {str(e)}")
                st.stop()

        # 응답 표시
        print("✅ 완료 메시지 표시 중...")
        st.success("✅ 답변 완료!")

        with st.chat_message("assistant"):
            st.write(response)

        # 평가 버튼
        st.subheader("이 답변이 도움이 되었나요?")
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("👍 도움됨", key="like_new"):
                # 최신 대화 ID 찾기
                history = service.get_history()
                if history:
                    latest_id = history[0]['id']
                    service.rate_message(latest_id, 1)
                    st.success("👍 평가가 저장되었습니다!")
                    time.sleep(1)
                    st.rerun()

        with col2:
            if st.button("😐 보통", key="neutral_new"):
                history = service.get_history()
                if history:
                    latest_id = history[0]['id']
                    service.rate_message(latest_id, 0)
                    st.info("😐 평가가 저장되었습니다!")
                    time.sleep(1)
                    st.rerun()

        with col3:
            if st.button("👎 도움안됨", key="dislike_new"):
                history = service.get_history()
                if history:
                    latest_id = history[0]['id']
                    service.rate_message(latest_id, -1)
                    st.warning("👎 평가가 저장되었습니다!")
                    time.sleep(1)
                    st.rerun()

    st.divider()

    # ==================== 대화 히스토리 ====================
    try:
        print("\n📋 히스토리 로드 중...")
        chat_history = service.get_history()

        if not chat_history:
            st.info("아직 대화가 없습니다.")
            print("ℹ️ 대화 히스토리가 비어있습니다")
        else:
            st.subheader("📋 대화 히스토리")
            print(f"✅ 히스토리 로드 완료: {len(chat_history)}개\n")

            for chat in chat_history:
                with st.container(border=True):
                    # 대화 내용 표시
                    col1, col2 = st.columns([9, 1])

                    with col1:
                        st.write(f"**👤 사용자:** {chat.get('user_message', 'N/A')}")
                        st.write(f"**🤖 AI:** {chat.get('assistant_message', 'N/A')}")

                    with col2:
                        # 삭제 버튼
                        if st.button("🗑️", key=f"delete_{chat['id']}", help="대화 삭제"):
                            service.delete_message(chat['id'])
                            st.info("삭제되었습니다.")
                            time.sleep(0.5)
                            st.rerun()

                    # 평가 표시
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

    except Exception as e:
        print(f"❌ 히스토리 로드 오류: {str(e)}")
        import traceback
        print(traceback.format_exc())
        st.warning(f"⚠️ 히스토리 로드 중 오류 발생: {str(e)}")
