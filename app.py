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

# ==================== 페이지 설정 ====================
st.set_page_config(
    page_title="AI 쇼핑 어시스턴트",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== 싱글톤 서비스 초기화 ====================
if "services" not in st.session_state:
    try:
        initial_llm_provider = st.session_state.get("llm_provider", LLM_PROVIDER)
        # 임베딩은 항상 Ollama로 고정!
        initial_embedding_provider = "ollama"

        print(f"\n{'=' * 60}")
        print(f"🚀 AI 쇼핑 어시스턴트 초기화")
        print(f"{'=' * 60}")
        print(f"📍 프로젝트 경로: {PROJECT_ROOT}")
        print(f"📍 FAISS 인덱스 경로: {FAISS_INDEX_PATH}")
        print(f"{'=' * 60}\n")

        # 데이터베이스 초기화
        print("📊 데이터베이스 초기화 중...")
        db = ChatDatabase()
        print(f"✅ 데이터베이스 초기화 완료\n")

        # LLM API 초기화
        print(f"🔗 LLM API 초기화: {initial_llm_provider}")
        llm_api = llm_factory.create_llm_api(initial_llm_provider)
        print(f"✅ LLM API 초기화 완료\n")

        # 임베딩 API 초기화 (Ollama 고정)
        print(f"🔗 임베딩 API 초기화: ollama (고정)")
        embedding_api = llm_factory.create_embedding_api(provider="ollama")
        embeddings_model = embedding_api.get_embeddings()
        print(f"✅ 임베딩 API 초기화 완료")
        print(f"   - 모델 클래스: {type(embeddings_model).__name__}\n")

        # Retriever 초기화
        print(f"🔗 Retriever 초기화 중...")
        retriever = Retriever(embeddings_model, FAISS_INDEX_PATH)
        print(f"✅ Retriever 초기화 완료")
        print(f"   - 청크 로드됨: {len(retriever.chunks) > 0}\n")

        # ChatbotService 초기화
        print(f"🔗 ChatbotService 초기화 중...")
        chatbot_service = ChatbotService(
            retriever=retriever,
            db=db,
            llm_provider=initial_llm_provider
        )
        print(f"✅ ChatbotService 초기화 완료\n")

        # 세션 상태에 서비스 저장
        st.session_state.services = {
            'chatbot': chatbot_service,
            'db': db,
            'llm_api': llm_api,
            'embedding_api': embedding_api,
        }
        st.session_state.llm_provider = initial_llm_provider
        st.session_state.embedding_provider = "ollama"  # 고정

        print(f"{'=' * 60}")
        print(f"✅ 서비스 초기화 완료!")
        print(f"   - LLM 프로바이더: {initial_llm_provider}")
        print(f"   - 임베딩 프로바이더: ollama (고정)")
        print(f"{'=' * 60}\n")

    except Exception as e:
        print(f"\n{'=' * 60}")
        print(f"❌ 서비스 초기화 실패!")
        print(f"{'=' * 60}")
        print(f"오류: {str(e)}\n")
        st.error(f"❌ 서비스 초기화 실패: {str(e)}")
        import traceback

        st.text(traceback.format_exc())
        st.stop()

# ==================== 상태 로드 ====================
state = StateManager()
status = state.load_state()

print(f"✅ 상태 로드됨: {status}\n")

# ==================== 사이드바 ====================
with st.sidebar:
    st.title("🛍️ AI 쇼핑 어시스턴트")
    st.divider()

    # ==================== 모델 정보 표시 ====================
    st.subheader("🤖 현재 모델")
    current_llm_provider = status.get("llm_provider", LLM_PROVIDER)
    current_embedding_provider = "ollama"  # 항상 ollama

    col1, col2 = st.columns(2)
    with col1:
        st.metric("LLM", current_llm_provider.upper())
    with col2:
        st.metric("임베딩", "OLLAMA")

    # 모델 상세 정보
    with st.expander("📊 모델 상세 정보"):
        st.write("**LLM (생성 모델):**")
        if current_llm_provider == "gemini":
            st.write("- 모델: Gemini 3.5 Flash Lite")
            st.write("- 제공: Google")
            st.write("- 비용: 유료 (API 요금제)")
        else:
            st.write("- 모델: Ollama Qwen2.5 14B")
            st.write("- 제공: 로컬 실행")
            st.write("- 비용: 무료")

        st.divider()
        st.write("**임베딩 모델 (고정):**")
        st.write("- 모델: Ollama nomic-embed-text")
        st.write("- 차원: 768")
        st.write("- 제공: 로컬 실행")
        st.write("- 비용: 무료")

    st.divider()

    # ==================== 상태 표시 ====================
    st.subheader("📊 시스템 상태")
    col1, col2 = st.columns(2)
    with col1:
        docs_status = "✅" if status.get('documents_loaded', False) else "❌"
        st.write(f"{docs_status} 문서: {'로드됨' if status.get('documents_loaded', False) else '미로드'}")
    with col2:
        index_status = "✅" if status.get('index_loaded', False) else "❌"
        st.write(f"{index_status} 인덱스: {'생성됨' if status.get('index_loaded', False) else '미생성'}")

    st.divider()

    # ==================== 페이지 네비게이션 ====================
    st.subheader("📍 페이지")
    page = st.radio(
        "페이지 선택",
        ["💬 채팅", "📊 대시보드", "⚙️ 설정"],
        label_visibility="collapsed"
    )

# ==================== 페이지 라우팅 ====================
if page == "💬 채팅":
    print(f"\n{'=' * 60}")
    print(f"📄 채팅 페이지 진입")
    print(f"{'=' * 60}\n")
    chatbot_ui.show(
        st.session_state.services['chatbot'],
        status.get('documents_loaded', False),
        status.get('index_loaded', False)
    )

elif page == "📊 대시보드":
    print(f"\n{'=' * 60}")
    print(f"📊 대시보드 페이지 진입")
    print(f"{'=' * 60}\n")
    dashboard_ui.show(st.session_state.services['db'])

elif page == "⚙️ 설정":
    print(f"\n{'=' * 60}")
    print(f"⚙️ 설정 페이지 진입")
    print(f"{'=' * 60}\n")
    settings_ui.show()
