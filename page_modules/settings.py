import streamlit as st
from modules.rag import RAGPipeline
from modules.db import ChatDatabase
from modules.state_manager import StateManager
from config import SAMPLE_DATA_PATH, TEMPERATURE, MAX_TOKENS

st.markdown("# ⚙️ 설정")

if "rag" not in st.session_state:
    st.session_state.rag = RAGPipeline()

# ============ 문서 관리 ============
st.markdown("## 📚 문서 관리")
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    if st.session_state.documents_loaded:
        st.success("✅ 문서가 로드되었습니다")
        if st.button("🔄 문서 다시 로드", use_container_width=True):
            with st.spinner("📚 문서 로딩 중..."):
                doc_count = st.session_state.rag.load_documents(SAMPLE_DATA_PATH)
                st.session_state.documents_loaded = True
                StateManager.save_state(st.session_state.documents_loaded, st.session_state.index_loaded)
                st.success(f"✅ {doc_count}개 문서 로드 완료")
    else:
        if st.button("📥 문서 로드", use_container_width=True):
            with st.spinner("📚 문서 로딩 중..."):
                doc_count = st.session_state.rag.load_documents(SAMPLE_DATA_PATH)
                st.session_state.documents_loaded = True
                StateManager.save_state(st.session_state.documents_loaded, st.session_state.index_loaded)
                st.success(f"✅ {doc_count}개 문서 로드 완료")

with col2:
    if st.session_state.index_loaded:
        st.success("✅ 인덱싱이 완료되었습니다")
        if st.button("🔄 인덱싱 다시 실행", use_container_width=True):
            if st.session_state.documents_loaded:
                with st.spinner("🔄 인덱싱 중..."):
                    if st.session_state.rag.build_index():
                        StateManager.save_state(st.session_state.documents_loaded, True)
                        st.success("✅ 인덱싱 완료")
            else:
                st.warning("⚠️ 먼저 문서를 로드하세요")
    else:
        if st.button("🔨 인덱싱 시작", use_container_width=True):
            if st.session_state.documents_loaded:
                with st.spinner("🔄 인덱싱 중..."):
                    if st.session_state.rag.build_index():
                        StateManager.save_state(st.session_state.documents_loaded, True)
                        st.success("✅ 인덱싱 완료")
            else:
                st.warning("⚠️ 먼저 문서를 로드하세요")

# ============ 모델 설정 ============
st.markdown("---")
st.markdown("## 🤖 모델 설정")
st.markdown("---")

st.session_state.temperature = st.slider(
    "🌡️ 창의성 (Temperature)",
    min_value=0.0,
    max_value=1.0,
    value=st.session_state.temperature,
    step=0.1
)

st.session_state.max_tokens = st.slider(
    "📏 응답 길이 (Max Tokens)",
    min_value=100,
    max_value=4000,
    value=st.session_state.max_tokens,
    step=100
)

# ============ 캐시 관리 ============
st.markdown("---")
st.markdown("## 💾 캐시 관리")
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    if st.button("🗑️ 임베딩 캐시 초기화", use_container_width=True):
        st.session_state.rag.clear_cache()
        st.success("✅ 캐시 초기화 완료")

with col2:
    if st.button("📋 채팅 히스토리 초기화", use_container_width=True):
        db = ChatDatabase()
        db.clear_history()
        st.session_state.chat_history = []
        st.success("✅ 히스토리 초기화 완료")

# ============ 전체 초기화 ============
st.markdown("---")
st.markdown("## 🔄 전체 초기화")
st.markdown("---")

if st.button("⚠️ 모든 설정 초기화", use_container_width=True):
    if st.confirm("정말로 모든 설정을 초기화하시겠습니까?"):
        StateManager.reset_state()
        st.session_state.documents_loaded = False
        st.session_state.index_loaded = False
        st.success("✅ 초기화 완료")
        st.rerun()

st.markdown("---")
st.caption("v1.0 | AI Shopping Assistant")
