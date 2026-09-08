import os
from typing import Optional
import google.generativeai as genai
import requests
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.llms import Ollama
from langchain_community.embeddings import OllamaEmbeddings
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
    OLLAMA_TIMEOUT,
)
import pickle
from pathlib import Path


# ==================== 임베딩 캐시 클래스 ====================
class EmbeddingCache:
    def __init__(self, cache_path):
        self.cache_path = Path(cache_path)
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        self.data = self._load()

    def _load(self):
        if self.cache_path.exists():
            with open(self.cache_path, 'rb') as f:
                return pickle.load(f)
        return {}

    def get(self, text: str):
        return self.data.get(text)

    def set(self, text: str, embedding):
        self.data[text] = embedding
        self._save()

    def _save(self):
        with open(self.cache_path, 'wb') as f:
            pickle.dump(self.data, f)


# ==================== Gemini API 클래스 ====================
class GeminiAPI:
    def __init__(self):
        if not GOOGLE_API_KEY:
            raise ValueError("❌ GOOGLE_API_KEY 환경변수가 설정되지 않았습니다")

        genai.configure(api_key=GOOGLE_API_KEY)
        self.llm = ChatGoogleGenerativeAI(
            model=GENERATION_MODEL,
            temperature=TEMPERATURE,
            max_output_tokens=MAX_TOKENS,
        )
        print(f"✅ Gemini API 로드됨 (모델: {GENERATION_MODEL})")

    def generate(self, prompt: str) -> str:
        """텍스트 생성"""
        try:
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            print(f"❌ Gemini 생성 오류: {str(e)}")
            return ""

    def get_llm(self):
        """LLM 객체 반환"""
        return self.llm

    def get_embeddings(self):
        """LangChain의 임베딩 모델 반환"""
        return GoogleGenerativeAIEmbeddings(
            model=EMBEDDING_MODEL,
            task_type=EMBEDDING_TASK,
        )


# ==================== Ollama API 클래스 ====================
class OllamaAPI:
    def __init__(self):
        # Ollama 서버 연결 확인
        try:
            response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
            if response.status_code != 200:
                raise ConnectionError(f"Ollama 서버 응답 오류: {response.status_code}")
            print(f"✅ Ollama 서버 연결 성공 ({OLLAMA_BASE_URL})")
        except Exception as e:
            print(f"❌ Ollama 서버 연결 실패: {str(e)}")
            raise

        self.llm = Ollama(
            base_url=OLLAMA_BASE_URL,
            model=OLLAMA_GENERATION_MODEL,
            temperature=TEMPERATURE,
        )
        print(f"✅ Ollama API 로드됨 (모델: {OLLAMA_GENERATION_MODEL})")

    def generate(self, prompt: str) -> str:
        """텍스트 생성"""
        try:
            response = self.llm.invoke(prompt)
            return response
        except Exception as e:
            print(f"❌ Ollama 생성 오류: {str(e)}")
            return ""

    def get_llm(self):
        """LLM 객체 반환"""
        return self.llm

    def get_embeddings(self):
        """LangChain의 Ollama 임베딩 모델 반환"""
        return OllamaEmbeddings(
            base_url=OLLAMA_BASE_URL,
            model=OLLAMA_EMBEDDING_MODEL,
        )


# ==================== LLM Factory ====================
class LLMFactory:
    def __init__(self):
        self._llm_instance = None
        self._embedding_instance = None

    def create_llm_api(self, provider: str = None):
        """LLM API 생성 (Gemini 또는 Ollama)"""
        if provider is None:
            provider = LLM_PROVIDER

        provider = provider.lower().strip()
        print(f"🔗 LLM API 생성: {provider}")

        if provider == "ollama":
            try:
                return OllamaAPI()
            except Exception as e:
                print(f"⚠️ Ollama 연결 실패, Gemini로 폴백: {e}")
                return GeminiAPI()
        else:
            return GeminiAPI()

    def create_embedding_api(self, provider: str = None):
        """임베딩 API 생성 (🔒 Ollama로 고정)"""
        # 임베딩은 항상 Ollama 사용!
        provider = "ollama"
        print(f"🔗 임베딩 API 생성: {provider} (고정)")

        try:
            api = OllamaAPI()
            print(f"✅ Ollama 임베딩 API 로드됨 (모델: {OLLAMA_EMBEDDING_MODEL}, 차원: {OLLAMA_EMBEDDING_DIM})")
            return api
        except Exception as e:
            print(f"❌ Ollama 임베딩 연결 실패: {e}")
            print(f"💡 Ollama 서버 실행: ollama serve")
            raise


# ==================== 싱글톤 인스턴스 ====================
llm_factory = LLMFactory()
