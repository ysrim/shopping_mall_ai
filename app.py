import streamlit as st
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import (
    PROJECT_ROOT,
    FAISS_INDEX_PATH,
    LLM_PROVIDER,
    EMBEDDING_PROVIDER,
)
from features.rag import Retriever
from features.shared.api import llm_factory
from features.shared.db import ChatDatabase
from features.shared.state_manager import StateManager
from features.chat.chatbot_service import ChatbotService
from features.chat import chatbot_ui
from features.dashboard import dashboard_ui
from features.settings import settings_ui

st.set_page_config(page_title="AI 쇼핑 어시스턴트", layout="wide")

# ==================== 싱글톤 서비스 초기화 ====================
if "services" not in st.session_state:
    try:
        # 기본 프로바이더 설정
        initial_llm_provider = st.session_state.get("llm_provider", LLM_PROVIDER)
        initial_embedding_provider = st.session_state.get("embedding_provider", EMBEDDING_PROVIDER)

        # 데이터베이스 초기화
        db = ChatDatabase()

        # LLM API 초기화
        print(f"🔗 LLM API 초기화: {initial_llm_provider}")
        llm_api = llm_factory.create_llm_api(initial_llm_provider)

        # 임베딩 API 초기화
        print(f"🔗 임베딩 API 초기화: {initial_embedding_provider}")
        embedding_api = llm_factory.create_embedding_api(initial_embedding_provider)

        # 임베딩 모델 가져오기
        embeddings_model = embedding_api.get_embeddings() if hasattr(embedding_api, 'get_embeddings') else embedding_api

        # Retriever 초기화
        retriever = Retriever(embeddings_model, FAISS_INDEX_PATH)

        # ChatbotService 초기화
        chatbot_service = ChatbotService(retriever, llm_api, db)

        # 세션 상태에 저장
        st.session_state.services = {
            'chatbot': chatbot_service,
            'db': db,
            'llm_api': llm_api,
            'embedding_api': embedding_api,
        }

        # 프로바이더 정보 저장
        st.session_state.llm_provider = initial_llm_provider
        st.session_state.embedding_provider = initial_embedding_provider

        print(f"✅ 서비스 초기화 완료 (LLM: {initial_llm_provider}, 임베딩: {initial_embedding_provider})")

    except Exception as e:
        st.error(f"❌ 서비스 초기화 실패: {str(e)}")
        import traceback

        st.text(traceback.format_exc())
        st.stop()

# ==================== 상태 로드 ====================
state = StateManager()
status = state.load_state()

# ==================== 사이드바 네비게이션 ====================
with st.sidebar:
    st.title("🛍️ AI 쇼핑 어시스턴트")

    # 현재 모델 정보 표시
    st.divider()
    st.subheader("🤖 현재 모델")
    col1, col2 = st.columns(2)
    with col1:
        llm_provider = st.session_state.get("llm_provider", LLM_PROVIDER)
        st.metric("LLM", llm_provider.upper())
    with col2:
        embedding_provider = st.session_state.get("embedding_provider", EMBEDDING_PROVIDER)
        st.metric("임베딩", embedding_provider.upper())

    # 문서/인덱스 상태
    st.divider()
    st.subheader("📊 상태")
    col1, col2 = st.columns(2)
    with col1:
        docs_status = "✅" if status.get('documents_loaded', False) else "❌"
        st.write(f"{docs_status} 문서: {'로드됨' if status.get('documents_loaded', False) else '미로드'}")
    with col2:
        index_status = "✅" if status.get('index_loaded', False) else "❌"
        st.write(f"{index_status} 인덱스: {'생성됨' if status.get('index_loaded', False) else '미생성'}")

    st.divider()

    # 페이지 선택
    st.subheader("📍 페이지")
    page = st.radio(
        "페이지 선택",
        ["💬 채팅", "📊 대시보드", "⚙️ 설정"],
        label_visibility="collapsed"
    )

# ==================== 페이지 라우팅 ====================
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
