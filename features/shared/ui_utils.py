"""
UI 공용 유틸리티 모듈
중복되는 UI 컴포넌트와 함수를 중앙화
"""

import streamlit as st
import time
import traceback
from typing import Dict, Any, Callable, Optional, List
from datetime import datetime


# ==================== 1️⃣ 에러 처리 ====================

def handle_error(
    func: Callable,
    error_message: str = "오류가 발생했습니다.",
    show_traceback: bool = True,
    on_error: Optional[Callable] = None
) -> Any:
    """
    함수 실행 중 에러를 안전하게 처리

    Args:
        func: 실행할 함수
        error_message: 에러 메시지
        show_traceback: 트레이스백 표시 여부
        on_error: 에러 발생 시 콜백 함수

    Returns:
        함수 결과 또는 None
    """
    try:
        return func()
    except Exception as e:
        print(f"❌ {error_message}: {str(e)}")
        if show_traceback:
            import traceback
            print(traceback.format_exc())
        st.error(f"❌ {error_message}: {str(e)}")
        if on_error:
            on_error(e)
        return None


# ==================== 2️⃣ 평가 버튼 ====================

def render_rating_buttons(
    chat_id: int,
    service,
    button_style: str = "new"
) -> None:
    """
    평가 버튼 렌더링 (재사용 가능)

    Args:
        chat_id: 대화 ID
        service: ChatbotService 인스턴스
        button_style: 버튼 스타일 ("new" 또는 "history")
    """
    if button_style == "history":
        # 히스토리 페이지용 (작은 버튼)
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("👍", key=f"like_{chat_id}", help="좋음"):
                service.rate_message(chat_id, 1)
                st.rerun()
        with col2:
            if st.button("😐", key=f"neutral_{chat_id}", help="보통"):
                service.rate_message(chat_id, 0)
                st.rerun()
        with col3:
            if st.button("👎", key=f"dislike_{chat_id}", help="나쁨"):
                service.rate_message(chat_id, -1)
                st.rerun()
    else:
        # 새 답변용 (큰 버튼)
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("👍 도움됨", key="like_new"):
                history = service.get_history()
                if history:
                    latest_id = history[0]['id']
                    service.rate_message(latest_id, 1)
                    st.success("👍 평가가 저장되었습니다!")
                    st.session_state.show_response = False
                    time.sleep(1)
                    st.rerun()

        with col2:
            if st.button("😐 보통", key="neutral_new"):
                history = service.get_history()
                if history:
                    latest_id = history[0]['id']
                    service.rate_message(latest_id, 0)
                    st.info("😐 평가가 저장되었습니다!")
                    st.session_state.show_response = False
                    time.sleep(1)
                    st.rerun()

        with col3:
            if st.button("👎 도움안됨", key="dislike_new"):
                history = service.get_history()
                if history:
                    latest_id = history[0]['id']
                    service.rate_message(latest_id, -1)
                    st.warning("👎 평가가 저장되었습니다!")
                    st.session_state.show_response = False
                    time.sleep(1)
                    st.rerun()


def display_rating(rating: Optional[int]) -> str:
    """
    평가를 이모지로 표시

    Args:
        rating: 평가값 (1, 0, -1) 또는 None

    Returns:
        이모지 문자열
    """
    if rating == 1:
        return "👍 좋음"
    elif rating == -1:
        return "👎 나쁨"
    elif rating == 0:
        return "😐 보통"
    else:
        return "평가 안 함"


# ==================== 3️⃣ 대화 카드 렌더링 ====================

def render_chat_card(
    chat: Dict[str, Any],
    service,
    show_buttons: bool = True,
    show_delete: bool = True
) -> None:
    """
    대화 카드를 표준 형식으로 렌더링

    Args:
        chat: 대화 데이터 딕셔너리
        service: ChatbotService 인스턴스
        show_buttons: 평가 버튼 표시 여부
        show_delete: 삭제 버튼 표시 여부
    """
    with st.container(border=True):
        # 메인 콘텐츠
        col1, col2 = st.columns([9, 1] if show_delete else [10, 0])

        with col1:
            st.write(f"**👤 사용자:** {chat.get('user_message', 'N/A')[:100]}")
            st.write(f"**🤖 AI:** {chat.get('assistant_message', 'N/A')[:100]}")

            # 메타 정보
            meta_info = f"🏷️ {chat.get('category', 'N/A')} | {chat.get('timestamp', 'N/A')}"
            if chat.get('rating') is not None:
                meta_info += f" | {display_rating(chat['rating'])}"
            st.caption(meta_info)

        # 삭제 버튼
        if show_delete:
            with col2:
                if st.button("🗑️", key=f"delete_{chat['id']}", help="대화 삭제"):
                    service.delete_message(chat['id'])
                    st.info("삭제되었습니다.")
                    time.sleep(0.5)
                    st.rerun()

        # 평가 버튼
        if show_buttons and chat.get('rating') is None:
            st.divider()
            render_rating_buttons(chat['id'], service, button_style="history")


# ==================== 4️⃣ 상태 표시 ====================

def show_status_cards(docs_loaded: bool, index_loaded: bool) -> bool:
    """
    문서/인덱스 상태를 카드로 표시

    Args:
        docs_loaded: 문서 로드 여부
        index_loaded: 인덱스 생성 여부

    Returns:
        상태 정상 여부
    """
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"📄 문서: {'✅ 로드됨' if docs_loaded else '❌ 미로드'}")
    with col2:
        st.info(f"🔍 인덱스: {'✅ 생성됨' if index_loaded else '❌ 미생성'}")

    if not docs_loaded or not index_loaded:
        st.warning("⚠️ 먼저 설정 페이지에서 문서를 로드하고 인덱스를 생성해주세요.")
        return False
    return True


