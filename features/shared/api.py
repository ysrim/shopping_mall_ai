import json
import pickle
from pathlib import Path
import google.generativeai as genai
from config import GOOGLE_API_KEY, EMBEDDING_MODEL, EMBEDDING_TASK, EMBEDDING_DIM, EMBEDDING_CACHE_PATH, ENABLE_CACHING, \
    GENERATION_MODEL

genai.configure(api_key=GOOGLE_API_KEY)


class EmbeddingCache:
    """임베딩 캐시 관리"""

    def __init__(self, cache_path: Path = EMBEDDING_CACHE_PATH):
        self.cache_path = cache_path
        self.cache = self._load_cache()

    def _load_cache(self) -> dict:
        """캐시 파일 로드"""
        try:
            if ENABLE_CACHING and self.cache_path.exists():
                with open(self.cache_path, 'rb') as f:
                    return pickle.load(f)
        except Exception as e:
            print(f"⚠️ Cache load error: {e}")
        return {}

    def get(self, text: str):
        """캐시에서 조회"""
        return self.cache.get(text)

    def save(self, text: str, embedding):
        """캐시에 저장"""
        if not ENABLE_CACHING:
            return

        try:
            self.cache[text] = embedding
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.cache_path, 'wb') as f:
                pickle.dump(self.cache, f)
        except Exception as e:
            print(f"⚠️ Cache save error: {e}")

    def clear(self):
        """캐시 전체 삭제"""
        try:
            self.cache = {}
            if self.cache_path.exists():
                self.cache_path.unlink()
            print("✅ Cache cleared")
        except Exception as e:
            print(f"❌ Cache clear error: {e}")


class GeminiAPI:
    """Gemini API 래퍼"""

    def __init__(self):
        self.embedding_cache = EmbeddingCache()

    @staticmethod
    def embed(text: str):
        """단일 임베딩"""
        try:
            response = genai.embed_content(
                model=EMBEDDING_MODEL,
                content=text,
                task_type=EMBEDDING_TASK
            )
            return response['embedding']
        except Exception as e:
            print(f"❌ Embedding error: {e}")
            return None

    def embed_batch(self, texts: list):
        """배치 임베딩"""
        embeddings = []

        for text in texts:
            cached = self.embedding_cache.get(text)
            if cached:
                embeddings.append(cached)
            else:
                emb = self.embed(text)
                if emb:
                    embeddings.append(emb)
                    self.embedding_cache.save(text, emb)
                else:
                    embeddings.append([0.0] * EMBEDDING_DIM)

        return embeddings

    @staticmethod
    def generate(prompt: str) -> str:
        """텍스트 생성"""
        try:
            model = genai.GenerativeModel(GENERATION_MODEL)
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"❌ Generation error: {e}")
            return "오류가 발생했습니다."

    @staticmethod
    def generate_streaming(prompt: str):
        """스트리밍 생성"""
        try:
            model = genai.GenerativeModel(GENERATION_MODEL)
            response = model.generate_content(prompt, stream=True)
            for chunk in response:
                yield chunk.text
        except Exception as e:
            print(f"❌ Streaming error: {e}")
            yield "오류가 발생했습니다."
