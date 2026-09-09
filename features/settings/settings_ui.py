import streamlit as st
from pathlib import Path
from features.rag.document_loader import DocumentLoader
from features.rag.text_splitter import TextSplitter
from features.rag.embedding_generator import EmbeddingGenerator
from features.rag.faiss_indexer import FAISSIndexBuilder
from features.shared.state_manager import StateManager
from features.shared.api import llm_factory
from features.shared.sample_data_generator import SampleDataGenerator
from features.shared.ui_utils import handle_error, show_confirmation_dialog
from config import SAMPLE_DATA_PATH, FAISS_INDEX_PATH, OLLAMA_EMBEDDING_DIM, OLLAMA_EMBEDDING_MODEL
import shutil
from datetime import datetime
import json


def show():
    st.title("⚙️ 설정")
    state = StateManager()
    current_state = state.load_state()

    # 현재 상태 표시
    col1, col2 = st.columns(2)
    with col1:
        docs_status = "✅" if current_state.get("documents_loaded") else "❌"
        st.metric("문서", f"{docs_status} {'로드됨' if current_state.get('documents_loaded') else '미로드'}")
    with col2:
        index_status = "✅" if current_state.get("index_loaded") else "❌"
        st.metric("인덱스", f"{index_status} {'생성됨' if current_state.get('index_loaded') else '미생성'}")

    st.divider()

    # ==================== LLM 프로바이더 선택 ====================
    st.subheader("🤖 모델 선택")
    col1, col2 = st.columns(2)
    with col1:
        st.write("**LLM (생성) 모델:**")
        current_llm = current_state.get("llm_provider", "gemini")
        llm_provider = st.radio(
            "LLM 프로바이더",
            options=["gemini", "ollama"],
            index=0 if current_llm == "gemini" else 1,
            label_visibility="collapsed",
            key="llm_provider_radio",
        )
    with col2:
        st.write("**임베딩 모델:**")
        st.info(f"🔒 **Ollama로 고정됨**\n- 모델: {OLLAMA_EMBEDDING_MODEL}\n- 차원: {OLLAMA_EMBEDDING_DIM}")

    st.info(f"📌 현재 선택: LLM={llm_provider.upper()} | 임베딩=OLLAMA (고정)")

    st.divider()

    # ==================== 문서 로드 및 인덱스 생성 ====================
    st.subheader("📥 문서 로드 및 인덱스 생성")
    if st.button("📥 문서 로드 및 인덱스 생성", key="load_docs_btn"):
        load_documents_and_index(llm_provider, state)

    st.divider()

    # ==================== 샘플 데이터 생성 ====================
    st.subheader("🔄 샘플 데이터 생성")
    st.write("테스트 목적으로 190개의 샘플 대화를 생성합니다.")
    if st.button("🔄 샘플 데이터 생성", key="generate_sample_btn"):
        generate_sample_data()

    st.divider()

    # ==================== 초기화 ====================
    st.subheader("🔄 초기화")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🗑️ FAISS 인덱스 삭제", key="delete_index_btn"):
            def delete_index():
                try:
                    if Path(FAISS_INDEX_PATH).exists():
                        shutil.rmtree(FAISS_INDEX_PATH)
                        st.success("✅ FAISS 인덱스 삭제 완료")
                        state.save_state(index_loaded=False)
                        st.rerun()
                    else:
                        st.info("ℹ️ 인덱스가 없습니다.")
                except Exception as e:
                    st.error(f"❌ 삭제 실패: {e}")

            delete_index()

    with col2:
        if st.button("🗑️ 모든 대화 삭제", key="delete_chats_btn"):
            st.warning("⚠️ 이 작업은 되돌릴 수 없습니다!")
            if st.button("⚠️ 정말 삭제하시겠습니까?", key="confirm_delete_chats"):
                # 실제 삭제는 app.py에서 처리
                st.info("💬 대화 내역 관리 섹션에서 삭제해주세요.")

    st.divider()

    # ==================== 현재 상태 표시 ====================
    st.subheader("📊 현재 상태")
    status_data = {
        "documents_loaded": current_state.get("documents_loaded", False),
        "index_loaded": current_state.get("index_loaded", False),
        "llm_provider": current_state.get("llm_provider", "gemini"),
        "embedding_provider": "ollama",
        "embedding_dimension": OLLAMA_EMBEDDING_DIM,
        "embedding_model": OLLAMA_EMBEDDING_MODEL,
        "sample_data_path": str(SAMPLE_DATA_PATH),
        "faiss_index_path": str(FAISS_INDEX_PATH),
    }
    st.json(status_data)

    st.divider()

    # ==================== 도움말 ====================
    st.subheader("❓ 도움말")

    with st.expander("📚 사용 가이드"):
        st.write("""
        **1. 첫 실행 시 (실제 문서 사용)**
        - `sample_data/` 폴더에 `.txt` 파일이 있는지 확인
        - **📥 문서 로드 및 인덱스 생성** 클릭
        - 벡터 DB에 저장됨

        **2. 테스트 시 (샘플 데이터 사용)**
        - **🔄 샘플 데이터 생성** 클릭
        - 190개의 대화가 자동 생성됨
        - **📊 대시보드** → **🔥 자주 받는 질문 TOP 10** 확인

        **3. 초기화**
        - **🔄 초기화** 섹션에서 인덱스/대화 삭제 가능
        """)

    with st.expander("🔧 트러블슈팅"):
        st.write("""
        **문제: 문서 로드 실패**
        - Ollama 서버 실행 여부 확인: `ollama serve`
        - `sample_data/` 폴더 존재 여부 확인

        **문제: 임베딩 생성 실패**
        - Ollama 실행 중인지 확인
        - 포트 11434가 열려있는지 확인

        **문제: TOP 10이 안 보임**
        - 먼저 샘플 데이터 생성 또는 실제 채팅 진행
        - 최소 10개 이상의 대화 필요
        """)


