import streamlit as st
from modules.rag import RAGPipeline
from modules.state_manager import StateManager
from config import PROJECT_ROOT


def show():
    st.title("⚙️ 설정")

    state = StateManager()

    st.subheader("📄 문서 관리")
    if st.button("문서 로드 및 인덱스 생성"):
        with st.spinner("처리 중..."):
            # 1. 문서 로드
            rag = RAGPipeline()
            doc_success = rag.load_documents(str(PROJECT_ROOT / "sample_data"))

            if not doc_success:
                st.error("문서 로드 실패!")
                return

            # 2. 인덱스 생성
            index_success = rag.build_index()

            if index_success:
                state.save_state(documents_loaded=True, index_loaded=True)
                st.success("✅ 문서 로드 및 인덱스 생성 완료!")
            else:
                state.save_state(documents_loaded=True, index_loaded=False)
                st.error("❌ 인덱스 생성 실패!")

            st.rerun()

    st.divider()
    st.subheader("🗑️ 초기화")

    if st.button("캐시 삭제"):
        rag = RAGPipeline()
        rag.clear_cache()
        st.success("✅ 캐시 삭제 완료")

    if st.button("인덱스 초기화"):
        rag = RAGPipeline()
        rag.reset_index()
        state.save_state(documents_loaded=False, index_loaded=False)
        st.success("✅ 인덱스 초기화 완료")
        st.rerun()
