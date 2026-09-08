# features/rag/embedding_generator.py
from typing import List
import numpy as np


class EmbeddingGenerator:
    """텍스트 임베딩 생성"""

    def __init__(self, embeddings_model):
        """
        초기화

        Args:
            embeddings_model: LangChain 임베딩 모델
        """
        self.embeddings = embeddings_model

    def generate(self, texts: List[str]) -> List[List[float]]:
        """
        텍스트 임베딩 생성

        Args:
            texts: 텍스트 리스트

        Returns:
            임베딩 벡터 리스트
        """
        if not texts:
            return []

        try:
            print(f"🔄 {len(texts)}개 텍스트에 대한 임베딩 생성 중...")

            # LangChain의 embed_documents 메서드 사용
            embeddings = self.embeddings.embed_documents(texts)

            print(f"✅ 임베딩 생성 완료: {len(embeddings)}개")
            return embeddings

        except Exception as e:
            print(f"❌ 임베딩 생성 실패: {e}")
            return []