# ==================== 함수 모음 ====================

def load_documents_and_index(llm_provider: str, state: StateManager) -> None:
    """
    문서 로드 및 인덱스 생성 (공통 로직)

    Args:
        llm_provider: LLM 프로바이더
        state: StateManager 인스턴스
    """
    print("\n" + "=" * 60)
    print("📋 설정 페이지: 문서 로드 시작")
    print(f"   LLM 프로바이더: {llm_provider}")
    print("   임베딩 프로바이더: ollama (고정)")
    print("=" * 60 + "\n")

    with st.spinner("📖 문서 로드 중..."):
        steps = [
            ("📥 문서 로드 중...", load_documents_step),
            ("✂️ 텍스트 청킹 중...", split_documents_step),
            ("🧠 임베딩 생성 중...", generate_embeddings_step),
            ("🔍 FAISS 인덱스 생성 중...", build_faiss_index_step),
        ]

        for step_name, step_func in steps:
            if not step_func(step_name, state):
                return

        # 최종 상태 저장
        state.save_state(
            documents_loaded=True,
            index_loaded=True,
            llm_provider=llm_provider,
            embedding_provider="ollama",
        )
        st.success("✅ 모든 과정 완료!")
        st.rerun()


def load_documents_step(step_name: str, state: StateManager) -> bool:
    """문서 로드 스텝"""

    def load():
        loader = DocumentLoader(SAMPLE_DATA_PATH)
        documents = loader.load()
        if isinstance(documents, bool) or not documents:
            raise Exception("문서 로드 실패")
        st.success(f"✅ {len(documents)}개 문서 로드 완료")
        return documents

    result = handle_error(load, error_message=step_name)
    return result is not None


def split_documents_step(step_name: str, state: StateManager) -> bool:
    """텍스트 분할 스텝"""

    def split():
        documents = DocumentLoader(SAMPLE_DATA_PATH).load()
        splitter = TextSplitter()
        chunks = splitter.split(documents)
        if not chunks:
            raise Exception("청크 생성 실패")
        st.success(f"✅ {len(chunks)}개 청크 생성 완료")
        return chunks

    result = handle_error(split, error_message=step_name)
    return result is not None


def generate_embeddings_step(step_name: str, state: StateManager) -> bool:
    """임베딩 생성 스텝"""

    def embed():
        documents = DocumentLoader(SAMPLE_DATA_PATH).load()
        chunks = TextSplitter().split(documents)
        embedding_api = llm_factory.create_embedding_api(provider="ollama")
        embeddings_model = embedding_api.get_embeddings()
        embedder = EmbeddingGenerator(embeddings_model)
        embeddings = embedder.generate(chunks)
        if not embeddings:
            raise Exception("임베딩 생성 실패")
        st.success(f"✅ {len(embeddings)}개 임베딩 생성 완료")
        return embeddings

    result = handle_error(embed, error_message=step_name)
    return result is not None


def build_faiss_index_step(step_name: str, state: StateManager) -> bool:
    """FAISS 인덱스 생성 스텝"""

    def build():
        documents = DocumentLoader(SAMPLE_DATA_PATH).load()
        chunks = TextSplitter().split(documents)
        embedding_api = llm_factory.create_embedding_api(provider="ollama")
        embeddings_model = embedding_api.get_embeddings()
        embeddings = EmbeddingGenerator(embeddings_model).generate(chunks)

        builder = FAISSIndexBuilder(dimension=OLLAMA_EMBEDDING_DIM, index_path=FAISS_INDEX_PATH)
        builder.build_index(chunks, embeddings)
        builder.save_index(FAISS_INDEX_PATH)
        st.success("✅ FAISS 인덱스 생성 완료!")
        return True

    result = handle_error(build, error_message=step_name)
    return result is not None


def generate_sample_data() -> None:
    """샘플 데이터 생성"""

    def generate():
        with st.spinner("🔄 샘플 데이터 생성 중..."):
            generator = SampleDataGenerator()
            result = generator.generate()
            if result:
                st.success(f"✅ {result}개의 샘플 데이터 생성 완료!")
                print(f"✅ 샘플 데이터 생성: {result}개")
            else:
                st.error("❌ 샘플 데이터 생성 실패")
                print("❌ 샘플 데이터 생성 실패")

    handle_error(generate, error_message="샘플 데이터 생성 실패")
