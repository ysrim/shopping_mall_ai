import streamlit as st
from features.shared.db import ChatDatabase
from features.shared.ui_utils import (
    handle_error,
    render_metric_grid,
    render_recent_chats,
    render_top_questions_table,
    render_category_card,
    display_rating
)
import pandas as pd


def show(db: ChatDatabase):
    st.title("📊 대시보드")

    # 탭 구성
    tab1, tab2, tab3 = st.tabs(["📈 전체 통계", "🔥 자주 받는 질문 TOP 10", "📋 카테고리별 분석"])

    # ==================== TAB 1: 전체 통계 ====================
    with tab1:
        st.subheader("📈 전체 통계")

        def get_stats():
            stats = db.get_statistics()
            print(f"📊 통계 조회: {stats}")
            return stats

        stats = handle_error(get_stats, error_message="통계 조회 실패")

        if stats:
            # 메트릭 그리드
            total_chats = stats.get('total_chats', 1)
            total_rated = stats.get('total_rated', 0)
            rated_percent = (total_rated / total_chats * 100) if total_chats > 0 else 0

            metrics = [
                {"label": "총 질문", "value": stats.get('total_chats', 0), "delta": None},
                {"label": "평가된 질문", "value": stats.get('total_rated', 0), "delta": f"{rated_percent:.1f}%"},
                {"label": "👍 좋은 평가", "value": stats.get('positive_count', 0), "delta": "만족도 높음"},
                {"label": "👎 나쁜 평가", "value": stats.get('negative_count', 0), "delta": "개선 필요"}
            ]
            render_metric_grid(metrics)

            st.divider()

            # 최근 대화 이력
            render_recent_chats(db, limit=10)

    # ==================== TAB 2: 자주 받는 질문 TOP 10 ====================
    with tab2:
        st.subheader("🔥 자주 받는 질문 TOP 10")

        def get_top_questions():
            top_questions = db.get_top_questions(limit=10)
            print(f"🔥 TOP 질문 조회: {len(top_questions) if top_questions else 0}개")
            return top_questions

        top_questions = handle_error(
            get_top_questions,
            error_message="TOP 질문 조회 실패"
        )

        if top_questions:
            render_top_questions_table(top_questions, show_download=True)
        else:
            st.info("⚠️ 아직 충분한 질문 이력이 없습니다. 더 많은 대화가 필요합니다.")

    # ==================== TAB 3: 카테고리별 분석 ====================
    with tab3:
        st.subheader("📋 카테고리별 분석")

        def get_category_stats():
            category_stats = db.get_category_stats()
            print(f"📋 카테고리 통계: {len(category_stats) if category_stats else 0}개 카테고리")
            return category_stats

        category_stats = handle_error(
            get_category_stats,
            error_message="카테고리 통계 조회 실패"
        )

        if category_stats:
            # 막대 그래프
            df_cat = pd.DataFrame(category_stats)
            st.write("**카테고리별 질문 수:**")
            st.bar_chart(df_cat.set_index('category')['total'], use_container_width=True)

            st.divider()

            st.write("**카테고리별 만족도 분석:**")
            for cat in category_stats:
                render_category_card(cat)

        else:
            st.info("⚠️ 아직 카테고리 데이터가 없습니다.")
