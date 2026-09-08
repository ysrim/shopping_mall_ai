import json
import pickle
import requests
from pathlib import Path
from typing import List, Optional
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_ollama import OllamaLLM
from langchain_ollama.embeddings import OllamaEmbeddings

from config import (
    GOOGLE_API_KEY,
    GENERATION_MODEL,
    EMBEDDING_MODEL,
    EMBEDDING_TASK,
    EMBEDDING_DIM,
    EMBEDDING_CACHE_PATH,
    ENABLE_CACHING,
    LLM_PROVIDER,
    EMBEDDING_PROVIDER,
    TEMPERATURE,
    MAX_TOKENS,
    OLLAMA_BASE_URL,
    OLLAMA_GENERATION_MODEL,
    OLLAMA_EMBEDDING_MODEL,
    OLLAMA_EMBEDDING_DIM,
    OLLAMA_TIMEOUT
)


# ==================== Embedding Cache ====================
class EmbeddingCache:
    """임베딩 캐시 관리"""

    def __init__(self, cache_path=EMBEDDING_CACHE_PATH):
        self.cache_path = Path(cache_path)
        self.cache = self._load_cache()

    def _load_cache(self):
        if self.cache_path.exists():
            try:
                with open(self.cache_path, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                print(f"⚠️ 캐시 로드 실패: {str(e)}")
                return {}
        return {}

    def get(self, key):
        return self.cache.get(key)

    def set(self, key, value):
        self.cache[key] = value
        self._save_cache()

    def _save_cache(self):
        try:
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.cache_path, 'wb') as f:
                pickle.dump(self.cache, f)
        except Exception as e:
            print(f"⚠️ 캐시 저장 실패: {str(e)}")

    def clear(self):
        self.cache = {}
        if self.cache_path.exists():
            self.cache_path.unlink()
        print("✅ 캐시 삭제 완료")


# ==================== Gemini API ====================
class GeminiAPI:
    """Google Gemini API 래퍼"""

    def __init__(self):
        if not GOOGLE_API_KEY:
            raise ValueError("❌ GOOGLE_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.")

        try:
            self.llm = ChatGoogleGenerativeAI(
                model=GENERATION_MODEL,
                api_key=GOOGLE_API_KEY,
                max_tokens=MAX_TOKENS,
                convert_system_message_to_human=True
            )

            self.embeddings = GoogleGenerativeAIEmbeddings(
                model=EMBEDDING_MODEL,
                api_key=GOOGLE_API_KEY,
                task_type=EMBEDDING_TASK
            )

            self.embedding_cache = EmbeddingCache()
            print(f"✅ Gemini API 로드됨 (모델: {GENERATION_MODEL})")

        except Exception as e:
            raise RuntimeError(f"❌ Gemini API 초기화 실패: {str(e)}")

    def get_llm(self):
        return self.llm

    def get_embeddings(self):
        return self.embeddings


# ==================== Ollama API ====================
class OllamaAPI:
    """Ollama 로컬 모델 래퍼"""

    def __init__(self, max_retries=5):
        self.base_url = OLLAMA_BASE_URL
        self.max_retries = max_retries

        # Ollama 연결 재시도
        if not self._check_connection():
            raise RuntimeError(f"❌ Ollama 서버에 연결할 수 없습니다. ({self.base_url})")

        try:
            self.llm = OllamaLLM(
                model=OLLAMA_GENERATION_MODEL,
                base_url=self.base_url,
                temperature=TEMPERATURE,
                num_ctx=2048,
            )

            self.embeddings = OllamaEmbeddings(
                model=OLLAMA_EMBEDDING_MODEL,
                base_url=self.base_url,
            )

            self.embedding_cache = EmbeddingCache()
            print(f"✅ Ollama API 로드됨 (모델: {OLLAMA_GENERATION_MODEL}, 임베딩: {OLLAMA_EMBEDDING_MODEL})")

        except Exception as e:
            raise RuntimeError(f"❌ Ollama API 초기화 실패: {str(e)}")

    def _check_connection(self):
        """Ollama 서버 연결 확인"""
        for attempt in range(1, self.max_retries + 1):
            try:
                response = requests.get(f"{self.base_url}/api/tags", timeout=5)
                if response.status_code == 200:
                    print(f"✅ Ollama 연결 성공 (시도 {attempt}/{self.max_retries})")
                    return True
            except Exception as e:
                print(f"⚠️ Ollama 연결 시도 {attempt}/{self.max_retries} 실패: {str(e)}")
                if attempt < self.max_retries:
                    import time
                    time.sleep(2)

        return False

    def get_llm(self):
        return self.llm

    def get_embeddings(self):
        return self.embeddings


# ==================== LLM Factory ====================
class LLMFactory:
    """LLM 및 임베딩 API 팩토리 (싱글톤)"""
    _instance = None
    _llm_instance = None
    _embedding_instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LLMFactory, cls).__new__(cls)
        return cls._instance

    def create_llm_api(self, provider=None):
        """LLM API 생성"""
        if provider is None:
            provider = LLM_PROVIDER

        provider = provider.lower()

        if provider == "ollama":
            try:
                print(f"🔗 Ollama LLM 연결 중... ({OLLAMA_GENERATION_MODEL})")
                return OllamaAPI()
            except Exception as e:
                print(f"❌ Ollama 연결 실패, Gemini로 폴백: {str(e)}")
                return GeminiAPI()
        else:
            try:
                print(f"🔗 Gemini LLM 로드 중... ({GENERATION_MODEL})")
                return GeminiAPI()
            except Exception as e:
                print(f"❌ Gemini 로드 실패: {str(e)}")
                raise

    def create_embedding_api(self, provider=None):
        """임베딩 API 생성"""
        if provider is None:
            provider = EMBEDDING_PROVIDER

        provider = provider.lower()

        if provider == "ollama":
            try:
                print(f"🔗 Ollama 임베딩 API 연결 중... ({OLLAMA_EMBEDDING_MODEL})")
                return OllamaAPI()
            except Exception as e:
                print(f"❌ Ollama 임베딩 연결 실패, Gemini로 폴백: {str(e)}")
                return GeminiAPI()
        else:
            try:
                print(f"🔗 Gemini 임베딩 API 로드 중... ({EMBEDDING_MODEL})")
                return GeminiAPI()
            except Exception as e:
                print(f"❌ Gemini 임베딩 로드 실패: {str(e)}")
                raise


# 싱글톤 인스턴스
llm_factory = LLMFactory()
