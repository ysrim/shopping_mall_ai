from pathlib import Path
from typing import List
import numpy as np
import faiss
import json


class FAISSIndexBuilder:
    """FAISS 인덱스를 구축하고 관리합니다."""

    def __init__(self, dimension: int, index_path: Path = None):
        """
        FAISS 인덱스 빌더를 초기화합니다.

        Args:
            dimension: 임베딩 차원 (예: 768)
            index_path: 인덱스 저장 경로
        """
        self.dimension = dimension
        self.index_path = Path(index_path) if index_path else Path("data/faiss_index")
        self.index = None
        self.chunks = []

        print(f"\n{'=' * 60}")
        print(f"📊 FAISSIndexBuilder 초기화")
        print(f"{'=' * 60}")
        print(f"   차원: {self.dimension}")
        print(f"   저장 경로: {self.index_path}")
        print(f"{'=' * 60}\n")

    def build_index(self, chunks: List[str], embeddings: List[List[float]]) -> bool:
        """
        FAISS 인덱스를 구축합니다.

        Args:
            chunks: 청크 텍스트 리스트
            embeddings: 임베딩 벡터 리스트

        Returns:
            성공 여부
        """
        try:
            print(f"\n{'=' * 60}")
            print(f"📊 FAISS 인덱스 구축")
            print(f"{'=' * 60}")

            # 입력 검증
            if not chunks:
                print(f"❌ 청크가 비어있습니다")
                return False

            if not embeddings:
                print(f"❌ 임베딩이 비어있습니다")
                return False

            if len(chunks) != len(embeddings):
                print(f"❌ 청크 수({len(chunks)})와 임베딩 수({len(embeddings)})가 일치하지 않습니다")
                return False

            print(f"✅ 입력 검증 완료")
            print(f"   청크 수: {len(chunks)}")
            print(f"   임베딩 수: {len(embeddings)}")
            print(f"   첫 번째 청크: {chunks[0][:100]}...")
            print(f"   첫 번째 임베딩 길이: {len(embeddings[0])}")

            # FAISS 인덱스 생성
            print(f"\n🔧 FAISS 인덱스 생성 중...")
            self.index = faiss.IndexFlatL2(self.dimension)

            # 임베딩을 numpy 배열로 변환
            embeddings_array = np.array(embeddings, dtype=np.float32)
            print(f"   임베딩 배열 shape: {embeddings_array.shape}")

            # 인덱스에 벡터 추가
            self.index.add(embeddings_array)
            print(f"✅ FAISS 인덱스 생성 완료")
            print(f"   인덱스 크기: {self.index.ntotal}개 벡터")

            # 청크 저장
            self.chunks = chunks
            print(f"✅ 청크 저장: {len(self.chunks)}개")
            print(f"   첫 번째 청크 길이: {len(self.chunks[0])}자")
            print(f"   마지막 청크 길이: {len(self.chunks[-1])}자")

            print(f"✅ FAISS 인덱스 구축 완료!")
            print(f"{'=' * 60}\n")

            return True

        except Exception as e:
            print(f"❌ FAISS 인덱스 구축 실패: {e}")
            import traceback
            print(traceback.format_exc())
            return False

    def save_index(self, path: Path) -> bool:
        """
        FAISS 인덱스를 저장합니다.

        Args:
            path: 저장 경로

        Returns:
            성공 여부
        """
        try:
            path = Path(path)
            path.mkdir(parents=True, exist_ok=True)

            print(f"\n{'=' * 60}")
            print(f"💾 인덱스 저장")
            print(f"{'=' * 60}")
            print(f"   경로: {path}")
            print(f"   청크 수: {len(self.chunks)}")
            print(f"   벡터 수: {self.index.ntotal if self.index else 0}")

            # 1. FAISS 인덱스 저장
            if self.index is None:
                print(f"❌ 인덱스가 None입니다")
                return False

            print(f"\n📝 FAISS 인덱스 저장 중...")
            index_path = path / "index.faiss"
            faiss.write_index(self.index, str(index_path))
            print(f"✅ FAISS 인덱스 저장 완료: {index_path}")
            print(f"   파일 크기: {index_path.stat().st_size} bytes")

            # 2. 청크 저장 (매우 중요!)
            print(f"\n📝 청크 저장 중...")

            if not self.chunks:
                print(f"❌ 청크가 비어있습니다!")
                return False

            print(f"   청크 수: {len(self.chunks)}")
            print(f"   첫 번째 청크 길이: {len(self.chunks[0])}자")
            print(f"   마지막 청크 길이: {len(self.chunks[-1])}자")

            chunks_path = path / "chunks.json"
            with open(chunks_path, 'w', encoding='utf-8') as f:
                json.dump(self.chunks, f, ensure_ascii=False, indent=2)

            print(f"✅ 청크 저장 완료: {chunks_path}")
            print(f"   파일 크기: {chunks_path.stat().st_size} bytes")

            # 검증: 저장된 청크 다시 로드
            print(f"\n🔍 저장된 청크 검증 중...")
            with open(chunks_path, 'r', encoding='utf-8') as f:
                loaded_chunks = json.load(f)
            print(f"✅ 저장된 청크 검증 완료: {len(loaded_chunks)}개")
            print(f"   첫 번째 청크: {loaded_chunks[0][:100]}...")

            # 3. 메타데이터 저장
            print(f"\n📝 메타데이터 저장 중...")
            metadata = {
                "chunk_count": len(self.chunks),
                "dimension": self.dimension,
                "vector_count": self.index.ntotal,
                "timestamp": str(__import__('datetime').datetime.now())
            }
            metadata_path = path / "metadata.json"
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)

            print(f"✅ 메타데이터 저장 완료: {metadata_path}")
            print(f"   메타데이터: {metadata}")

            print(f"\n{'=' * 60}")
            print(f"✅ 인덱스 저장 완료!")
            print(f"{'=' * 60}\n")

            return True

        except Exception as e:
            print(f"❌ 인덱스 저장 실패: {e}")
            import traceback
            print(traceback.format_exc())
            return False
