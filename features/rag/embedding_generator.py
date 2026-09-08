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
        print(f"📦 EmbeddingGenerator 초기화")
        print(f"   임베딩 모델 클래스: {self.embeddings.__class__.__name__}")
        print(f"   사용 가능한 메서드: {[m for m in dir(self.embeddings) if not m.startswith('_')][:10]}")

    def generate(self, texts: List[str]) -> List[List[float]]:
        """
        텍스트 임베딩 생성

        Args:
            texts: 텍스트 리스트

        Returns:
            임베딩 벡터 리스트
        """
        if not texts:
            print(f"⚠️ 임베딩할 텍스트 없음")
            return []

        try:
            print(f"🔄 {len(texts)}개 텍스트에 대한 임베딩 생성 중...")
            print(f"   임베딩 모델 타입: {type(self.embeddings)}")
            print(f"   첫 번째 텍스트 길이: {len(texts[0]) if texts else 0}자")

            # LangChain의 embed_documents 메서드 사용
            print(f"🔧 embed_documents 메서드 호출 중...")
            embeddings = self.embeddings.embed_documents(texts)

            print(f"✅ 임베딩 생성 완료: {len(embeddings)}개")
            if embeddings and len(embeddings) > 0:
                print(f"   첫 번째 임베딩 차원: {len(embeddings[0])}")
                print(f"   첫 번째 임베딩 값 샘플: {embeddings[0][:5]}")

            return embeddings

        except AttributeError as e:
            print(f"❌ 속성 오류 (메서드 없음): {e}")
            print(f"   사용 가능한 속성/메서드:")
            for attr in dir(self.embeddings):
                if not attr.startswith('_'):
                    print(f"      - {attr}")
            return []
        except Exception as e:
            print(f"❌ 임베딩 생성 실패: {e}")
            print(f"   오류 타입: {type(e).__name__}")
            print(f"   상세 메시지: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
