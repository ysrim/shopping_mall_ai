```markdown
# 🛍️ AI 쇼핑 어시스턴트 (Shopping Mall AI)

LangChain LCEL 파이프라인과 RAG(Retrieval Augmented Generation)를 활용한 Streamlit 기반 AI 쇼핑 어시스턴트입니다.

## 📋 목차

- [프로젝트 개요](#프로젝트-개요)
- [주요 기능](#주요-기능)
- [아키텍처](#아키텍처)
- [파일 구조](#파일-구조)
- [파일별 기능](#파일별-기능)
- [설치 방법](#설치-방법)
- [사용 방법](#사용-방법)
- [기술 스택](#기술-스택)
- [주요 구현 특징](#주요-구현-특징)
- [문제 해결](#문제-해결)

---

## 프로젝트 개요

이 프로젝트는 쇼핑몰 정책 문서(배송, 반품 등)를 기반으로 고객의 질문에 자동으로 답변하는 AI 챗봇입니다.

**주요 특징:**
- ✅ **Vertical Slice Architecture** – 기능별 폴더 구조로 확장성 높음
- ✅ **LCEL 파이프라인** – LangChain으로 선언적이고 간결한 코드
- ✅ **자동 카테고리 분류** – 질문 유형별 최적화된 프롬프트 자동 선택
- ✅ **RAG 시스템** – FAISS 벡터 검색으로 관련 문서 정확하게 검색
- ✅ **임베딩 캐싱** – 반복 계산 방지로 성능 최적화
- ✅ **평가 시스템** – 사용자 피드백(👍 좋음 / 😐 보통 / 👎 나쁨) 수집
- ✅ **통계 대시보드** – 대화량 및 만족도 추적

---

## 주요 기능

### 1. 💬 채팅 (Chat)
- 사용자 질문에 AI가 자동으로 응답
- RAG 기반 관련 문서 검색
- 질문 유형 자동 감지 (배송/반품/일반)
- 각 답변에 대한 사용자 평가 기능

### 2. 📊 대시보드 (Dashboard)
- 총 대화 수 표시
- 평균 평가 점수 계산
- 평가별 통계 (좋음/보통/나쁨 개수)
- 대화 이력 관리 기능

### 3. ⚙️ 설정 (Settings)
- 쇼핑몰 정책 문서 자동 로드
- FAISS 벡터 인덱스 자동 생성
- 임베딩 캐시 삭제
- 인덱스 초기화

---

## 아키텍처

### 데이터 흐름

```
사용자 질문 (채팅 페이지)
    ↓
ChatbotService.process_message()
    ↓
① RAG 검색: Retriever.retrieve()
    ↓ (FAISS에서 관련 청크 검색)
② 카테고리 감지: _detect_category()
    ↓ (배송/반품/일반 중 선택)
③ 프롬프트 선택: SHIPPING_PROMPT / RETURN_PROMPT / GENERAL_PROMPT
    ↓
④ LCEL 파이프라인 실행: prompt | llm | parser
    ↓ (LangChain으로 LLM 호출)
⑤ 응답 생성 (Gemini API)
    ↓
⑥ DB 저장: ChatDatabase.save_chat()
    ↓
⑦ UI 표시 + 평가 버튼
```

### 시스템 구성도

```
┌─────────────────────────────────────────────────────────┐
│                   Streamlit Frontend                     │
│  ┌──────────────┬──────────────┬──────────────────────┐  │
│  │   💬 Chat   │  📊 Dashboard │  ⚙️ Settings       │  │
│  └──────────────┴──────────────┴──────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                   Feature Layer                          │
│  ┌──────────────┬──────────┬─────┬──────────┬────────┐  │
│  │  Chat       │ Dashboard│ RAG │ Settings │ Shared │  │
│  │ (Service)   │  (UI)    │     │   (UI)   │(Utils) │  │
│  └──────────────┴──────────┴─────┴──────────┴────────┘  │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                   Core Services                          │
│  ┌──────────────┬──────────┬──────────────────────────┐  │
│  │  GeminiAPI   │   DB     │  State Manager          │  │
│  │ (LLM/Embed)  │(SQLite)  │  (JSON State)          │  │
│  └──────────────┴──────────┴──────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                   External Services                      │
│  ┌──────────────┬──────────────┬──────────────────────┐  │
│  │ Gemini API   │  FAISS Index │  SQLite Database    │  │
│  │ (Generation) │  (Retrieval) │  (Chat History)     │  │
│  └──────────────┴──────────────┴──────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## 파일 구조

