# features/shared/api.py
import pickle
from pathlib import Path
from typing import List, Optional
import time
import requests

from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.llms import Ollama
from langchain_community.embeddings import OllamaEmbeddings

from config import (
    GOOGLE_API_KEY,
    GENERATION_MODEL,
    EMBEDDING_MODEL,
    EMBEDDING_TASK,
    EMBEDDING_DIM,
    OLLAMA_BASE_URL,
    OLLAMA_GENERATION_MODEL,
    OLLAMA_EMBEDDING_MODEL,
    OLLAMA_EMBEDDING_DIM,
    OLLAMA_TIMEOUT,
    TEMPERATURE,
    EMBEDDING_CACHE_PATH,
    LLM_PROVIDER,
    ENABLE_CACHING,
)


# ===== 임베딩 캐시 =====
class EmbeddingCache:
    """임베딩 캐시 관리"""

    def __init__(self, cache_path: Path = EMBEDDING_CACHE_PATH):
        self.cache_path = Path(cache_path)
        self.cache = self._load_cache()

    def _load_cache(self) -> dict:
        """캐시 로드"""
        if self.cache_path.exists():
            try:
                with open(self.cache_path, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                print(f"⚠️ 캐시 로드 실패: {e}")
                return {}
        return {}

    def save_cache(self):
        """캐시 저장"""
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.cache_path, 'wb') as f:
            pickle.dump(self.cache, f)

    def get(self, key: str) -> Optional[List[float]]:
        """캐시에서 임베딩 조회"""
        return self.cache.get(key)

    def set(self, key: str, value: List[float]):
        """캐시에 임베딩 저장"""
        self.cache[key] = value
        if ENABLE_CACHING:
            self.save_cache()

    def clear(self):
        """캐시 초기화"""
        self.cache.clear()
        self.save_cache()


# ===== Gemini API =====
class GeminiAPI:
    """Google Gemini 3.8 Flash API (클라우드)"""

    def __init__(self):
        """Gemini API 초기화"""
        self.embedding_cache = EmbeddingCache()
        try:
            self.llm = ChatGoogleGenerativeAI(
                model=GENERATION_MODEL,  # gemini-3.8-flash
                temperature=TEMPERATURE,
                google_api_key=GOOGLE_API_KEY
            )
            self._embeddings = GoogleGenerativeAIEmbeddings(
                model=EMBEDDING_MODEL,
                task_type=EMBEDDING_TASK,
                google_api_key=GOOGLE_API_KEY
            )
            print(f"✅ Gemini API 로드됨 (모델: {GENERATION_MODEL})")
        except Exception as e:
            print(f"❌ Gemini API 초기화 실패: {e}")
            raise

    def get_llm(self):
        """LLM 반환"""
        return self.llm

    def get_embeddings(self):
        """임베딩 모델 반환"""
        return self._embeddings

    def get_embedding_dimension(self) -> int:
        """임베딩 차원"""
        return EMBEDDING_DIM


# ===== Ollama API =====
class OllamaAPI:
    """Ollama 로컬 모델 API"""

    def __init__(self, max_retries: int = 5, retry_delay: int = 2):
        """
        Ollama API 초기화

        Args:
            max_retries: 최대 재시도 횟수
            retry_delay: 재시도 간격 (초)
        """
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        try:
            self._test_connection_with_retry()
            self.llm = Ollama(
                base_url=OLLAMA_BASE_URL,
                model=OLLAMA_GENERATION_MODEL,
                temperature=TEMPERATURE,
                timeout=OLLAMA_TIMEOUT
            )
            self._embeddings = OllamaEmbeddings(
                base_url=OLLAMA_BASE_URL,
                model=OLLAMA_EMBEDDING_MODEL
            )
            print("✅ Ollama API 로드됨")
        except Exception as e:
            raise RuntimeError(
                f"❌ Ollama 연결 실패: {e}\n"
                f"✅ 해결: 터미널에서 'ollama serve' 또는 'brew services start ollama' 실행"
            )

    def _test_connection_with_retry(self):
        """재시도 로직을 포함한 연결 테스트"""
        for attempt in range(self.max_retries):
            try:
                response = requests.get(
                    f"{OLLAMA_BASE_URL}/api/tags",
                    timeout=5
                )
                if response.status_code == 200:
                    print(f"✅ Ollama 연결 성공 (시도: {attempt + 1}/{self.max_retries})")
                    return
            except requests.exceptions.ConnectionError:
                if attempt < self.max_retries - 1:
                    print(f"⏳ Ollama 연결 대기 중... ({attempt + 1}/{self.max_retries})")
                    time.sleep(self.retry_delay)
                else:
                    raise

        raise RuntimeError("Ollama 서버에 연결할 수 없습니다")

    def get_llm(self):
        """LLM 반환"""
        return self.llm

    def get_embeddings(self):
        """임베딩 모델 반환"""
        return self._embeddings

    def get_embedding_dimension(self) -> int:
        """임베딩 차원"""
        return OLLAMA_EMBEDDING_DIM


# ===== LLM 팩토리 =====
class LLMFactory:
    """LLM & 임베딩 API 팩토리 (싱글톤)"""

    _instance = None
    _current_llm_provider = None
    _llm_instance = None
    _current_embedding_provider = None
    _embedding_instance = None

    def __new__(cls):
        """싱글톤 패턴"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @staticmethod
    def create_llm_api(provider: str = None):
        """
        LLM API 생성

        Args:
            provider: "gemini" 또는 "ollama"

        Returns:
            LLM API 인스턴스
        """
        factory = LLMFactory()

        if provider is None:
            provider = LLM_PROVIDER

        if factory._current_llm_provider == provider and factory._llm_instance is not None:
            return factory._llm_instance

        try:
            if provider == "ollama":
                factory._llm_instance = OllamaAPI()
            else:
                factory._llm_instance = GeminiAPI()

            factory._current_llm_provider = provider
            return factory._llm_instance

        except Exception as e:
            print(f"❌ LLM API 생성 실패: {e}")
            if provider != "gemini":
                print("⚠️ Gemini로 자동 전환")
                factory._llm_instance = GeminiAPI()
                factory._current_llm_provider = "gemini"
                return factory._llm_instance
            raise

    @staticmethod
    def create_embedding_api(self, provider=None):
        """임베딩 프로바이더 선택"""
        if provider is None:
            provider = EMBEDDING_PROVIDER

        provider = provider.lower()

        if provider == "ollama":
            try:
                print(f"🔗 Ollama 임베딩 API 연결 중... ({OLLAMA_EMBEDDING_MODEL})")
                return OllamaAPI()
            except Exception as e:
                print(f"❌ Ollama 연결 실패, Gemini로 폴백: {str(e)}")
                return GeminiAPI()
        else:
            print(f"🔗 Gemini 임베딩 API 로드 중... ({EMBEDDING_MODEL})")
            return GeminiAPI()


# ===== 싱글톤 인스턴스 =====
llm_factory = LLMFactory()
