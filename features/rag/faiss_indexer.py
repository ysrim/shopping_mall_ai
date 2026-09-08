# features/rag/faiss_indexer.py
import json
from pathlib import Path
from typing import List, Dict
import numpy as np
from config import FAISS_INDEX_PATH


class FAISSIndexBuilder:
    """FAISS 인덱스 생성 및 관리"""

    def __init__(self, index_path: Path = FAISS_INDEX_PATH):
        """
        초기화

        Args:
            index_path: FAISS 인덱스 저장 경로
        """
        self.index_path = Path(index_path)

    def build(self, chunks: List[str], embeddings: List[List[float]], documents: List[Dict]) -> bool:
        """
        FAISS 인덱스 생성

        Args:
            chunks: 청크 텍스트 리스트
            embeddings: 임베딩 벡터 리스트
            documents: 원본 문서 리스트

        Returns:
            성공 여부
        """
        try:
            if not chunks or not embeddings:
                print("❌ 청크 또는 임베딩 데이터 없음")
                return False

            if len(chunks) != len(embeddings):
                print(f"❌ 청크와 임베딩 개수 불일치: {len(chunks)} vs {len(embeddings)}")
                return False

            print("🔄 FAISS 인덱스 생성 중...")
            import faiss

            # 인덱스 디렉토리 생성
            self.index_path.mkdir(parents=True, exist_ok=True)

            # FAISS 인덱스 생성
            dim = len(embeddings[0])
            arr = np.array(embeddings, dtype=np.float32)
            index = faiss.IndexFlatL2(dim)
            index.add(arr)

            # 메타데이터 저장
            metadata = {
                'chunks': chunks,
                'documents': documents,
                'dimension': dim,
                'chunk_count': len(chunks),
                'embedding_count': len(embeddings)
            }

            metadata_path = self.index_path / 'metadata.json'
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)

            print(f"✅ 메타데이터 저장됨: {metadata_path}")

            # FAISS 인덱스 저장
            index_path_faiss = self.index_path / 'index.faiss'
            faiss.write_index(index, str(index_path_faiss))
            print(f"✅ FAISS 인덱스 저장됨: {index_path_faiss}")

            # 임베딩 벡터 저장
            embeddings_path = self.index_path / 'embeddings.npy'
            np.save(str(embeddings_path), arr)
            print(f"✅ 임베딩 벡터 저장됨: {embeddings_path}")

            # 최종 확인
            print(f"✅ FAISS 인덱스 생성 완료!")
            print(f"   - 청크: {len(chunks)}개")
            print(f"   - 임베딩: {len(embeddings)}개")
            print(f"   - 차원: {dim}")

            return True

        except Exception as e:
            print(f"❌ 인덱스 생성 오류: {e}")
            import traceback
            traceback.print_exc()
            return False

    def verify_index(self) -> bool:
        """
        인덱스 검증

        Returns:
            인덱스 유효 여부
        """
        try:
            metadata_path = self.index_path / 'metadata.json'
            index_path_faiss = self.index_path / 'index.faiss'

            if not metadata_path.exists():
                print(f"❌ 메타데이터 파일 없음: {metadata_path}")
                return False

            if not index_path_faiss.exists():
                print(f"❌ FAISS 인덱스 파일 없음: {index_path_faiss}")
                return False

            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)

            chunks_count = len(metadata.get('chunks', []))
            embedding_count = metadata.get('embedding_count', 0)

            if chunks_count == 0:
                print(f"❌ 메타데이터에 청크 데이터 없음")
                return False

            print(f"✅ 인덱스 검증 완료:")
            print(f"   - 청크: {chunks_count}개")
            print(f"   - 임베딩: {embedding_count}개")
            print(f"   - 차원: {metadata.get('dimension')}차원")

            return True

        except Exception as e:
            print(f"❌ 인덱스 검증 오류: {e}")
            return False
