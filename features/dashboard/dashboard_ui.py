import streamlit as st
from features.shared.db import ChatDatabase
from datetime import datetime
import pandas as pd


def show(db: ChatDatabase):
    st.title("📊 대시보드")

    # 탭 구성
    tab1, tab2, tab3 = st.tabs(["📈 전체 통계", "🔥 자주 받는 질문 TOP 10", "📋 카테고리별 분석"])

    # ==================== TAB 1: 전체 통계 ====================
    with tab1:
        st.subheader("📈 전체 통계")

        try:
            stats = db.get_statistics()
            print(f"📊 통계 조회: {stats}")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    "총 질문",
                    stats.get('total_chats', 0),
                    delta=None
                )

            with col2:
                total_chats = stats.get('total_chats', 1)
                total_rated = stats.get('total_rated', 0)
                rated_percent = (total_rated / total_chats * 100) if total_chats > 0 else 0
                st.metric(
                    "평가된 질문",
                    stats.get('total_rated', 0),
                    delta=f"{rated_percent:.1f}%"
                )

            with col3:
                st.metric(
                    "👍 좋은 평가",
                    stats.get('positive_count', 0),
                    delta=f"만족도 높음"
                )

            with col4:
                st.metric(
                    "👎 나쁜 평가",
                    stats.get('negative_count', 0),
                    delta=f"개선 필요"
                )

            st.divider()

            # 최근 대화 이력
            st.subheader("💬 최근 대화 이력")
            try:
                history = db.get_history(limit=10)
                history = list(reversed(history))

                if history:
                    for chat in history:
                        with st.container(border=True):
                            col1, col2 = st.columns([3, 1])

                            with col1:
                                st.write(f"**Q:** {chat['user_message'][:100]}")
                                st.write(f"**A:** {chat['assistant_message'][:100]}...")
                                st.caption(f"🏷️ {chat.get('category', 'N/A')} | {chat.get('timestamp', 'N/A')}")

                            with col2:
                                rating = chat.get('rating', 0)
                                if rating == 1:
                                    st.write("👍 좋음")
                                elif rating == -1:
                                    st.write("👎 나쁨")
                                else:
                                    st.write("😐 보통")
                else:
                    st.info("대화 이력이 없습니다.")

            except Exception as e:
                print(f"❌ 최근 대화 조회 실패: {e}")
                import traceback
                print(traceback.format_exc())
                st.error(f"❌ 최근 대화 조회 실패: {e}")

        except Exception as e:
            print(f"❌ 통계 조회 실패: {e}")
            import traceback
            print(traceback.format_exc())
            st.error(f"❌ 통계 조회 실패: {e}")

    # ==================== TAB 2: 자주 받는 질문 TOP 10 ====================
    with tab2:
        st.subheader("🔥 자주 받는 질문 TOP 10")

        try:
            top_questions = db.get_top_questions(limit=10)
            print(f"🔥 TOP 질문 조회: {len(top_questions)}개")

            if top_questions:
                # 테이블 형식으로 표시
                st.write("**가장 자주 나오는 질문들:**")

                for idx, q in enumerate(top_questions, 1):
                    with st.container(border=True):
                        col1, col2, col3 = st.columns([2, 1, 1])

                        with col1:
                            st.write(f"**#{idx}. {q['user_message'][:80]}**")
                            st.caption(f"🏷️ 카테고리: {q.get('category', 'N/A')}")

                        with col2:
                            st.metric("질문 횟수", int(q['count']))

                        with col3:
                            # None 체크 추가
                            satisfaction = q.get('avg_satisfaction')
                            if satisfaction is None:
                                satisfaction = 0.5

                            if satisfaction >= 0.8:
                                st.write("⭐⭐⭐⭐⭐ 높음")
                            elif satisfaction >= 0.6:
                                st.write("⭐⭐⭐⭐ 보통")
                            elif satisfaction >= 0.4:
                                st.write("⭐⭐⭐ 낮음")
                            else:
                                st.write("⭐⭐ 매우낮음")

                # 다운로드 버튼
                st.divider()
                st.write("**데이터 다운로드:**")

                # CSV 형식으로 변환
                df = pd.DataFrame(top_questions)
                csv_data = df.to_csv(index=False, encoding='utf-8-sig')

                st.download_button(
                    label="📥 TOP 10 다운로드 (CSV)",
                    data=csv_data,
                    file_name=f"top_questions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    key="download_top_questions"
                )

            else:
                st.info("⚠️ 아직 충분한 질문 이력이 없습니다. 더 많은 대화가 필요합니다.")

        except Exception as e:
            print(f"❌ TOP 질문 조회 실패: {e}")
            import traceback
            print(traceback.format_exc())
            st.error(f"❌ TOP 질문 조회 실패: {e}")

    # ==================== TAB 3: 카테고리별 분석 ====================
    with tab3:
        st.subheader("📋 카테고리별 분석")

        try:
            category_stats = db.get_category_stats()
            print(f"📋 카테고리 통계: {len(category_stats)}개 카테고리")

            if category_stats:
                # 막대 그래프
                df_cat = pd.DataFrame(category_stats)

                st.write("**카테고리별 질문 수:**")
                st.bar_chart(df_cat.set_index('category')['total'], use_container_width=True)

                st.divider()

                st.write("**카테고리별 만족도 분석:**")

                for cat in category_stats:
                    with st.container(border=True):
                        col1, col2, col3, col4 = st.columns(4)

                        with col1:
                            st.metric("카테고리", cat['category'])

                        with col2:
                            st.metric("총 질문", int(cat['total']))

                        with col3:
                            st.metric("👍 좋은평가", int(cat['positive']))

                        with col4:
                            satisfaction = cat.get('satisfaction_rate', 0)
                            if satisfaction is None:
                                satisfaction = 0
                            st.metric("만족도", f"{satisfaction:.1f}%")

            else:
                st.info("⚠️ 아직 카테고리 데이터가 없습니다.")

        except Exception as e:
            print(f"❌ 카테고리 통계 조회 실패: {e}")
            import traceback
            print(traceback.format_exc())
            st.error(f"❌ 카테고리 통계 조회 실패: {e}")
