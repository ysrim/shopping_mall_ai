import json
from pathlib import Path
from typing import List, Dict, Any
import numpy as np
from features.shared.api import llm_factory
from config import FAISS_INDEX_PATH, EMBEDDING_PROVIDER


class Retriever:
    """RAG 기반 문서 검색"""

    def __init__(self, embeddings_model=None, index_path: Path = FAISS_INDEX_PATH):
        """
        초기화

        Args:
            embeddings_model: LangChain 임베딩 모델
            index_path: FAISS 인덱스 경로
        """
        self.embeddings_model = embeddings_model
        self.index_path = Path(index_path)
        self.chunks = []
        print(f"🔧 Retriever 초기화: index_path={self.index_path}")
        self._load_metadata()

        if not self.chunks:
            print(f"⚠️ 경고: 청크 데이터가 비어있습니다 (나중에 reload_metadata()로 다시 로드 가능)")

    def reload_metadata(self):
        """메타데이터 다시 로드 (문서 로드 후 호출)"""
        print(f"🔄 메타데이터 다시 로드 중...")
        self.chunks = []
        self._load_metadata()
        print(f"✅ 메타데이터 재로드 완료: {len(self.chunks)}개 청크")

    def _load_metadata(self):
        """메타데이터 로드"""
        try:
            meta_path = self.index_path / 'metadata.json'

            print(f"🔍 메타데이터 경로: {meta_path}")
            print(f"📂 경로 존재 여부: {meta_path.exists()}")

            if not meta_path.exists():
                print(f"❌ 메타데이터 파일 없음: {meta_path}")
                print(f"   인덱스 경로 내용: {list(self.index_path.glob('*')) if self.index_path.exists() else '경로 없음'}")
                return

            print(f"📖 메타데이터 파일 읽기 중...")
            with open(meta_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            print(f"✅ JSON 파싱 완료")

            self.chunks = data.get('chunks', [])

            print(f"📊 메타데이터 내용:")
            print(f"   - 청크 개수: {len(self.chunks)}")
            print(f"   - 문서 개수: {len(data.get('documents', []))}")
            print(f"   - 차원: {data.get('dimension')}")

            if self.chunks:
                print(f"✅ 메타데이터 로드 성공: {len(self.chunks)}개 청크")
                print(f"   - 첫 번째 청크 길이: {len(self.chunks[0]) if self.chunks[0] else 0}자")
            else:
                print(f"❌ 메타데이터에 청크 없음 - JSON 파일 내용 확인 필요")
                print(f"   전체 데이터: {data}")

        except json.JSONDecodeError as e:
            print(f"❌ 메타데이터 JSON 파싱 오류: {e}")
            print(f"   파일 경로: {self.index_path / 'metadata.json'}")
        except FileNotFoundError as e:
            print(f"❌ 파일을 찾을 수 없음: {e}")
        except Exception as e:
            print(f"❌ 메타데이터 로드 오류: {e}")
            import traceback
            traceback.print_exc()

    def _get_embeddings_model(self, embedding_provider: str = None):
        """현재 설정된 임베딩 프로바이더로 임베딩 모델 반환"""
        if self.embeddings_model is not None:
            return self.embeddings_model

        if embedding_provider is None:
            embedding_provider = EMBEDDING_PROVIDER

        embedding_api = llm_factory.create_embedding_api(embedding_provider)
        return embedding_api.get_embeddings()

    def embed_query(self, query: str, embedding_provider: str = None) -> List[float]:
        """
        쿼리 임베딩 생성

        Args:
            query: 쿼리 텍스트
            embedding_provider: 임베딩 프로바이더

        Returns:
            임베딩 벡터
        """
        try:
            embeddings_model = self._get_embeddings_model(embedding_provider)
            print(f"🔧 embed_query 실행")
            print(f"   임베딩 모델 클래스: {embeddings_model.__class__.__name__}")

            query_embedding = embeddings_model.embed_query(query)

            print(f"✅ 쿼리 임베딩 생성: {len(query_embedding)}차원")
            print(f"   첫 5개 값: {query_embedding[:5]}")
            return query_embedding

        except Exception as e:
            print(f"❌ 쿼리 임베딩 오류: {e}")
            import traceback
            traceback.print_exc()
            return []

    def retrieve(self, query: str, top_k: int = 3, embedding_provider: str = None) -> List[Dict[str, Any]]:
        """
        쿼리와 유사한 문서 검색

        Args:
            query: 검색 쿼리
            top_k: 반환할 상위 K개 결과
            embedding_provider: 임베딩 프로바이더

        Returns:
            검색 결과 리스트
        """
        try:
            # ✅ 청크가 없으면 메타데이터 다시 로드 시도
            if not self.chunks:
                print(f"⚠️ 청크 데이터 없음, 메타데이터 재로드 시도...")
                self.reload_metadata()

            if not self.chunks:
                print(f"❌ 청크 데이터 없음 - 설정 페이지에서 '문서 로드 및 인덱스 생성'을 먼저 실행하세요")
                return []

            print(f"🔍 검색 시작: 쿼리='{query[:50]}...', top_k={top_k}")
            print(f"   사용 가능한 청크: {len(self.chunks)}개")

            # 쿼리 임베딩 생성
            print(f"🧠 쿼리 임베딩 생성 중...")
            q_emb = self.embed_query(query, embedding_provider)
            if not q_emb:
                print("❌ 쿼리 임베딩 실패")
                return []

            print(f"📊 쿼리 임베딩 정보:")
            print(f"   - 차원: {len(q_emb)}")
            print(f"   - 첫 5개 값: {q_emb[:5]}")

            # FAISS 인덱스 로드
            import faiss
            idx_file = self.index_path / 'index.faiss'

            if not idx_file.exists():
                print(f"❌ FAISS 인덱스 파일 없음: {idx_file}")
                return []

            print(f"📂 FAISS 인덱스 로드 중: {idx_file}")
            index = faiss.read_index(str(idx_file))
            print(f"✅ FAISS 인덱스 로드 성공")

            # ✅ 인덱스 차원 정보 출력
            print(f"📊 FAISS 인덱스 정보:")
            print(f"   - 인덱스 차원: {index.d}")
            print(f"   - 저장된 벡터 개수: {index.ntotal}")

            # ✅ 차원 검증
            if len(q_emb) != index.d:
                print(f"❌ 차원 불일치!")
                print(f"   쿼리 임베딩 차원: {len(q_emb)}")
                print(f"   FAISS 인덱스 차원: {index.d}")
                print(f"   해결책: 설정 페이지에서 '인덱스 초기화'를 클릭하고")
                print(f"           '문서 로드 및 인덱스 생성'을 다시 실행하세요")
                return []

            # 검색 실행
            print(f"🔍 FAISS 검색 실행 중...")
            search_k = min(top_k, len(self.chunks))
            D, I = index.search(
                np.array([q_emb], dtype=np.float32),
                search_k
            )

            print(f"✅ FAISS 검색 완료: {len(I[0])}개 결과")

            # 결과 정리
            results = []
            for dist, idx in zip(D[0], I[0]):
                if 0 <= idx < len(self.chunks):
                    chunk_text = self.chunks[int(idx)]
                    results.append({
                        'content': chunk_text,
                        'source': 'Retrieved Document',
                        'relevance': float(dist)
                    })
                    print(f"   ✅ 청크 {int(idx)}: 거리={float(dist):.4f}, 길이={len(chunk_text)}자")

            if results:
                print(f"✅ {len(results)}개 청크 검색 완료")
            else:
                print(f"⚠️ 검색 결과 없음")

            return results

        except AssertionError as e:
            print(f"❌ FAISS 검색 오류 (AssertionError - 차원 불일치): {e}")
            if 'q_emb' in locals() and 'index' in locals():
                print(f"   쿼리 임베딩 차원: {len(q_emb)}")
                print(f"   FAISS 인덱스 차원: {index.d}")
            print(f"   → 설정 페이지에서 '인덱스 초기화'를 클릭하고 다시 문서를 로드하세요")
            return []
        except Exception as e:
            print(f"❌ 검색 오류: {e}")
            print(f"   오류 타입: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            return []
