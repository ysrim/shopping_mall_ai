import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from modules.db import ChatDatabase
from config import DB_PATH

st.markdown("# 📊 대시보드")

# ============ 데이터베이스 초기화 ============
db = ChatDatabase()

# ============ 통계 조회 ============
stats = db.get_statistics()

# ============ 핵심 메트릭 ============
st.markdown("---")
st.markdown("### 📈 핵심 지표")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="💬 총 대화 수",
        value=stats['total_chats']
    )

with col2:
    # 평가된 대화 수 표시
    avg_display = f"{stats['avg_rating']:.2f}" if stats['rated_chats'] > 0 else "평가 없음"
    st.metric(
        label="⭐ 평균 평점",
        value=avg_display,
        help=f"평가된 대화: {stats['rated_chats']}개"
    )

with col3:
    st.metric(
        label="👍 도움됨",
        value=stats['good_count']
    )

with col4:
    st.metric(
        label="😊 만족도",
        value=f"{stats['satisfaction']:.1f}%"
    )

# ============ 상세 통계 ============
st.markdown("---")
st.markdown("### 📊 평가 현황")

col1, col2, col3 = st.columns(3)
with col1:
    st.info(f"👍 **도움됨**: {stats['good_count']}개")
with col2:
    st.warning(f"😐 **보통**: {stats['normal_count']}개")
with col3:
    st.error(f"👎 **도움 안됨**: {stats['bad_count']}개")

# ============ 차트 ============
st.markdown("---")
st.markdown("### 📉 평가 분포")

# 파이 차트 - 평가 분포
if stats['total_chats'] > 0:
    fig_pie = go.Figure(data=[go.Pie(
        labels=['👍 도움됨', '😐 보통', '👎 도움 안됨'],
        values=[
            stats['good_count'],
            stats['normal_count'],
            stats['bad_count']
        ],
        marker=dict(colors=['#10b981', '#f59e0b', '#ef4444']),
        textposition='inside',
        textinfo='label+percent'
    )])

    fig_pie.update_layout(
        title="평가 분포",
        height=400,
        showlegend=True
    )

    st.plotly_chart(fig_pie, use_container_width=True)
else:
    st.info("아직 평가 데이터가 없습니다.")

# ============ 최근 대화 ============
st.markdown("---")
st.markdown("### 💬 최근 대화")

recent_chats = db.get_recent_chats(limit=10)

if recent_chats:
    for chat_id, timestamp, user_msg, assistant_msg, rating in recent_chats:
        rating_emoji = '👍' if rating == 1 else '😐' if rating == 3 else '👎' if rating == 5 else '⭐'
        with st.expander(f"🕐 {timestamp} - 평가: {rating_emoji}"):
            st.markdown(f"**👤 사용자:** {user_msg}")
            st.markdown(f"**🤖 어시스턴트:** {assistant_msg}")
            if rating:
                st.caption(f"📊 평가: {'좋음' if rating == 1 else '보통' if rating == 3 else '나쁨'}")
            else:
                st.caption("📊 평가: 없음")
else:
    st.info("아직 대화가 없습니다.")

# ============ 데이터 관리 ============
st.markdown("---")
st.markdown("### 🛠️ 데이터 관리")

col1, col2 = st.columns(2)

with col1:
    if st.button("📊 CSV 내보내기"):
        try:
            chats = db.get_chat_history(limit=1000)
            df = pd.DataFrame(chats, columns=['ID', 'Timestamp', 'User', 'Assistant', 'Rating'])
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 CSV 다운로드",
                data=csv,
                file_name="chat_history.csv",
                mime="text/csv"
            )
            st.success("✅ CSV 내보내기 준비 완료")
        except Exception as e:
            st.error(f"❌ CSV 내보내기 실패: {e}")

with col2:
    if st.button("🗑️ 데이터 초기화"):
        if st.confirm("정말로 모든 데이터를 삭제하시겠습니까?"):
            try:
                db.clear_history()
                st.success("✅ 모든 데이터가 초기화되었습니다")
                st.rerun()
            except Exception as e:
                st.error(f"❌ 데이터 초기화 실패: {e}")
