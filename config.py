# config.py (전체 코드)

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ==================== 프로젝트 경로 ====================
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
CACHE_DIR = PROJECT_ROOT / "cache"

# 디렉토리 자동 생성
DATA_DIR.mkdir(exist_ok=True)
CACHE_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "chat.db"
FAISS_INDEX_PATH = DATA_DIR / "faiss_index"
EMBEDDING_CACHE_PATH = CACHE_DIR / "embeddings.pkl"
STATE_FILE_PATH = DATA_DIR / "app_state.json"
SAMPLE_DATA_PATH = PROJECT_ROOT / "sample_data"

# ==================== Google Gemini API ====================
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GENERATION_MODEL = "gemini-3.5-flash-lite"

# ==================== Ollama 로컬 모델 (고정) ====================
# ==================== Ollama 로컬 모델 (고정) ====================
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_GENERATION_MODEL = "qwen2.5:14b-instruct-q4_0"
OLLAMA_EMBEDDING_MODEL = "nomic-embed-text"
OLLAMA_EMBEDDING_DIM = 768  # nomic-embed-text는 768차원 고정
OLLAMA_TIMEOUT = 60  # ← 추가!

# ==================== 프로바이더 선택 (고정) ====================
LLM_PROVIDER = "gemini"          # LLM: Gemini 또는 Ollama 선택 가능
EMBEDDING_PROVIDER = "ollama"    # 임베딩: 🔒 Ollama로 고정!

# ==================== 임베딩 설정 (Ollama 기준) ====================
EMBEDDING_MODEL = OLLAMA_EMBEDDING_MODEL  # "nomic-embed-text"
EMBEDDING_TASK = "retrieval_document"
EMBEDDING_DIM = OLLAMA_EMBEDDING_DIM  # 768 (고정)

# ==================== LLM 생성 파라미터 ====================
TEMPERATURE = 0.3
MAX_TOKENS = 2000

# ==================== RAG 설정 ====================
NUM_WORKERS = 4
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100
TOP_K = 10  # 검색 결과 상위 K개

# ==================== 데이터베이스 설정 ====================
DATABASE_TIMEOUT = 10

# ==================== 캐싱 설정 ====================
ENABLE_CACHING = True
CACHE_EXPIRY_HOURS = 24