```
shopping_mall_ai/
├── app.py                          # 메인 Streamlit 애플리케이션
├── config.py                       # 전역 설정 및 상수
├── requirements.txt                # 의존성 패키지
├── .gitignore                      # Git 무시 파일
├── README.md                       # 프로젝트 설명 (이 파일)
├── features/
│   ├── __init__.py
│   ├── chat/                       # 채팅 기능
│   │   ├── __init__.py
│   │   ├── prompts.py              # LLM 프롬프트 템플릿
│   │   ├── chatbot_service.py      # 채팅 비즈니스 로직
│   │   └── chatbot_ui.py           # 채팅 UI (Streamlit)
│   ├── dashboard/                  # 대시보드
│   │   ├── __init__.py
│   │   └── dashboard_ui.py         # 통계 대시보드 UI
│   ├── settings/                   # 설정
│   │   ├── __init__.py
│   │   └── settings_ui.py          # 문서 관리 및 인덱싱 UI
│   ├── rag/                        # RAG (검색 증강 생성)
│   │   ├── __init__.py
│   │   ├── document_loader.py      # 문서 로드
│   │   ├── text_splitter.py        # 텍스트 청킹
│   │   ├── embedding_generator.py  # 임베딩 생성
│   │   ├── faiss_indexer.py        # FAISS 인덱싱
│   │   └── retriever.py            # 벡터 검색
│   └── shared/                     # 공유 유틸리티
│       ├── __init__.py
│       ├── api.py                  # Gemini API 래퍼
│       ├── db.py                   # SQLite 데이터베이스
│       └── state_manager.py        # 앱 상태 관리
├── sample_data/                    # 쇼핑몰 정책 문서
│   ├── 배송정책.txt
│   └── 반품정책.txt
└── data/ (자동 생성)
    ├── chat.db                     # SQLite 데이터베이스
    ├── app_state.json              # 앱 상태 파일
    └── faiss_index/
        ├── index.faiss             # FAISS 인덱스
        ├── embeddings.npy          # 임베딩 벡터
        └── metadata.json           # 청크 메타데이터
```

---

## 파일별 기능

### 📦 최상위 레벨

#### **app.py** – 애플리케이션 진입점
- Streamlit 애플리케이션의 메인 파일
- 모든 서비스(API, DB, RAG) 초기화
- 3개 페이지(💬 채팅, 📊 대시보드, ⚙️ 설정) 라우팅
- 싱글톤 패턴으로 세션 상태 관리

```python
# 서비스 초기화
api = GeminiAPI()
db = ChatDatabase()
retriever = Retriever(api, FAISS_INDEX_PATH)
chatbot_service = ChatbotService(retriever, api, db)

# 페이지 라우팅
if page == "💬 채팅":
    chatbot_ui.show(chatbot_service, ...)
elif page == "📊 대시보드":
    dashboard_ui.show(db)
elif page == "⚙️ 설정":
    settings_ui.show()
```

#### **config.py** – 전역 설정
- 프로젝트 경로, 파일 경로 정의
- Gemini API 키 및 모델명 설정
- 임베딩, 캐싱, DB 타임아웃 등 파라미터
- **모든 파일이 참조하는 중앙 설정 파일**

```python
# 경로
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "chat.db"
FAISS_INDEX_PATH = DATA_DIR / "faiss_index"

# API 설정
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GENERATION_MODEL = "gemini-1.5-flash"
EMBEDDING_MODEL = "models/gemini-embedding-001"
EMBEDDING_DIM = 3072

# 파라미터
TEMPERATURE = 0.3
MAX_TOKENS = 2000
ENABLE_CACHING = True
```

#### **requirements.txt** – 의존성 패키지
```
streamlit          # 웹 UI
langchain          # LLM 체인
langchain-core     # 코어
langchain-google-genai  # Gemini 통합
google-generativeai # Gemini API
faiss-cpu          # 벡터 검색
numpy, pandas      # 데이터 처리
```

---

### 🔧 features/shared/ – 공유 유틸리티

