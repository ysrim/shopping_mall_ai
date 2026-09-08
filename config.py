# config.py
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

PROJECT_ROOT = Path(__file__).parent
SAMPLE_DATA_PATH = PROJECT_ROOT / "sample_data"
DATA_DIR = PROJECT_ROOT / "data"
CACHE_DIR = PROJECT_ROOT / "cache"

# 디렉토리 자동 생성
for d in [DATA_DIR, CACHE_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# 파일 경로
DB_PATH = DATA_DIR / "chat.db"
FAISS_INDEX_PATH = DATA_DIR / "faiss_index"
EMBEDDING_CACHE_PATH = CACHE_DIR / "embeddings.pkl"
STATE_FILE_PATH = DATA_DIR / "app_state.json"

# ==================== Google Gemini API ====================
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GENERATION_MODEL = "gemini-3.5-flash-lite"
EMBEDDING_MODEL = "gemini-embedding-2"  # ✅ 반드시 이것! (gemini-embedding-001 아님)
EMBEDDING_TASK = "retrieval_document"
EMBEDDING_DIM = 3072  # ✅ embedding-001은 768차원

# ==================== Ollama 로컬 모델 ====================
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_GENERATION_MODEL = "qwen2.5:14b-instruct-q4_0"
OLLAMA_EMBEDDING_MODEL = "nomic-embed-text"
OLLAMA_EMBEDDING_DIM = 384
OLLAMA_TIMEOUT = 60

# ==================== 프로바이더 선택 ====================
LLM_PROVIDER = "ollama"           # ✅ ollama로 변경
EMBEDDING_PROVIDER = "ollama"     # ✅ ollama로 변경

# ==================== LLM 생성 파라미터 ====================
TEMPERATURE = 0.3
MAX_TOKENS = 2000
NUM_WORKERS = 4

# ==================== 데이터베이스 설정 ====================
DATABASE_TIMEOUT = 10
ENABLE_CACHING = True
