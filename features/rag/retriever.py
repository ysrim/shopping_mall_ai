from pathlib import Path
from typing import List, Dict
import json
import numpy as np


class Retriever:
    """FAISS를 사용하여 문서를 검색합니다."""

    def __init__(self, embeddings_model, index_path: Path):
        """
        Retriever를 초기화합니다.

        Args:
            embeddings_model: 임베딩 모델 (Ollama, Gemini 등)
            index_path: FAISS 인덱스 경로
        """
        self.embeddings_model = embeddings_model
        self.index_path = Path(index_path)
        self.index = None
        self.chunks = []

        print(f"\n{'=' * 60}")
        print(f"🔍 Retriever 초기화")
        print(f"{'=' * 60}")
        print(f"   인덱스 경로: {self.index_path}")

        self._load_index()

        print(f"{'=' * 60}")
        print(f"   인덱스 상태: {self.index.ntotal if self.index else 'None'}개 벡터")
        print(f"   청크 수: {len(self.chunks)}개")
        print(f"{'=' * 60}\n")

    def _load_index(self) -> bool:
        """FAISS 인덱스와 청크를 로드합니다."""
        try:
            print(f"\n📂 인덱스 로드 시작")
            print(f"   경로: {self.index_path}")
            print(f"   경로 존재: {self.index_path.exists()}")

            if not self.index_path.exists():
                print(f"⚠️ 인덱스 경로가 없습니다")
                return False

            # 1. 메타데이터 로드
            print(f"\n📋 메타데이터 로드 중...")
            metadata_file = self.index_path / "metadata.json"

            if metadata_file.exists():
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                print(f"✅ 메타데이터 로드 완료:")
                print(f"   청크 수: {metadata.get('chunk_count', 0)}")
                print(f"   벡터 수: {metadata.get('vector_count', 0)}")
                print(f"   차원: {metadata.get('dimension', 0)}")
            else:
                print(f"⚠️ metadata.json이 없습니다")
                return False

            # 2. FAISS 인덱스 로드
            print(f"\n🔍 FAISS 인덱스 로드 중...")
            index_file = self.index_path / "index.faiss"

            if not index_file.exists():
                print(f"❌ index.faiss가 없습니다")
                return False

            print(f"   파일: {index_file}")
            print(f"   파일 크기: {index_file.stat().st_size} bytes")

            import faiss
            self.index = faiss.read_index(str(index_file))
            print(f"✅ FAISS 인덱스 로드 완료")
            print(f"   벡터 수: {self.index.ntotal}")

            # 3. 청크 로드
            print(f"\n📝 청크 로드 중...")
            chunks_file = self.index_path / "chunks.json"

            if not chunks_file.exists():
                print(f"❌ chunks.json이 없습니다")
                return False

            print(f"   파일: {chunks_file}")
            print(f"   파일 크기: {chunks_file.stat().st_size} bytes")

            with open(chunks_file, 'r', encoding='utf-8') as f:
                self.chunks = json.load(f)

            print(f"✅ 청크 로드 완료: {len(self.chunks)}개")
            if self.chunks:
                print(f"   첫 번째 청크: {self.chunks[0][:100]}...")
                print(f"   마지막 청크: {self.chunks[-1][:100]}...")

            # 4. 검증
            print(f"\n🔍 인덱스 검증")
            if len(self.chunks) != self.index.ntotal:
                print(f"⚠️ 청크 수({len(self.chunks)})와 벡터 수({self.index.ntotal})가 불일치!")
                return False

            print(f"✅ 인덱스 검증 완료")
            print(f"✅ 인덱스 로드 성공!\n")

            return True

        except Exception as e:
            print(f"❌ 인덱스 로드 실패: {e}")
            import traceback
            print(traceback.format_exc())
            return False

    def retrieve(self, query: str, top_k: int = 2) -> List[Dict]:
        """
        쿼리와 유사한 문서를 검색합니다.

        Args:
            query: 검색 쿼리
            top_k: 상위 K개 결과

        Returns:
            검색 결과 리스트 ({"chunk": 텍스트, "distance": 거리})
        """
        try:
            print(f"\n{'=' * 60}")
            print(f"🔍 문서 검색 시작")
            print(f"{'=' * 60}")
            print(f"쿼리: {query}")
            print(f"상위 K: {top_k}")

            # 인덱스 상태 확인
            print(f"\n📊 FAISS 인덱스 정보:")
            if self.index is None:
                print(f"❌ 인덱스가 None입니다")
                return []

            print(f"   - 인덱스 차원: {self.index.d if hasattr(self.index, 'd') else 'unknown'}")
            print(f"   - 저장된 벡터 개수: {self.index.ntotal}")
            print(f"   - 로드된 청크 개수: {len(self.chunks)}")

            if len(self.chunks) == 0:
                print(f"❌ 청크가 비어있습니다!")
                return []

            if self.index.ntotal == 0:
                print(f"❌ 인덱스에 벡터가 없습니다!")
                return []

            # 쿼리 임베딩 생성
            print(f"\n📝 쿼리 임베딩 생성 중...")
            query_embedding = self.embeddings_model.embed_query(query)
            print(f"   임베딩 차원: {len(query_embedding)}")
            print(f"   임베딩 샘플: {query_embedding[:5]}")

            # FAISS 검색
            query_array = np.array([query_embedding], dtype=np.float32)

            print(f"\n🔍 FAISS 검색 실행 중...")
            distances, indices = self.index.search(query_array, min(top_k, self.index.ntotal))

            print(f"✅ FAISS 검색 완료: {len(indices[0])}개 결과")
            for i, idx in enumerate(indices[0]):
                if 0 <= idx < len(self.chunks):
                    chunk_len = len(self.chunks[idx])
                else:
                    chunk_len = 0
                print(f"   ✅ 청크 {idx}: 거리={distances[0][i]:.4f}, 길이={chunk_len}자")

            # 결과 처리
            results = []
            print(f"\n📋 청크 추출 중...")
            for i, idx in enumerate(indices[0]):
                print(f"\n   [{i + 1}] 인덱스: {idx}")
                print(f"       범위 확인: {0} <= {idx} < {len(self.chunks)}")

                if 0 <= idx < len(self.chunks):
                    chunk = self.chunks[idx]
                    distance = float(distances[0][i])

                    print(f"       ✅ 청크 발견!")
                    print(f"       내용: {chunk[:80]}...")
                    print(f"       길이: {len(chunk)}자")
                    print(f"       거리: {distance:.4f}")

                    results.append({
                        "chunk": chunk,
                        "distance": distance
                    })
                else:
                    print(f"       ❌ 인덱스 범위 초과: {idx}")

            print(f"\n{'=' * 60}")
            print(f"✅ {len(results)}개 문서 검색 완료")
            for i, r in enumerate(results, 1):
                print(f"   [{i}] 길이: {len(r['chunk'])}자, 거리: {r['distance']:.4f}")
            print(f"{'=' * 60}\n")

            return results

        except Exception as e:
            print(f"\n❌ 검색 실패: {e}")
            import traceback
            print(traceback.format_exc())
            return []
