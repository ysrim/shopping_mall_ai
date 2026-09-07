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

# Google Gemini API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GENERATION_MODEL = "gemini-3.8-flash"
EMBEDDING_MODEL = "models/gemini-embedding-001"
EMBEDDING_TASK = "retrieval_document"
EMBEDDING_DIM = 3072

# 생성 파라미터
TEMPERATURE = 0.3
MAX_TOKENS = 2000
NUM_WORKERS = 4

# 데이터베이스
DATABASE_TIMEOUT = 10
ENABLE_CACHING = True

# LLM 프로바이더
LLM_PROVIDER = "gemini"
