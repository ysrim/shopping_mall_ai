# app.py
import streamlit as st
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import PROJECT_ROOT, FAISS_INDEX_PATH
from features.rag import Retriever
from features.shared.api import llm_factory
from features.shared.db import ChatDatabase
from features.shared.state_manager import StateManager
from features.chat.chatbot_service import ChatbotService
from features.chat import chatbot_ui
from features.dashboard import dashboard_ui
from features.settings import settings_ui

st.set_page_config(
    page_title="AI 쇼핑 어시스턴트",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== 싱글톤 서비스 초기화 =====
if "services" not in st.session_state:
    try:
        db = ChatDatabase()

        # 초기 프로바이더 설정
        initial_llm_provider = "gemini"
        initial_embedding_provider = "ollama"

        # Retriever 초기화
        embedding_api = llm_factory.create_embedding_api(initial_embedding_provider)
        retriever = Retriever(
            embeddings_model=embedding_api.get_embeddings(),
            index_path=FAISS_INDEX_PATH
        )

        # ChatbotService 초기화
        chatbot_service = ChatbotService(retriever, db, llm_provider=initial_llm_provider)
        chatbot_service.set_embedding_provider(initial_embedding_provider)

        st.session_state.services = {
            'chatbot': chatbot_service,
            'db': db,
            'retriever': retriever
        }

        # 프로바이더 초기값 설정
        st.session_state.llm_provider = initial_llm_provider
        st.session_state.embedding_provider = initial_embedding_provider

        print("✅ 모든 서비스 초기화 완료")

    except Exception as e:
        st.error(f"❌ 서비스 초기화 실패: {str(e)}")
        import traceback

        st.error(traceback.format_exc())
        st.stop()

state = StateManager()
status = state.load_state()

# ===== 네비게이션 메뉴 =====
with st.sidebar:
    st.title("🛍️ AI 쇼핑 어시스턴트")
    st.divider()

    page = st.radio(
        "페이지 선택",
        options=["💬 채팅", "📊 대시보드", "⚙️ 설정"],
        label_visibility="collapsed"
    )

    st.divider()

    # 현재 설정 표시
    with st.expander("📌 현재 설정"):
        if "llm_provider" in st.session_state:
            llm = st.session_state.llm_provider
            llm_name = "☁️ Gemini 3.8 Flash" if llm == "gemini" else "🖥️ Ollama Qwen2.5"
            st.write(f"**LLM:** {llm_name}")

        if "embedding_provider" in st.session_state:
            embedding = st.session_state.embedding_provider
            embedding_name = "☁️ Gemini Text-Embedding-004" if embedding == "gemini" else "🖥️ Ollama Nomic"
            st.write(f"**임베딩:** {embedding_name}")

        st.write(f"**문서 로드:** {'✅' if status.get('documents_loaded') else '❌'}")
        st.write(f"**인덱스 생성:** {'✅' if status.get('index_loaded') else '❌'}")

# ===== 페이지 라우팅 =====
if page == "💬 채팅":
    chatbot_ui.show(
        st.session_state.services['chatbot'],
        status.get('documents_loaded', False),
        status.get('index_loaded', False)
    )
elif page == "📊 대시보드":
    dashboard_ui.show(st.session_state.services['db'])
elif page == "⚙️ 설정":
    settings_ui.show()
