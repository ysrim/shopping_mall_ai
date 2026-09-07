import google.generativeai as genai
from config import (
    GOOGLE_API_KEY, GENERATION_MODEL, EMBEDDING_MODEL,
    EMBEDDING_TASK, EMBEDDING_DIM, EMBEDDING_CACHE_PATH
)
from pathlib import Path
import pickle
from concurrent.futures import ThreadPoolExecutor


class EmbeddingCache:
    def __init__(self, cache_path):
        """캐시 초기화"""
        self.cache_path = Path(cache_path)
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        self.cache = self.load()

    def load(self):
        """캐시 파일에서 로드"""
        try:
            if self.cache_path.exists():
                with open(self.cache_path, 'rb') as f:
                    cache = pickle.load(f)
                    print(f"✅ Cache loaded: {len(cache)} items")
                    return cache
        except Exception as e:
            print(f"⚠️ Cache load error: {e}")
        return {}

    def save(self):
        """캐시를 파일에 저장"""
        try:
            with open(self.cache_path, 'wb') as f:
                pickle.dump(self.cache, f)
                print(f"✅ Cache saved: {len(self.cache)} items")
        except Exception as e:
            print(f"❌ Cache save error: {e}")

    def get(self, key):
        """캐시에서 값 가져오기"""
        return self.cache.get(key)

    def set(self, key, value):
        """캐시에 값 저장"""
        self.cache[key] = value
        self.save()

    def clear(self):
        """캐시 초기화"""
        self.cache = {}
        try:
            if self.cache_path.exists():
                self.cache_path.unlink()
            print("✅ Cache cleared")
        except Exception as e:
            print(f"❌ Cache clear error: {e}")


genai.configure(api_key=GOOGLE_API_KEY)
embedding_cache = EmbeddingCache(str(EMBEDDING_CACHE_PATH))


class GeminiAPI:
    """Google Gemini API 래퍼 (최신 고성능 모델)"""

    @staticmethod
    def embed(text: str, task_type: str = EMBEDDING_TASK) -> list:
        """텍스트 임베딩 (models/gemini-embedding-001)"""
        try:
            cache_key = f"{text}_{task_type}"
            cached_embedding = embedding_cache.get(cache_key)
            if cached_embedding:
                print(f"✅ Embedding from cache")
                return cached_embedding

            # models/gemini-embedding-001 사용
            response = genai.embed_content(
                model=EMBEDDING_MODEL,
                content=text,
                task_type=task_type
            )
            embedding = response['embedding']
            embedding_cache.set(cache_key, embedding)
            return embedding
        except Exception as e:
            print(f"❌ Embedding error: {e}")
            raise

    @staticmethod
    def embed_batch(texts: list, task_type: str = EMBEDDING_TASK) -> list:
        """배치 임베딩"""
        embeddings = []
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [
                executor.submit(GeminiAPI.embed, text, task_type)
                for text in texts
            ]
            for future in futures:
                try:
                    embeddings.append(future.result())
                except Exception as e:
                    print(f"❌ Batch embedding error: {e}")
                    embeddings.append([0.0] * EMBEDDING_DIM)
        return embeddings

    @staticmethod
    def generate(prompt: str, temperature: float = 0.3, max_tokens: int = 2000) -> str:
        """텍스트 생성 (gemini-3.8-flash)"""
        try:
            model = genai.GenerativeModel(GENERATION_MODEL)
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens
                )
            )
            return response.text
        except Exception as e:
            print(f"❌ Generation error: {e}")
            raise

    @staticmethod
    def generate_streaming(prompt: str, temperature: float = 0.3, max_tokens: int = 2000):
        """스트리밍 텍스트 생성"""
        try:
            model = genai.GenerativeModel(GENERATION_MODEL)
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens
                ),
                stream=True
            )
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            print(f"❌ Streaming error: {e}")
            raise

    @staticmethod
    def get_usage_stats() -> dict:
        """API 사용 통계"""
        return {
            "cache_size": len(embedding_cache.cache),
            "cache_path": str(EMBEDDING_CACHE_PATH),
            "generation_model": GENERATION_MODEL,
            "embedding_model": EMBEDDING_MODEL
        }
