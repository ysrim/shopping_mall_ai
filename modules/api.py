# modules/api.py
import google.generativeai as genai
from config import (
    GOOGLE_API_KEY, GENERATION_MODEL, EMBEDDING_MODEL,
    EMBEDDING_TASK, EMBEDDING_DIM, EMBEDDING_CACHE_PATH, NUM_WORKERS
)
from pathlib import Path
import pickle
from concurrent.futures import ThreadPoolExecutor

class EmbeddingCache:
    """임베딩 캐시 관리"""
    def __init__(self, cache_path):
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
        except Exception as e:
            print(f"❌ Cache save error: {e}")

    def get(self, key):
        return self.cache.get(key)

    def set(self, key, value):
        self.cache[key] = value
        self.save()

    def clear(self):
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
    """Google Gemini API 래퍼"""

    @staticmethod
    def embed(text: str, task_type: str = EMBEDDING_TASK) -> list:
        """텍스트 임베딩"""
        try:
            cache_key = f"{text}_{task_type}"
            cached_embedding = embedding_cache.get(cache_key)
            if cached_embedding:
                return cached_embedding

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
            return None

    @staticmethod
    def embed_batch(texts: list, task_type: str = EMBEDDING_TASK) -> list:
        """배치 임베딩"""
        embeddings = []
        with ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
            futures = [
                executor.submit(GeminiAPI.embed, text, task_type)
                for text in texts
            ]
            for future in futures:
                try:
                    result = future.result()
                    if result:
                        embeddings.append(result)
                    else:
                        embeddings.append([0.0] * EMBEDDING_DIM)
                except Exception as e:
                    print(f"❌ Batch error: {e}")
                    embeddings.append([0.0] * EMBEDDING_DIM)
        return embeddings

    @staticmethod
    def generate(prompt: str, temperature: float = 0.3, max_tokens: int = 2000) -> str:
        """텍스트 생성"""
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
            return "죄송합니다. 응답 생성에 실패했습니다."

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
            yield "죄송합니다. 응답 생성에 실패했습니다."
