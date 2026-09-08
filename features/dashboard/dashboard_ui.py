import streamlit as st
from features.shared.db import ChatDatabase
import pandas as pd


def show(db: ChatDatabase):
    st.title("📊 대시보드")

    try:
        print("\n" + "=" * 60)
        print("📊 대시보드 페이지 진입")
        print("=" * 60 + "\n")

        # 통계 조회
        print("📊 통계 조회 중...")
        stats = db.get_statistics()
        print(f"통계 데이터: {stats}\n")

        if not stats or stats.get('total_chats', 0) == 0:
            st.info("📭 아직 대화가 없습니다. 채팅 페이지에서 시작해보세요!")
            return

        # ==================== 상단 메트릭 ====================
        st.subheader("📈 주요 통계")
        col1, col2, col3 = st.columns(3)

        with col1:
            total_chats = stats.get('total_chats', 0)
            st.metric("총 대화 수", total_chats)
            print(f"✅ 총 대화 수: {total_chats}")

        with col2:
            rating_stats = stats.get('rating_stats', {})
            positive_count = rating_stats.get(1, 0)
            st.metric("👍 좋은 평가", positive_count)
            print(f"✅ 좋은 평가: {positive_count}")

        with col3:
            # 평가율 계산
            total_rated = sum(rating_stats.values())
            if total_chats > 0:
                rating_rate = (total_rated / total_chats) * 100
            else:
                rating_rate = 0
            st.metric("⭐ 평가율", f"{rating_rate:.1f}%")
            print(f"✅ 평가율: {rating_rate:.1f}%")

        st.divider()

        # ==================== 평가 분포 ====================
        st.subheader("⭐ 평가 분포")

        rating_stats = stats.get('rating_stats', {})

        if rating_stats:
            # 데이터 준비
            rating_labels = {1: "👍 좋음", 0: "😐 보통", -1: "👎 나쁨"}
            rating_data = {
                rating_labels.get(k, f"평가 {k}"): v
                for k, v in rating_stats.items()
            }

            print(f"평가 분포: {rating_data}")

            # 막대 그래프
            col1, col2 = st.columns([2, 1])

            with col1:
                st.bar_chart(pd.Series(rating_data))

            with col2:
                st.write("**평가 통계:**")
                for label, count in rating_data.items():
                    st.write(f"{label}: {count}건")
        else:
            st.info("아직 평가 데이터가 없습니다.")

        st.divider()

        # ==================== 카테고리 분포 ====================
        st.subheader("📂 카테고리 분포")

        category_stats = stats.get('category_stats', {})

        if category_stats:
            print(f"카테고리 분포: {category_stats}")

            # 카테고리 번역
            category_names = {
                'shipping': '🚚 배송',
                'return': '↩️ 반품/환불',
                'payment': '💳 결제',
                'product': '📦 상품',
                'account': '👤 계정',
                'general': '❓ 기타'
            }

            category_data = {
                category_names.get(k, k): v
                for k, v in category_stats.items()
            }

            # 파이 차트
            col1, col2 = st.columns([2, 1])

            with col1:
                st.bar_chart(pd.Series(category_data))

            with col2:
                st.write("**카테고리별 건수:**")
                for category, count in category_data.items():
                    st.write(f"{category}: {count}건")
        else:
            st.info("아직 카테고리 데이터가 없습니다.")

        st.divider()

        # ==================== 최근 대화 ====================
        st.subheader("💬 최근 대화 (최신순)")

        try:
            history = db.get_history(limit=5)

            if history:
                print(f"최근 대화 {len(history)}건 로드")

                # 역순으로 정렬 (최근이 맨 위)
                history = list(reversed(history))

                for idx, chat in enumerate(history, 1):
                    with st.expander(f"대화 #{chat['id']} - {chat.get('category', '기타')}"):
                        st.write(f"**👤 사용자:**\n{chat['user_message']}")
                        st.write(f"**🤖 AI:**\n{chat['assistant_message']}")

                        col1, col2, col3 = st.columns(3)
                        with col1:
                            if chat.get('llm_provider'):
                                st.caption(f"🤖 {chat['llm_provider'].upper()}")
                        with col2:
                            if chat.get('timestamp'):
                                st.caption(f"⏰ {chat['timestamp']}")
                        with col3:
                            if chat.get('rating') is not None:
                                rating_emoji = {1: "👍", 0: "😐", -1: "👎"}.get(chat['rating'], "❓")
                                st.caption(f"⭐ {rating_emoji}")
            else:
                st.info("아직 대화가 없습니다.")

        except Exception as e:
            print(f"❌ 최근 대화 로드 실패: {str(e)}")
            st.warning(f"최근 대화를 로드할 수 없습니다: {str(e)}")

        st.divider()

        # ==================== 통계 정보 ====================
        st.subheader("📋 상세 통계")

        stats_info = {
            "총 대화 수": stats.get('total_chats', 0),
            "긍정적 평가 (👍)": stats.get('rating_stats', {}).get(1, 0),
            "중립 평가 (😐)": stats.get('rating_stats', {}).get(0, 0),
            "부정적 평가 (👎)": stats.get('rating_stats', {}).get(-1, 0),
            "평가된 대화": sum(stats.get('rating_stats', {}).values()),
        }

        col1, col2, col3 = st.columns(3)
        with col1:
            for key in list(stats_info.keys())[:2]:
                st.metric(key, stats_info[key])

        with col2:
            for key in list(stats_info.keys())[2:4]:
                st.metric(key, stats_info[key])

        with col3:
            st.metric(list(stats_info.keys())[4], stats_info[list(stats_info.keys())[4]])

        print("✅ 대시보드 로드 완료\n")

    except Exception as e:
        print(f"❌ 대시보드 오류: {str(e)}")
        import traceback
        print(traceback.format_exc())
        st.error(f"❌ 대시보드를 로드할 수 없습니다: {str(e)}")
