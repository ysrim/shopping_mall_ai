import streamlit as st
from features.rag import DocumentLoader, TextSplitter, EmbeddingGenerator, FAISSIndexBuilder
from features.shared.state_manager import StateManager
from features.shared.api import llm_factory
from config import PROJECT_ROOT, SAMPLE_DATA_PATH, EMBEDDING_PROVIDER
import shutil


def show():
    st.title("⚙️ 설정")

    state = StateManager()

    # ============ LLM 및 임베딩 프로바이더 선택 ============
    st.subheader("🤖 모델 선택")

    # ✅ 현재 상태 로드
    current_state = state.load_state()
    current_llm = current_state.get("llm_provider", "ollama")  # ✅ 기본값: ollama
    current_embedding = current_state.get("embedding_provider", "ollama")  # ✅ 기본값: ollama

    print(f"📊 settings_ui 로드됨")
    print(f"   현재 저장된 LLM: {current_llm}")
    print(f"   현재 저장된 임베딩: {current_embedding}")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**LLM (생성) 모델:**")
        llm_provider = st.radio(
            "LLM 프로바이더 선택",
            options=["gemini", "ollama"],
            index=0 if current_llm == "gemini" else 1,
            label_visibility="collapsed",
            key="llm_provider_select_unique"
        )
        print(f"✅ LLM 라디오 선택: {llm_provider}")

    with col2:
        st.write("**임베딩 모델:**")
        embedding_provider = st.radio(
            "임베딩 프로바이더 선택",
            options=["gemini", "ollama"],
            index=0 if current_embedding == "gemini" else 1,
            label_visibility="collapsed",
            key="embedding_provider_select_unique"
        )
        print(f"✅ 임베딩 라디오 선택: {embedding_provider}")

    # 현재 선택 상태 표시
    st.info(f"📌 현재 선택: LLM={llm_provider} | 임베딩={embedding_provider}")
    print(f"📌 설정 페이지 최종 선택값: llm_provider={llm_provider}, embedding_provider={embedding_provider}")

    st.divider()

    # ============ 문서 로드 및 인덱스 생성 ============
    st.subheader("📄 문서 관리")

    if st.button("📥 문서 로드 및 인덱스 생성", use_container_width=True):
        with st.spinner("처리 중..."):
            try:
                # ✅ 선택된 프로바이더 확인
                print(f"🔘 버튼 클릭 시점의 프로바이더:")
                print(f"   llm_provider: {llm_provider}")
                print(f"   embedding_provider: {embedding_provider}")

                # 1. 문서 로드
                st.write("📖 문서 로드 중...")
                loader = DocumentLoader(str(SAMPLE_DATA_PATH))
                doc_success = loader.load()

                if not doc_success:
                    st.error("❌ 문서 로드 실패!")
                    return

                st.success(f"✅ {len(loader.documents)}개 문서 로드 완료")
                print(f"✅ {len(loader.documents)}개 문서 로드 완료")

                # 2. 청킹
                st.write("✂️ 텍스트 청킹 중...")
                splitter = TextSplitter()
                combined = '\n\n'.join(d['content'] for d in loader.documents)
                chunks = splitter.split(combined)

                if not chunks:
                    st.error("❌ 청킹 실패!")
                    return

                st.success(f"✅ {len(chunks)}개 청크 생성 완료")
                print(f"✅ {len(chunks)}개 청크 생성 완료")

                # 3. 임베딩 (선택된 프로바이더 사용)
                st.write(f"🧠 {embedding_provider.upper()} 임베딩 생성 중...")
                print(f"🧠 {embedding_provider.upper()} 임베딩 생성 시작")

                try:
                    print(f"🔗 임베딩 API 생성 중: {embedding_provider}")
                    embedding_api = llm_factory.create_embedding_api(embedding_provider)

                    print(f"📦 임베딩 API 타입: {type(embedding_api)}")
                    print(f"   클래스명: {embedding_api.__class__.__name__}")

                    # ✅ 핵심: API 객체가 아닌 LangChain 임베딩 모델 전달
                    print(f"🔧 LangChain 임베딩 모델 추출 중...")
                    embeddings_model = embedding_api.get_embeddings()

                    print(f"📦 임베딩 모델 타입: {type(embeddings_model)}")
                    print(f"   클래스명: {embeddings_model.__class__.__name__}")

                    embedder = EmbeddingGenerator(embeddings_model)

                    print(f"🔄 임베딩 생성 시작: {len(chunks)}개 청크")
                    embeddings = embedder.generate(chunks)

                    # ✅ 임베딩 검증
                    if embeddings and len(embeddings) > 0:
                        print(f"✅ 임베딩 생성 완료: {len(embeddings)}개")
                        print(f"   첫 번째 벡터 차원: {len(embeddings[0])}")
                        st.success(f"✅ {len(embeddings)}개 임베딩 생성 완료 (차원: {len(embeddings[0])})")
                    else:
                        print(f"❌ 임베딩 결과가 비어있음")
                        st.error("❌ 임베딩 생성 실패 (결과 없음)!")
                        return

                except AttributeError as e:
                    print(f"❌ 속성 오류: {e}")
                    st.error(f"❌ {embedding_provider.upper()} 임베딩 속성 오류: {str(e)}")
                    import traceback
                    st.text(traceback.format_exc())
                    return

                except Exception as e:
                    print(f"❌ {embedding_provider.upper()} 임베딩 생성 실패: {str(e)}")
                    st.error(f"❌ {embedding_provider.upper()} 임베딩 생성 실패: {str(e)}")
                    st.info("💡 팁: Ollama 사용 시 `ollama serve` 실행 확인 후 재시도하세요.")
                    import traceback
                    st.text(traceback.format_exc())
                    return

                if not embeddings:
                    print(f"❌ 최종 임베딩 검증 실패")
                    st.error("❌ 임베딩 생성 실패!")
                    return

                # 4. FAISS 인덱싱
                st.write("🔍 FAISS 인덱싱 중...")
                print(f"🔍 FAISS 인덱싱 시작")

                indexer = FAISSIndexBuilder()
                index_success = indexer.build(chunks, embeddings, loader.documents)

                if index_success:
                    state.save_state(
                        documents_loaded=True,
                        index_loaded=True,
                        llm_provider=llm_provider,
                        embedding_provider=embedding_provider
                    )
                    print(f"✅ 상태 저장 완료:")
                    print(f"   llm_provider: {llm_provider}")
                    print(f"   embedding_provider: {embedding_provider}")
                    st.success("✅ 문서 로드 및 인덱스 생성 완료!")
                else:
                    print(f"❌ 인덱스 생성 실패")
                    st.error("❌ 인덱스 생성 실패!")
                    return

                st.rerun()

            except Exception as e:
                print(f"❌ 예기치 않은 오류: {str(e)}")
                st.error(f"❌ 예기치 않은 오류: {str(e)}")
                import traceback
                print(traceback.format_exc())
                st.text(traceback.format_exc())

    st.divider()

    # ============ 초기화 ============
    st.subheader("🗑️ 캐시 및 인덱스 초기화")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🧹 캐시 삭제", use_container_width=True):
            try:
                gemini_api = llm_factory.create_embedding_api("gemini")
                gemini_api.embedding_cache.clear()
                st.success("✅ Gemini 캐시 삭제 완료")
                print(f"✅ Gemini 캐시 삭제 완료")
            except Exception as e:
                st.warning(f"⚠️ Gemini 캐시 삭제 중 오류: {str(e)}")
                print(f"⚠️ Gemini 캐시 삭제 중 오류: {str(e)}")

    with col2:
        if st.button("🔄 인덱스 초기화", use_container_width=True):
            try:
                from config import FAISS_INDEX_PATH
                if FAISS_INDEX_PATH.exists():
                    shutil.rmtree(FAISS_INDEX_PATH)
                    st.success("✅ 인덱스 초기화 완료")
                    print(f"✅ 인덱스 초기화 완료")
                else:
                    st.info("ℹ️ 인덱스가 없습니다.")
                    print(f"ℹ️ 인덱스가 없습니다.")

                state.save_state(documents_loaded=False, index_loaded=False)
                st.rerun()
            except Exception as e:
                st.error(f"❌ 인덱스 초기화 실패: {str(e)}")
                print(f"❌ 인덱스 초기화 실패: {str(e)}")

    st.divider()

    # ============ 상태 정보 ============
    st.subheader("📊 현재 상태")
    current_state = state.load_state()
    st.json({
        "문서_로드됨": current_state.get("documents_loaded", False),
        "인덱스_생성됨": current_state.get("index_loaded", False),
        "LLM_프로바이더": current_state.get("llm_provider", "ollama"),
        "임베딩_프로바이더": current_state.get("embedding_provider", "ollama")
    })
