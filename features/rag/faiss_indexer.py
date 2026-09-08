from pathlib import Path
import numpy as np
import faiss
from typing import List
import json
from config import FAISS_INDEX_PATH


class FAISSIndexBuilder:
    def __init__(self, dimension: int, index_path: Path = None):
        """
        FAISS 인덱스 빌더 초기화

        Args:
            dimension: 임베딩 차원 (예: 768)
            index_path: 인덱스 저장 경로 (기본: FAISS_INDEX_PATH)
        """
        self.dimension = dimension
        self.index_path = Path(index_path) if index_path else FAISS_INDEX_PATH
        self.index = None
        self.chunks = []

        print(f"📊 FAISSIndexBuilder 초기화")
        print(f"   - 차원: {self.dimension}")
        print(f"   - 저장 경로: {self.index_path}")

    def build_index(self, chunks: List[str], embeddings: List[List[float]]) -> None:
        """
        FAISS 인덱스 생성

        Args:
            chunks: 텍스트 청크 리스트
            embeddings: 임베딩 벡터 리스트
        """
        if not chunks or not embeddings:
            raise ValueError("❌ chunks 또는 embeddings이 비어있습니다")

        if len(chunks) != len(embeddings):
            raise ValueError(f"❌ chunks({len(chunks)})와 embeddings({len(embeddings)}) 길이 불일치")

        print(f"\n📊 FAISS 인덱스 생성 중...")
        print(f"   - 청크: {len(chunks)}개")
        print(f"   - 임베딩: {len(embeddings)}개")
        print(f"   - 차원: {self.dimension}")

        # embeddings이 numpy array가 아니면 변환
        if not isinstance(embeddings, np.ndarray):
            embeddings = np.array(embeddings, dtype=np.float32)
        else:
            embeddings = embeddings.astype(np.float32)

        # 차원 확인
        if embeddings.shape[1] != self.dimension:
            raise ValueError(
                f"❌ 임베딩 차원 불일치: "
                f"예상={self.dimension}, 실제={embeddings.shape[1]}"
            )

        # FAISS 인덱스 생성
        self.index = faiss.IndexFlatL2(self.dimension)
        self.index.add(embeddings)
        self.chunks = chunks

        print(f"✅ FAISS 인덱스 생성 완료")
        print(f"   - 저장된 벡터: {self.index.ntotal}개")

    def save_index(self, index_path: Path = None) -> None:
        """
        인덱스를 디스크에 저장

        Args:
            index_path: 저장 경로 (기본: self.index_path)
        """
        if self.index is None:
            raise ValueError("❌ 인덱스가 생성되지 않았습니다")

        save_path = Path(index_path) if index_path else self.index_path
        save_path.mkdir(parents=True, exist_ok=True)

        print(f"\n💾 인덱스 저장 중...")

        try:
            # FAISS 인덱스 저장
            index_file = save_path / "index.faiss"
            faiss.write_index(self.index, str(index_file))
            print(f"✅ FAISS 인덱스 저장됨: {index_file}")

            # 메타데이터 저장
            metadata = {
                "chunks": self.chunks,
                "dimension": self.dimension,
                "chunk_count": len(self.chunks),
                "embedding_count": self.index.ntotal,
            }

            metadata_file = save_path / "metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            print(f"✅ 메타데이터 저장됨: {metadata_file}")

            # embeddings.npy도 저장 (선택사항)
            embeddings_file = save_path / "embeddings.npy"
            # 실제 임베딩은 FAISS 인덱스에서 추출 (간단히 하기 위해 생략)
            print(f"✅ 인덱스 저장 완료: {save_path}")

        except Exception as e:
            print(f"❌ 인덱스 저장 실패: {str(e)}")
            raise

    def load_index(self, index_path: Path = None) -> bool:
        """
        디스크에서 인덱스 로드

        Args:
            index_path: 로드 경로 (기본: self.index_path)

        Returns:
            성공 여부
        """
        load_path = Path(index_path) if index_path else self.index_path
        index_file = load_path / "index.faiss"
        metadata_file = load_path / "metadata.json"

        if not index_file.exists() or not metadata_file.exists():
            print(f"⚠️ 인덱스 파일 없음: {load_path}")
            return False

        try:
            self.index = faiss.read_index(str(index_file))

            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)

            self.chunks = metadata.get("chunks", [])
            print(f"✅ 인덱스 로드 완료: {len(self.chunks)}개 청크")
            return True

        except Exception as e:
            print(f"❌ 인덱스 로드 실패: {str(e)}")
            return False

    def search(self, query_embedding: List[float], top_k: int = 2) -> List[dict]:
        """
        FAISS 인덱스에서 유사한 청크 검색

        Args:
            query_embedding: 쿼리 임베딩 벡터
            top_k: 상위 K개 결과

        Returns:
            검색 결과 리스트
        """
        if self.index is None:
            raise ValueError("❌ 인덱스가 로드되지 않았습니다")

        query_embedding = np.array([query_embedding], dtype=np.float32)
        distances, indices = self.index.search(query_embedding, top_k)

        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.chunks):
                results.append({
                    "chunk": self.chunks[idx],
                    "distance": float(distances[0][i]),
                    "index": int(idx)
                })

        return results
