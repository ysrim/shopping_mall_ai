import streamlit as st
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import PROJECT_ROOT, FAISS_INDEX_PATH
from features.rag import Retriever
from features.shared.api import GeminiAPI
from features.shared.db import ChatDatabase
from features.shared.state_manager import StateManager
from features.chat.chatbot_service import ChatbotService
from features.chat import chatbot_ui
from features.dashboard import dashboard_ui
from features.settings import settings_ui

st.set_page_config(page_title="AI 쇼핑 어시스턴트", layout="wide")

# 싱글톤 서비스 초기화
if "services" not in st.session_state:
    api = GeminiAPI()
    db = ChatDatabase()
    retriever = Retriever(api, FAISS_INDEX_PATH)
    st.session_state.services = {
        'chatbot': ChatbotService(retriever, api, db),
        'db': db
    }

state = StateManager()
status = state.load_state()

# 네비게이션
with st.sidebar:
    st.title("🛍️ 메뉴")
    page = st.radio("페이지 선택", ["💬 채팅", "📊 대시보드", "⚙️ 설정"], label_visibility="collapsed")

# 라우팅
if page == "💬 채팅":
    chatbot_ui.show(st.session_state.services['chatbot'], status.get('documents_loaded', False), status.get('index_loaded', False))
elif page == "📊 대시보드":
    dashboard_ui.show(st.session_state.services['db'])
elif page == "⚙️ 설정":
    settings_ui.show()