#### **api.py** – Gemini API 래퍼 + 캐싱

**EmbeddingCache 클래스:**
```python
class EmbeddingCache:
    def _load_cache()      # pickle 파일에서 캐시 로드
    def get(text)          # 캐시 조회
    def save(text, emb)    # 임베딩 결과 저장
    def clear()            # 캐시 전체 삭제
```

**GeminiAPI 클래스:**
```python
class GeminiAPI:
    def embed(text)                # 단일 텍스트 임베딩
    def embed_batch(texts)         # 배치 임베딩 (캐싱 활용)
    def generate(prompt)           # 텍스트 생성
    def generate_streaming(prompt) # 스트리밍 응답
```

**주요 기능:**
- Gemini API를 통한 임베딩 및 텍스트 생성
- 임베딩 결과를 pickle 파일로 캐싱하여 API 호출 최소화
- 배치 임베딩으로 여러 텍스트 한 번에 처리

#### **db.py** – SQLite 데이터베이스 관리

**ChatDatabase 클래스:**
```python
class ChatDatabase:
    def _init_db()              # 테이블 생성
    def save_chat(user, ai)     # 대화 저장
    def save_rating(id, rating) # 평가 저장 (1/0/-1)
    def get_chat_history()      # 대화 히스토리 조회
    def get_statistics()        # 통계 조회
    def clear_history()         # 모든 대화 삭제
    def get_recent_chats(limit) # 최근 대화 조회
```

**테이블 구조:**
```sql
CREATE TABLE chat_history (
    id INTEGER PRIMARY KEY,
    timestamp DATETIME,
    user_message TEXT,
    assistant_message TEXT,
    rating INTEGER          -- 1(좋음), 0(보통), -1(나쁨)
)
```

#### **state_manager.py** – 앱 상태 관리

**StateManager 클래스:**
```python
class StateManager:
    def load_state()         # JSON에서 상태 로드
    def save_state(...)      # 상태 저장
    def load_chat_history()  # DB에서 히스토리 로드
```

**관리 상태:**
- `documents_loaded`: 문서 로드 여부
- `index_loaded`: FAISS 인덱스 생성 여부

---

### 🔍 features/rag/ – RAG 시스템

#### **document_loader.py** – 문서 로드

```python
class DocumentLoader:
    def load() -> bool
        # sample_data의 모든 .txt 파일 로드
        # 반환: [{'title': 'file1', 'content': '...'}, ...]
```

#### **text_splitter.py** – 텍스트 청킹

```python
class TextSplitter:
    def split(text) -> List[str]
        # 문서를 문장 기반으로 청킹
        # chunk_size: 500자
        # overlap: 100자 중복
```

#### **embedding_generator.py** – 임베딩 생성

```python
class EmbeddingGenerator:
    def generate(texts) -> List[List[float]]
        # GeminiAPI를 사용하여 텍스트 임베딩
        # 반환: [embedding1, embedding2, ...]
        # 각 embedding은 3072차원 벡터
```

#### **faiss_indexer.py** – FAISS 인덱싱

```python
class FAISSIndexBuilder:
    def build(chunks, embeddings, documents) -> bool
        # FAISS IndexFlatL2로 인덱싱
        # 저장 파일:
        # - index.faiss: 벡터 인덱스
        # - embeddings.npy: 벡터 배열
        # - metadata.json: 청크 및 메타데이터
```

#### **retriever.py** – 의미 검색

```python
class Retriever:
    def _load_metadata()        # 메타데이터 로드
    def retrieve(query, top_k) -> List[Dict]
        # 1. 질문을 임베딩
        # 2. FAISS에서 top_k 유사 청크 검색
        # 반환: [
        #   {'content': '청크1', 'source': '...', 'relevance': 0.5},
        #   ...
        # ]
```

---

### 💬 features/chat/ – 채팅 기능

#### **prompts.py** – LLM 프롬프트 템플릿

```python
GENERAL_PROMPT      # 일반 질문용 프롬프트
SHIPPING_PROMPT     # 배송 관련 질문 특화
RETURN_PROMPT       # 반품 관련 질문 특화

CATEGORY_KEYWORDS = {
    'shipping': ['배송', '언제', '배달', '도착', '며칠'],
    'return': ['반품', '환불', '교환', '불량', '손상']
}
```

