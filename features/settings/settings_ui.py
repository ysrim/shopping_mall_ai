import streamlit as st
from pathlib import Path
from features.rag.document_loader import DocumentLoader
from features.rag.text_splitter import TextSplitter
from features.rag.embedding_generator import EmbeddingGenerator
from features.rag.faiss_indexer import FAISSIndexBuilder
from features.shared.state_manager import StateManager
from features.shared.api import llm_factory
from features.shared.sample_data_generator import SampleDataGenerator
from config import SAMPLE_DATA_PATH, FAISS_INDEX_PATH, OLLAMA_EMBEDDING_DIM, OLLAMA_EMBEDDING_MODEL
import shutil
from datetime import datetime


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
        print("\n" + "=" * 60)
        print("📋 설정 페이지: 문서 로드 시작")
        print(f"   LLM 프로바이더: {llm_provider}")
        print("   임베딩 프로바이더: ollama (고정)")
        print("=" * 60 + "\n")
        with st.spinner("📖 문서 로드 중..."):
            try:
                # 1. 문서 로드
                loader = DocumentLoader(SAMPLE_DATA_PATH)
                documents = loader.load()
                if isinstance(documents, bool) or not documents:
                    st.error("❌ 문서 로드 실패")
                    return
                st.success(f"✅ {len(documents)}개 문서 로드 완료")

                # 2. 텍스트 청킹
                splitter = TextSplitter()
                chunks = splitter.split(documents)
                if not chunks:
                    st.error("❌ 청크 생성 실패")
                    return
                st.success(f"✅ {len(chunks)}개 청크 생성 완료")

                # 3. Ollama 임베딩 생성 (고정)
                embedding_api = llm_factory.create_embedding_api(provider="ollama")
                embeddings_model = embedding_api.get_embeddings()
                embedder = EmbeddingGenerator(embeddings_model)
                embeddings = embedder.generate(chunks)
                if not embeddings:
                    st.error("❌ 임베딩 생성 실패")
                    return
                st.success(f"✅ {len(embeddings)}개 임베딩 생성 완료")

                # 4. FAISS 인덱스 생성
                builder = FAISSIndexBuilder(dimension=OLLAMA_EMBEDDING_DIM, index_path=FAISS_INDEX_PATH)
                builder.build_index(chunks, embeddings)
                builder.save_index(FAISS_INDEX_PATH)
                st.success("✅ FAISS 인덱스 생성 완료!")

                # 5. 상태 저장
                state.save_state(
                    documents_loaded=True,
                    index_loaded=True,
                    llm_provider=llm_provider,
                    embedding_provider="ollama",
                )
                st.success("✅ 모든 과정 완료!")
                st.rerun()
            except Exception as e:
                print(f"❌ 오류 발생: {str(e)}\n")
                import traceback, sys
                print(traceback.format_exc())
                st.error(f"❌ 오류: {str(e)}")
                st.error("💡 해결 방법: Ollama 서버 실행 확인\n```\nollama serve\n```")

    st.divider()

    # ==================== 캐시 및 인덱스 초기화 ====================
    st.subheader("🔄 초기화")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ 캐시 삭제", key="clear_cache_btn"):
            try:
                cache_path = Path("cache/embeddings.pkl")
                if cache_path.exists():
                    cache_path.unlink()
                    st.success("✅ 캐시 삭제 완료")
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

    # ==================== 대화 내역 관리 ====================
    st.subheader("💬 대화 내역 관리")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("📊 대화 내역 통계 보기", key="view_stats_btn"):
            try:
                from features.shared.db import ChatDatabase
                db = ChatDatabase()
                stats = db.get_statistics()

                st.write("**현재 저장된 대화 통계:**")
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("총 대화", stats.get('total_chats', 0))
                with col_b:
                    st.metric("평가됨", stats.get('total_rated', 0))
                with col_c:
                    st.metric("👍 좋음", stats.get('positive_count', 0))

            except Exception as e:
                st.error(f"❌ 통계 조회 실패: {e}")

    with col2:
        if st.button("🗑️ 모든 대화 삭제", key="delete_all_chats_btn"):
            st.session_state.confirm_delete = True

    # 삭제 확인 두 단계
    if st.session_state.get("confirm_delete", False):
        st.warning("⚠️ **정말로 모든 대화를 삭제하시겠습니까?** 이 작업은 되돌릴 수 없습니다.")
        col1, col2 = st.columns(2)

        with col1:
            if st.button("✅ 확인-삭제", key="confirm_delete_btn"):
                try:
                    from features.shared.db import ChatDatabase
                    db = ChatDatabase()
                    db.clear_history()
                    st.success("✅ 모든 대화 삭제 완료")
                    print("✅ 모든 대화 삭제 완료")
                    st.session_state.confirm_delete = False
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ 삭제 실패: {e}")

        with col2:
            if st.button("❌ 취소", key="cancel_delete_btn"):
                st.session_state.confirm_delete = False
                st.rerun()

    st.divider()

    # ==================== 샘플 데이터 생성 (테스트용) ====================
    st.subheader("🔄 샘플 데이터 생성 (테스트용)")
    st.info("📌 개발/테스트 용도로 2개월치 샘플 대화 데이터를 생성할 수 있습니다. 이를 통해 TOP 10 분석, 카테고리 분석 등의 기능을 미리 확인할 수 있습니다.")

    col1, col2, col3 = st.columns(3)

    with col1:
        sample_count = st.number_input(
            "각 질문당 반복 횟수",
            min_value=1,
            max_value=50,
            value=10,
            help="예: 10을 선택하면 19개 질문 × 10 = 190개 데이터 생성",
            key="sample_count_input"
        )

    with col2:
        if st.button("🔄 샘플 데이터 생성", key="generate_sample_btn"):
            try:
                with st.spinner(f"📊 {sample_count * 19}개의 샘플 데이터 생성 중..."):
                    print("\n" + "=" * 60)
                    print("🔄 샘플 데이터 생성 시작")
                    print("=" * 60)

                    generator = SampleDataGenerator()
                    total = generator.generate_sample_data(count_per_dialog=sample_count)
                    generator.close()

                    print("\n" + "=" * 60)
                    print(f"✅ 샘플 데이터 생성 완료: {total}개")
                    print("=" * 60 + "\n")

                st.success(f"✅ {total}개의 샘플 데이터 생성 완료!")
                st.info("💡 이제 **📊 대시보드**에서 다음을 확인할 수 있습니다:\n- 🔥 자주 받는 질문 TOP 10\n- 📈 전체 통계\n- 📋 카테고리별 분석")
                st.rerun()

            except Exception as e:
                print(f"❌ 샘플 데이터 생성 실패: {e}")
                import traceback
                print(traceback.format_exc())
                st.error(f"❌ 샘플 데이터 생성 실패: {e}")

    with col3:
        if st.button("🗑️ 샘플 데이터 삭제", key="delete_sample_btn"):
            try:
                with st.spinner("삭제 중..."):
                    generator = SampleDataGenerator()
                    generator.clear_sample_data()
                    generator.close()

                st.warning("✅ 샘플 데이터 삭제 완료")
                st.rerun()

            except Exception as e:
                print(f"❌ 샘플 데이터 삭제 실패: {e}")
                st.error(f"❌ 삭제 실패: {e}")

    # 샘플 데이터 정보
    st.info("""
    **📊 생성되는 샘플 데이터 정보:**

    - **19가지 질문 유형**: 배송(3), 반품(4), 결제(4), 상품(3), 회원(5)
    - **타임스탐프**: 최근 2개월 내 랜덤 설정
    - **평가**: 좋음(👍), 보통(😐), 나쁨(👎) 섞여 있음
    - **카테고리**: 자동 분류

    **사용 시나리오:**
    1. 샘플 데이터 생성 → 190개 대화 생성
    2. 📊 대시보드 확인 → TOP 10 분석 결과 보기
    3. 🔥 자주 받는 질문 파악 → 개선 항목 도출
    """)

    st.divider()

    # ==================== 현재 상태 표시 ====================
    st.subheader("📊 현재 상태")
    import json
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
        - `data/samples/` 폴더에 `.txt` 파일 추가
        - **📥 문서 로드 및 인덱스 생성** 클릭
        - 벡터 DB에 저장됨

        **2. 테스트 시 (샘플 데이터 사용)**
        - **🔄 샘플 데이터 생성** 클릭
        - 190개의 대화가 자동 생성됨
        - **📊 대시보드** → **🔥 자주 받는 질문 TOP 10** 확인

        **3. 초기화**
        - **🔄 초기화** 섹션에서 캐시/인덱스 삭제 가능
        - **💬 대화 내역 관리**에서 모든 대화 삭제 가능
        """)

    with st.expander("🔧 트러블슈팅"):
        st.write("""
        **문제: 문서 로드 실패**
        - Ollama 서버 실행 여부 확인: `ollama serve`
        - `data/samples/` 폴더 존재 여부 확인

        **문제: 임베딩 생성 실패**
        - Ollama 실행 중인지 확인
        - 포트 11434가 열려있는지 확인

        **문제: TOP 10이 안 보임**
        - 먼저 샘플 데이터 생성 또는 실제 채팅 진행
        - 최소 10개 이상의 대화 필요
        """)