# ==================== 5️⃣ 메트릭 카드 ====================

def render_metric_grid(
    metrics: List[Dict[str, Any]],
    columns: int = 4
) -> None:
    """
    여러 메트릭을 그리드 형식으로 렌더링

    Args:
        metrics: 메트릭 리스트 [{"label": "총 질문", "value": 10, "delta": None}, ...]
        columns: 열 개수
    """
    cols = st.columns(columns)
    for idx, metric in enumerate(metrics):
        with cols[idx % columns]:
            st.metric(
                metric.get('label', 'N/A'),
                metric.get('value', 0),
                delta=metric.get('delta', None)
            )


# ==================== 6️⃣ 카테고리 카드 ====================

def render_category_card(category_data: Dict[str, Any]) -> None:
    """
    카테고리 통계를 카드로 렌더링

    Args:
        category_data: 카테고리 통계 데이터
    """
    with st.container(border=True):
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("카테고리", category_data['category'])

        with col2:
            st.metric("총 질문", int(category_data['total']))

        with col3:
            st.metric("👍 좋은평가", int(category_data['positive']))

        with col4:
            satisfaction = category_data.get('satisfaction_rate', 0) or 0
            st.metric("만족도", f"{satisfaction:.1f}%")


# ==================== 7️⃣ 데이터 다운로드 ====================

def render_download_button(
    data: List[Dict[str, Any]],
    filename: str = "data",
    file_format: str = "csv"
) -> None:
    """
    데이터 다운로드 버튼 렌더링

    Args:
        data: 다운로드할 데이터 (Dict 리스트)
        filename: 파일명 (timestamp 자동 추가)
        file_format: 파일 형식 ("csv" 또는 "json")
    """
    import pandas as pd
    import json

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    if file_format == "csv":
        df = pd.DataFrame(data)
        csv_data = df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 다운로드 (CSV)",
            data=csv_data,
            file_name=f"{filename}_{timestamp}.csv",
            mime="text/csv",
            key=f"download_{timestamp}"
        )
    elif file_format == "json":
        json_data = json.dumps(data, ensure_ascii=False, indent=2)
        st.download_button(
            label="📥 다운로드 (JSON)",
            data=json_data,
            file_name=f"{filename}_{timestamp}.json",
            mime="application/json",
            key=f"download_{timestamp}"
        )


# ==================== 8️⃣ 테이블 렌더링 ====================

def render_top_questions_table(
    questions: List[Dict[str, Any]],
    show_download: bool = True
) -> None:
    """
    자주 받는 질문 테이블 렌더링

    Args:
        questions: 질문 리스트
        show_download: 다운로드 버튼 표시 여부
    """
    if questions:
        st.write("**가장 자주 나오는 질문들:**")

        for idx, q in enumerate(questions, 1):
            with st.container(border=True):
                col1, col2, col3 = st.columns([2, 1, 1])

                with col1:
                    st.write(f"**#{idx}. {q['user_message'][:80]}**")
                    st.caption(f"🏷️ 카테고리: {q.get('category', 'N/A')}")

                with col2:
                    st.metric("질문 횟수", int(q['count']))

                with col3:
                    satisfaction = q.get('avg_satisfaction') or 0.5
                    if satisfaction >= 0.8:
                        st.write("⭐⭐⭐⭐⭐ 높음")
                    elif satisfaction >= 0.6:
                        st.write("⭐⭐⭐⭐ 보통")
                    elif satisfaction >= 0.4:
                        st.write("⭐⭐⭐ 낮음")
                    else:
                        st.write("⭐⭐ 매우낮음")

        if show_download:
            st.divider()
            st.write("**데이터 다운로드:**")
            render_download_button(questions, "top_questions", "csv")

    else:
        st.info("⚠️ 아직 충분한 질문 이력이 없습니다.")


# ==================== 9️⃣ 최근 대화 렌더링 ====================

def render_recent_chats(
    db,
    limit: int = 10
) -> None:
    """
    최근 대화 이력을 표준 형식으로 렌더링

    Args:
        db: ChatDatabase 인스턴스
        limit: 조회할 대화 수
    """
    st.subheader("💬 최근 대화 이력")

    def load_history():
        history = db.get_history(limit=limit)
        return list(reversed(history)) if history else []

    history = handle_error(
        load_history,
        error_message="최근 대화 조회 실패"
    )

    if history:
        for chat in history:
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.write(f"**Q:** {chat['user_message'][:100]}")
                    st.write(f"**A:** {chat['assistant_message'][:100]}...")
                    st.caption(f"🏷️ {chat.get('category', 'N/A')} | {chat.get('timestamp', 'N/A')}")

                with col2:
                    st.write(display_rating(chat.get('rating')))
    else:
        st.info("대화 이력이 없습니다.")


# ==================== 🔟 확인 다이얼로그 ====================

def show_confirmation_dialog(
    message: str,
    on_confirm: Callable,
    confirm_text: str = "확인",
    cancel_text: str = "취소"
) -> None:
    """
    확인 다이얼로그 표시

    Args:
        message: 확인 메시지
        on_confirm: 확인 시 실행할 함수
        confirm_text: 확인 버튼 텍스트
        cancel_text: 취소 버튼 텍스트
    """
    st.warning(f"⚠️ **{message}**")
    col1, col2 = st.columns(2)

    with col1:
        if st.button(f"✅ {confirm_text}"):
            on_confirm()

    with col2:
        if st.button(f"❌ {cancel_text}"):
            st.session_state.confirm_dialog = False
            st.rerun()