#### **chatbot_service.py** – 채팅 비즈니스 로직 (LCEL 파이프라인)

```python
class ChatbotService:
    def _init_chains()
        # LCEL 파이프라인 초기화
        chains = {
            'general': GENERAL_PROMPT | llm | parser,
            'shipping': SHIPPING_PROMPT | llm | parser,
            'return': RETURN_PROMPT | llm | parser
        }
    
    def _detect_category(question) -> str
        # 질문 키워드로 카테고리 자동 감지
    
    def process_message(user_input) -> str
        # 1. RAG로 관련 문서 검색
        # 2. 카테고리별 최적 프롬프트 선택
        # 3. LLM으로 응답 생성
        # 4. DB에 저장
    
    def rate_message(chat_id, rating) -> bool
        # 대화 평가 저장
    
    def get_history() -> List[Dict]
        # 대화 히스토리 조회
```

**LCEL 파이프라인 구조:**
```python
# 배송 관련 질문 예시
response = (SHIPPING_PROMPT | llm | parser).invoke({
    'context': context,
    'question': user_input
})

# 실행 순서:
# 1. SHIPPING_PROMPT: 입력 → 프롬프트 텍스트 완성
# 2. llm: 프롬프트 → Gemini API 호출 → 응답
# 3. parser: 응답 객체 → 문자열로 변환
```

#### **chatbot_ui.py** – 채팅 UI (Streamlit)

```python
def show(service, docs_loaded, index_loaded)
    ├── 상태 표시 (문서 로드, 인덱스 생성 여부)
    ├── 사용자 입력 받기
    ├── service.process_message() 호출
    ├── 응답 표시
    ├── 평가 버튼 (👍 좋음 / 😐 보통 / 👎 나쁨)
    └── 과거 대화 목록 표시
```

---

### 📊 features/dashboard/ – 대시보드

#### **dashboard_ui.py** – 통계 대시보드 UI

```python
def show(db)
    ├── 총 대화 수 표시
    ├── 평균 평가 점수 계산
    ├── 평가별 통계
    │   ├── 👍 좋음 개수
    │   ├── 😐 보통 개수
    │   └── 👎 나쁨 개수
    └── 모든 대화 삭제 버튼
```

---

### ⚙️ features/settings/ – 설정

#### **settings_ui.py** – 문서 관리 및 인덱싱 UI

```python
def show()
    ├── 문서 로드 및 인덱스 생성
    │   ├── 1. DocumentLoader: 문서 로드
    │   ├── 2. TextSplitter: 청킹
    │   ├── 3. EmbeddingGenerator: 임베딩
    │   └── 4. FAISSIndexBuilder: 인덱싱
    ├── 캐시 삭제
    │   └── EmbeddingCache.clear()
    └── 인덱스 초기화
        └── FAISS 인덱스 전체 삭제
```

---

## 설치 방법

### 1. 저장소 클론
```bash
git clone https://github.com/ysrim/shopping_mall_ai.git
cd shopping_mall_ai
```

### 2. 가상환경 생성 및 활성화
```bash
# Python 3.12 추천
python3.12 -m venv venv

# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. 패키지 설치
```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### 4. 환경변수 설정
`.env` 파일 생성 후 Gemini API 키 추가:
```
GOOGLE_API_KEY=your_gemini_api_key_here
```

