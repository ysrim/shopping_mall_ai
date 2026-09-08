import streamlit as st
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import PROJECT_ROOT, FAISS_INDEX_PATH, LLM_PROVIDER, EMBEDDING_PROVIDER
from features.rag import Retriever
from features.shared.api import llm_factory
from features.shared.db import ChatDatabase
from features.shared.state_manager import StateManager
from features.chat.chatbot_service import ChatbotService
from features.chat import chatbot_ui
from features.dashboard import dashboard_ui
from features.settings import settings_ui

st.set_page_config(page_title="AI 쇼핑 어시스턴트", layout="wide", initial_sidebar_state="expanded")

if "services" not in st.session_state:
    try:
        initial_llm_provider = st.session_state.get("llm_provider", LLM_PROVIDER)
        initial_embedding_provider = "ollama"

        print("\n" + "=" * 60)
        print("🚀 AI 쇼핑 어시스턴트 초기화")
        print("=" * 60)
        print(f"📍 프로젝트 경로: {PROJECT_ROOT}")
        print(f"📍 FAISS 인덱스 경로: {FAISS_INDEX_PATH}")
        print(f"📍 LLM 프로바이더: {initial_llm_provider}")
        print(f"📍 임베딩 프로바이더: {initial_embedding_provider}")

        # 1. DB 초기화
        print(f"\n📦 ChatDatabase 초기화 중...")
        db = ChatDatabase()
        print(f"✅ ChatDatabase 초기화 완료")

        # 2. LLM API 초기화
        print(f"\n🤖 LLM API 초기화 중...")
        llm_api = llm_factory.create_llm_api(initial_llm_provider)
        print(f"✅ LLM API 초기화 완료")

        # 3. 임베딩 API 초기화
        print(f"\n🔧 임베딩 API 초기화 중...")
        embedding_api = llm_factory.create_embedding_api(provider="ollama")
        embeddings_model = embedding_api.get_embeddings()
        print(f"✅ 임베딩 API 초기화 완료")

        # 4. Retriever 초기화 (매우 중요!)
        print(f"\n📚 Retriever 초기화 중...")
        print(f"   FAISS 경로: {FAISS_INDEX_PATH}")
        print(f"   경로 존재: {FAISS_INDEX_PATH.exists()}")

        if FAISS_INDEX_PATH.exists():
            print(f"   폴더 내용:")
            for f in FAISS_INDEX_PATH.glob("*"):
                print(f"      - {f.name} ({f.stat().st_size} bytes)")

        retriever = Retriever(embeddings_model, FAISS_INDEX_PATH)

        if retriever.index is None:
            print(f"⚠️ Retriever 인덱스가 None입니다!")
            print(f"   청크 수: {len(retriever.chunks)}")
        else:
            print(f"✅ Retriever 초기화 완료")
            print(f"   벡터 수: {retriever.index.ntotal}")
            print(f"   청크 수: {len(retriever.chunks)}")

        # 5. ChatbotService 초기화
        print(f"\n💬 ChatbotService 초기화 중...")
        chatbot_service = ChatbotService(
            retriever=retriever,
            db=db,
            llm_provider=initial_llm_provider
        )
        print(f"✅ ChatbotService 초기화 완료")

        # 6. 세션 상태에 저장
        st.session_state.services = {
            'chatbot': chatbot_service,
            'db': db,
            'llm_api': llm_api,
            'embedding_api': embedding_api,
            'retriever': retriever,
        }
        st.session_state.llm_provider = initial_llm_provider
        st.session_state.embedding_provider = "ollama"

        print("\n" + "=" * 60)
        print("✅ 모든 서비스 초기화 완료!")
        print("=" * 60 + "\n")

    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ 서비스 초기화 실패: {str(e)}")
        print("=" * 60)
        import traceback

        print(traceback.format_exc())
        st.error(f"❌ 서비스 초기화 실패: {str(e)}")
        st.stop()

state = StateManager()
status = state.load_state()
print(f"✅ 상태 로드됨: {status}\n")

with st.sidebar:
    st.title("🛍️ AI 쇼핑 어시스턴트")
    st.divider()
    st.subheader("🤖 현재 모델")
    current_llm_provider = status.get("llm_provider", LLM_PROVIDER)
    col1, col2 = st.columns(2)
    with col1:
        st.metric("LLM", current_llm_provider.upper())
    with col2:
        st.metric("임베딩", "OLLAMA")

    with st.expander("📊 모델 상세 정보"):
        st.write("**LLM (생성 모델):**")
        if current_llm_provider == "gemini":
            st.write("- 모델: Gemini 3.5 Flash Lite\n- 제공: Google\n- 비용: 유료")
        else:
            st.write("- 모델: Ollama Qwen2.5 14B\n- 제공: 로컬 실행\n- 비용: 무료")
        st.divider()
        st.write("**임베딩 모델 (고정):**")
        st.write("- 모델: Ollama nomic-embed-text\n- 차원: 768\n- 제공: 로컬 실행\n- 비용: 무료")

    st.divider()
    st.subheader("📊 시스템 상태")
    col1, col2 = st.columns(2)
    with col1:
        docs_status = "✅" if status.get('documents_loaded', False) else "❌"
        st.write(f"{docs_status} 문서: {'로드됨' if status.get('documents_loaded', False) else '미로드'}")
    with col2:
        index_status = "✅" if status.get('index_loaded', False) else "❌"
        st.write(f"{index_status} 인덱스: {'생성됨' if status.get('index_loaded', False) else '미생성'}")

    # 디버그 정보
    st.divider()
    st.subheader("🔍 디버그 정보")
    retriever = st.session_state.services.get('retriever')
    if retriever:
        st.write(f"**Retriever 상태:**")
        st.write(f"- 인덱스: {retriever.index is not None}")
        if retriever.index:
            st.write(f"- 벡터 수: {retriever.index.ntotal}")
        st.write(f"- 청크 수: {len(retriever.chunks)}")

    st.divider()
    st.subheader("📍 페이지")
    page = st.radio("페이지 선택", ["💬 채팅", "📊 대시보드", "⚙️ 설정"], label_visibility="collapsed")

if page == "💬 채팅":
    print("📄 채팅 페이지 진입")
    chatbot_ui.show(st.session_state.services['chatbot'], status.get('documents_loaded', False),
                    status.get('index_loaded', False))
elif page == "📊 대시보드":
    print("📊 대시보드 페이지 진입")
    dashboard_ui.show(st.session_state.services['db'])
elif page == "⚙️ 설정":
    print("⚙️ 설정 페이지 진입")
    settings_ui.show()
