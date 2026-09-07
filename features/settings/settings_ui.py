import streamlit as st
from features.rag import DocumentLoader, TextSplitter, EmbeddingGenerator, FAISSIndexBuilder
from features.shared.state_manager import StateManager
from features.shared.api import GeminiAPI
from config import PROJECT_ROOT, SAMPLE_DATA_PATH


def show():
    st.title("⚙️ 설정")

    state = StateManager()

    st.subheader("📄 문서 관리")
    if st.button("문서 로드 및 인덱스 생성"):
        with st.spinner("처리 중..."):
            # 1. 문서 로드
            loader = DocumentLoader(str(SAMPLE_DATA_PATH))
            doc_success = loader.load()

            if not doc_success:
                st.error("문서 로드 실패!")
                return

            # 2. 청킹
            splitter = TextSplitter()
            combined = '\n\n'.join(d['content'] for d in loader.documents)
            chunks = splitter.split(combined)

            if not chunks:
                st.error("청킹 실패!")
                return

            # 3. 임베딩
            api = GeminiAPI()
            embedder = EmbeddingGenerator(api)
            embeddings = embedder.generate(chunks)

            if not embeddings:
                st.error("임베딩 실패!")
                return

            # 4. 인덱싱
            indexer = FAISSIndexBuilder()
            index_success = indexer.build(chunks, embeddings, loader.documents)

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
        api = GeminiAPI()
        api.embedding_cache.clear()
        st.success("✅ 캐시 삭제 완료")

    if st.button("인덱스 초기화"):
        from config import FAISS_INDEX_PATH
        import shutil
        if FAISS_INDEX_PATH.exists():
            shutil.rmtree(FAISS_INDEX_PATH)
        state.save_state(documents_loaded=False, index_loaded=False)
        st.success("✅ 인덱스 초기화 완료")
        st.rerun()