[Gemini API 키 발급하기](https://aistudio.google.com/app/apikey)

### 5. 애플리케이션 실행
```bash
streamlit run app.py
```

브라우저에서 `http://localhost:8501` 열기

---

## 사용 방법

### Step 1: 문서 로드 및 인덱싱
1. 좌측 사이드바에서 "⚙️ 설정" 클릭
2. "📄 문서 로드 및 인덱스 생성" 버튼 클릭
3. 완료 메시지 확인

### Step 2: 채팅
1. "💬 채팅" 페이지로 이동
2. 질문 입력 (예: "배송은 며칠 걸려?")
3. AI 응답 확인
4. 평가 버튼으로 피드백 제공 (👍/😐/👎)

### Step 3: 대시보드 확인
1. "📊 대시보드" 페이지로 이동
2. 총 대화 수, 평균 평가, 평가별 통계 확인

### 추가 설정
- **캐시 삭제**: 설정 페이지 → "🗑️ 초기화" → "캐시 삭제"
- **인덱스 초기화**: 설정 페이지 → "🗑️ 초기화" → "인덱스 초기화"
- **대화 삭제**: 대시보드 → "모든 대화 삭제"

---

## 기술 스택

| 항목 | 기술 |
|------|------|
| **UI Framework** | Streamlit |
| **LLM** | Google Gemini API |
| **LLM Framework** | LangChain (LCEL) |
| **Vector Search** | FAISS (IndexFlatL2) |
| **Embedding** | Gemini Embedding Model (3072-dim) |
| **Database** | SQLite3 |
| **Caching** | Python Pickle |
| **Language** | Python 3.12+ |

---

## 주요 구현 특징

### 1. Vertical Slice Architecture
각 기능(Chat, Dashboard, Settings, RAG)이 독립적인 폴더로 구성되어 있어 확장과 유지보수가 용이합니다.

```
features/
├── chat/       # 채팅 기능 (서비스 + UI)
├── dashboard/  # 대시보드 (UI)
├── settings/   # 설정 (UI)
├── rag/        # RAG 시스템
└── shared/     # 공유 유틸리티
```

### 2. LCEL (LangChain Expression Language)
선언적이고 간결한 파이프라인 구성:

```python
# 기존 방식
prompt_text = prompt.invoke({'context': ctx, 'question': q})
response = llm.invoke(prompt_text)

# LCEL 방식 (더 간결)
response = (prompt | llm | parser).invoke({
    'context': ctx,
    'question': q
})
```

### 3. 자동 카테고리 분류
질문 키워드를 분석하여 배송/반품/일반 중 최적의 프롬프트 자동 선택

```python
def _detect_category(self, question: str) -> str:
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(word in question for word in keywords):
            return category
    return 'general'
```

### 4. 임베딩 캐싱
반복되는 임베딩 계산을 Pickle 파일로 캐싱하여 API 호출 감소

```python
def embed_batch(self, texts: list):
    for text in texts:
        cached = self.embedding_cache.get(text)
        if cached:
            embeddings.append(cached)  # 캐시 사용
        else:
            emb = self.embed(text)     # API 호출
            self.embedding_cache.save(text, emb)
```

### 5. Config 중앙화
모든 설정값을 `config.py`에서 관리하여 일관성 유지

```python
# config.py
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GENERATION_MODEL = "gemini-1.5-flash"
EMBEDDING_DIM = 3072
TEMPERATURE = 0.3
```

### 6. 평가 시스템
각 답변에 대한 사용자 피드백(좋음/보통/나쁨)을 수집하여 성능 분석

```python
# chatbot_ui.py
if st.button("👍", key=f"like_{chat['id']}"):
    service.rate_message(chat['id'], 1)
```

---

## 문제 해결

### FAISS 인덱스 오류
```bash
# 인덱스 초기화
rm -rf data/faiss_index
# 설정 페이지에서 다시 생성
```

### API 키 에러
```bash
# .env 파일 확인
cat .env
# GOOGLE_API_KEY가 올바른지 확인
```

### 임베딩 캐시 문제
```bash
# 캐시 삭제
rm -rf cache/embeddings.pkl
# 설정 페이지에서 캐시 삭제 버튼 클릭
```

### 패키지 설치 에러
```bash
# 가상환경 재생성
rm -rf venv
python3.12 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### 문서 로드 실패
```bash
# sample_data 폴더 확인
ls -la sample_data/
# 파일이 있는지 확인
```

---

## 프로젝트 구조 요약

```
입력 (사용자 질문)
  ↓
[채팅 서비스]
  ├─ RAG 검색 (FAISS)
  ├─ 카테고리 감지
  ├─ 프롬프트 선택
  └─ LLM 생성 (LCEL)
  ↓
[데이터 저장]
  ├─ 채팅 DB (SQLite)
  └─ 평가 저장
  ↓
[통계 대시보드]
  ├─ 총 대화 수
  ├─ 평균 평가
  └─ 평가 분포
  ↓
출력 (UI 표시)
```

---

## 관련 링크

- [Streamlit 문서](https://docs.streamlit.io/)
- [LangChain 문서](https://python.langchain.com/)
- [Google Gemini API](https://ai.google.dev/)
- [FAISS 문서](https://faiss.ai/)
