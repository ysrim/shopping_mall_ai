from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

PROJECT_ROOT = Path(__file__).parent
SAMPLE_DATA_PATH = PROJECT_ROOT / "sample_data"
DATA_DIR = PROJECT_ROOT / "data"
CACHE_DIR = PROJECT_ROOT / "cache"

# 필요한 디렉토리 자동 생성
for d in [DATA_DIR, CACHE_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# 파일 경로
DB_PATH = DATA_DIR / "chat.db"
FAISS_INDEX_PATH = DATA_DIR / "faiss_index"
EMBEDDING_CACHE_PATH = CACHE_DIR / "embeddings.pkl"
STATE_FILE_PATH = DATA_DIR / "app_state.json"

# ============ Google Gemini API (최신 고성능) ============
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

# 텍스트 생성 모델 - 최신 고성능
GENERATION_MODEL = "gemini-3.8-flash"

# 임베딩 모델 - 최신
# models/gemini-embedding-001의 기본 차원: 3072
EMBEDDING_MODEL = "models/gemini-embedding-001"
EMBEDDING_TASK = "retrieval_document"
EMBEDDING_DIM = 3072  # ← 변경: 768 → 3072 (gemini-embedding-001의 실제 차원)

# 생성 파라미터
TEMPERATURE = 0.3
MAX_TOKENS = 2000

# 재시도 설정
RETRY_MAX_ATTEMPTS = 3
RETRY_BASE_DELAY = 2

# 병렬 처리
NUM_WORKERS = 4

# 데이터베이스
ENABLE_CACHING = True
DATABASE_TIMEOUT = 10

# LLM 프로바이더
LLM_PROVIDER = "gemini"
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "qwen2.5"

# FAISS 가용성
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

STREAMLIT_CONFIG = {"showErrorDetails": False}
