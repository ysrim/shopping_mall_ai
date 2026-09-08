# features/rag/retriever.py
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
        self._load_metadata()

        if not self.chunks:
            print(f"⚠️ 경고: 청크 데이터가 비어있습니다")

    def _load_metadata(self):
        """메타데이터 로드"""
        try:
            meta_path = self.index_path / 'metadata.json'

            print(f"🔍 메타데이터 경로: {meta_path}")
            print(f"📂 경로 존재 여부: {meta_path.exists()}")

            if not meta_path.exists():
                print(f"❌ 메타데이터 파일 없음: {meta_path}")
                return

            with open(meta_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.chunks = data.get('chunks', [])

            if self.chunks:
                print(f"✅ 메타데이터 로드 성공: {len(self.chunks)}개 청크")
                print(f"   - 첫 번째 청크 길이: {len(self.chunks[0])}자")
            else:
                print(f"⚠️ 메타데이터에 청크 없음")

        except json.JSONDecodeError as e:
            print(f"❌ 메타데이터 JSON 파싱 오류: {e}")
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
            query_embedding = embeddings_model.embed_query(query)

            print(f"✅ 쿼리 임베딩 생성: {len(query_embedding)}차원")
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
            if not self.chunks:
                print(f"❌ 청크 데이터 없음")
                return []

            # 쿼리 임베딩 생성
            q_emb = self.embed_query(query, embedding_provider)
            if not q_emb:
                print("❌ 쿼리 임베딩 실패")
                return []

            # FAISS 인덱스 로드
            import faiss
            idx_file = self.index_path / 'index.faiss'

            if not idx_file.exists():
                print(f"❌ FAISS 인덱스 파일 없음: {idx_file}")
                return []

            print(f"📂 FAISS 인덱스 로드: {idx_file}")
            index = faiss.read_index(str(idx_file))
            print(f"✅ FAISS 인덱스 로드 성공")

            # 검색 실행
            D, I = index.search(
                np.array([q_emb], dtype=np.float32),
                min(top_k, len(self.chunks))
            )

            print(f"🔍 FAISS 검색: top_k={top_k}, 반환된 결과: {len(I[0])}개")

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
                print(f"✅ {len(results)}개 청크 검색됨")
            else:
                print(f"⚠️ 검색 결과 없음")

            return results

        except Exception as e:
            print(f"❌ 검색 오류: {e}")
            import traceback
            traceback.print_exc()
            return []
