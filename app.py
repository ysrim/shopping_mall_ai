import streamlit as st
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import PROJECT_ROOT
from page_modules import chatbot, dashboard, settings

st.set_page_config(page_title="AI 쇼핑 어시스턴트", layout="wide")

# 사이드바 네비게이션
with st.sidebar:
    st.title("🛍️ 메뉴")
    page = st.radio("페이지 선택", ["💬 채팅", "📊 대시보드", "⚙️ 설정"], label_visibility="collapsed")

# 페이지 라우팅
if page == "💬 채팅":
    chatbot.show()
elif page == "📊 대시보드":
    dashboard.show()
elif page == "⚙️ 설정":
    settings.show()
