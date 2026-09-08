import streamlit as st
from pathlib import Path
from features.rag.document_loader import DocumentLoader
from features.rag.text_splitter import TextSplitter
from features.rag.embedding_generator import EmbeddingGenerator
from features.rag.faiss_indexer import FAISSIndexBuilder
from features.shared.state_manager import StateManager
from features.shared.api import llm_factory
from features.shared.db import ChatDatabase
from config import (
    SAMPLE_DATA_PATH,
    FAISS_INDEX_PATH,
    OLLAMA_EMBEDDING_DIM,
    OLLAMA_EMBEDDING_MODEL,
    DB_PATH,
)
import shutil


def show():
    st.title("⚙️ 설정")
    state = StateManager()
    current_state = state.load_state()

    # ==================== 현재 상태 표시 ====================
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
        print(f"\n{'=' * 60}")
        print(f"📋 설정 페이지: 문서 로드 시작")
        print(f"   LLM 프로바이더: {llm_provider}")
        print(f"   임베딩 프로바이더: ollama (고정)")
        print(f"{'=' * 60}\n")

        with st.spinner("📖 문서 로드 중..."):
            try:
                # 1. 문서 로드
                print("📖 문서 로드 시작...")
                loader = DocumentLoader(SAMPLE_DATA_PATH)
                documents = loader.load()

                # documents가 bool이면 에러 처리
                if isinstance(documents, bool):
                    st.error(f"❌ 문서 로드 실패")
                    print(f"❌ DocumentLoader.load()가 bool 반환: {documents}")
                    return

                if not documents or len(documents) == 0:
                    st.error("❌ 로드된 문서가 없습니다")
                    print(f"❌ 로드된 문서 없음")
                    return

                st.success(f"✅ {len(documents)}개 문서 로드 완료")
                print(f"✅ {len(documents)}개 문서 로드 완료\n")

                # 2. 텍스트 청킹
                print("✂️ 텍스트 청킹 시작...")
                st.write("✂️ 텍스트 청킹 중...")
                splitter = TextSplitter()
                chunks = splitter.split(documents)

                if not chunks or len(chunks) == 0:
                    st.error("❌ 청크 생성 실패")
                    print(f"❌ 청크 생성 실패")
                    return

                st.success(f"✅ {len(chunks)}개 청크 생성 완료")
                print(f"✅ {len(chunks)}개 청크 생성 완료\n")

                # 3. Ollama 임베딩 생성 (고정)
                print("🧠 Ollama 임베딩 생성 시작...")
                st.write("🧠 Ollama 임베딩 생성 중...")

                embedding_api = llm_factory.create_embedding_api(provider="ollama")
                embeddings_model = embedding_api.get_embeddings()

                print(f"📦 임베딩 API 타입: {type(embedding_api).__name__}")
                print(f"📦 LangChain 임베딩 모델 타입: {type(embeddings_model).__name__}\n")

                embedder = EmbeddingGenerator(embeddings_model)
                embeddings = embedder.generate(chunks)

                if not embeddings or len(embeddings) == 0:
                    st.error("❌ 임베딩 생성 실패")
                    print("❌ 임베딩 생성 실패\n")
                    return

                st.success(f"✅ {len(embeddings)}개 임베딩 생성 완료")
                print(f"✅ {len(embeddings)}개 임베딩 생성 완료\n")

                # 4. FAISS 인덱스 생성
                print("📊 FAISS 인덱스 생성 시작...")
                st.write("📊 FAISS 인덱스 생성 중...")

                builder = FAISSIndexBuilder(
                    dimension=OLLAMA_EMBEDDING_DIM,
                    index_path=FAISS_INDEX_PATH
                )
                builder.build_index(chunks, embeddings)
                builder.save_index(FAISS_INDEX_PATH)

                st.success("✅ FAISS 인덱스 생성 완료!")
                print(f"✅ FAISS 인덱스 생성 완료\n")
                print(f"   - 청크: {len(chunks)}개")
                print(f"   - 임베딩: {len(embeddings)}개")
                print(f"   - 차원: {OLLAMA_EMBEDDING_DIM}\n")

                # 5. 상태 저장
                print("💾 상태 저장 중...")
                state.save_state(
                    documents_loaded=True,
                    index_loaded=True,
                    llm_provider=llm_provider,
                    embedding_provider="ollama",  # 항상 ollama
                )
                print(f"✅ 상태 저장 완료\n")
                st.success("✅ 모든 과정 완료!")
                st.rerun()

            except Exception as e:
                print(f"❌ 오류 발생: {str(e)}\n")
                import traceback
                print(traceback.format_exc())
                st.error(f"❌ 오류: {str(e)}")
                st.error(f"💡 해결 방법: Ollama 서버 실행 확인\n```\nollama serve\n```")

    st.divider()

    # ==================== 초기화 ====================
    st.subheader("🔄 초기화")

    # ==================== 캐시 및 인덱스 초기화 ====================
    st.write("**문서 및 인덱스:**")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🗑️ 캐시 삭제", key="clear_cache_btn"):
            try:
                cache_path = Path("cache/embeddings.pkl")
                if cache_path.exists():
                    cache_path.unlink()
                    st.success("✅ 캐시 삭제 완료")
                    print("✅ 캐시 삭제 완료")
                else:
                    st.info("ℹ️ 캐시 파일이 없습니다")
            except Exception as e:
                st.error(f"❌ 캐시 삭제 실패: {str(e)}")

    with col2:
        if st.button("🔄 인덱스 초기화", key="reset_index_btn"):
            try:
                if FAISS_INDEX_PATH.exists():
                    shutil.rmtree(FAISS_INDEX_PATH)
                    st.success("✅ 인덱스 초기화 완료")
                    print("✅ FAISS 인덱스 초기화 완료")

                    # 상태 업데이트
                    state.save_state(
                        documents_loaded=False,
                        index_loaded=False,
                        llm_provider=llm_provider,
                        embedding_provider="ollama",
                    )
                    st.rerun()
                else:
                    st.info("ℹ️ 인덱스가 없습니다")
            except Exception as e:
                st.error(f"❌ 인덱스 초기화 실패: {str(e)}")

    st.divider()

    # ==================== 대화 히스토리 관리 ====================
    st.write("**대화 히스토리:**")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("📊 통계 보기", key="show_stats_btn"):
            try:
                db = ChatDatabase()
                stats = db.get_statistics()

                if stats:
                    st.subheader("📊 대화 통계")
                    st.metric("총 대화 수", stats.get('total_chats', 0))

                    if stats.get('rating_stats'):
                        st.write("**평가 분포:**")
                        rating_data = stats.get('rating_stats', {})
                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            st.metric("👍 좋음", rating_data.get(1, 0))
                        with col_b:
                            st.metric("😐 보통", rating_data.get(0, 0))
                        with col_c:
                            st.metric("👎 나쁨", rating_data.get(-1, 0))

                    if stats.get('category_stats'):
                        st.write("**카테고리 분포:**")
                        for category, count in stats.get('category_stats', {}).items():
                            st.write(f"- {category}: {count}개")
                else:
                    st.info("통계 데이터가 없습니다.")
            except Exception as e:
                st.error(f"❌ 통계 로드 실패: {str(e)}")

    with col2:
        if st.button("🗑️ 모든 대화 삭제", key="clear_history_btn"):
            try:
                # 확인 메시지
                st.warning("⚠️ 정말로 모든 대화를 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.")

                col_confirm1, col_confirm2 = st.columns(2)
                with col_confirm1:
                    if st.button("✅ 확인 - 삭제", key="confirm_delete_history"):
                        db = ChatDatabase()
                        db.clear_history()
                        st.success("✅ 모든 대화가 삭제되었습니다!")
                        print("✅ 모든 대화 삭제 완료")
                        import time
                        time.sleep(1)
                        st.rerun()

                with col_confirm2:
                    if st.button("❌ 취소", key="cancel_delete_history"):
                        st.info("삭제가 취소되었습니다.")
            except Exception as e:
                st.error(f"❌ 대화 삭제 실패: {str(e)}")

    st.divider()

    # ==================== 현재 상태 표시 ====================
    st.subheader("📊 현재 상태")
    import json
    status_data = {
        "documents_loaded": current_state.get("documents_loaded", False),
        "index_loaded": current_state.get("index_loaded", False),
        "llm_provider": current_state.get("llm_provider", "gemini"),
        "embedding_provider": "ollama",  # 항상 ollama
        "embedding_dimension": OLLAMA_EMBEDDING_DIM,
        "sample_data_path": str(SAMPLE_DATA_PATH),
        "faiss_index_path": str(FAISS_INDEX_PATH),
        "database_path": str(DB_PATH),
    }
    st.json(status_data)
