# Shopping Mall AI

LangChain LCEL과 RAG(검색 증강 생성) 기반으로 쇼핑몰 사내 정책 규정(AS·결제·반품·배송·환불·회원)을 실시간 검색하여 환각 없이 정확한 답변을 제공하는 지능형 CS 질의응답 시스템입니다.

---

## 📌 주요 특징 (Key Features)

* **정책 기반 지능형 질의응답 (RAG Engine):** 모델의 자체 사전학습 지식에 의존하지 않고 사내 원본 문서를 실시간 검색하여 사실에 입각한 응답 제공.


* **선언적 LCEL 파이프라인:** LangChain Expression Language(`prompt | llm | StrOutputParser()`)를 적용한 직관적이고 확장성 높은 체인 설계.


* **의도 기반 동적 라우팅 (Intent Routing):** 고객 질문 키워드를 실시간 감지하여 카테고리(배송/반품, 결제/환불, AS/회원 등)별 최적 시스템 프롬프트 자동 분기.


* **3대 독립 UI 제공 (Streamlit):** 고객용 대화형 챗봇, 관리자용 통계 대시보드, 규정 파일 업로드 및 인덱스 관리자 화면 구현.


* **실시간 피드백 및 품질 역추적 감사:** 고객 응답 직후 만족도(+1, 0, -1)를 수집하며, -1점 불만족 질의의 질문/답변/참조 청크를 역추적 감사.



---

## 🛠 기술 스택 (Tech Stack)

| 구분 | 기술 | 주요 역할 |
| --- | --- | --- |
| **Frontend / UI** | Streamlit | 반응형 대화형 챗봇 인터페이스 및 통계 대시보드 시각화

 |
| **Orchestration** | LangChain (LCEL) | 선언적 체인 파이프라인 조율 및 프롬프트 동적 분기

 |
| **AI Models** | Google Gemini, Ollama | LLM 답변 생성 추론 및 로컬 768차원 임베딩 벡터 생성

 |
| **Vector DB** | FAISS | `IndexFlatL2` 기반 정책 문서 고속 유사도 검색

 |
| **Storage** | SQLite3 | 상담 세션 이력 및 사용자 피드백 평가 로그 영속화

 |

---

## 🏗 시스템 아키텍처 & 파이프라인

### 1. Data Pipeline

```text
[고객 질문] ──> [의도 라우터] (AS·결제·반품·배송·환불·회원)
     │
     ▼
[RAG 검색]  ──> Ollama 768d 임베딩 & FAISS Top-K(k=10) 추출
     │
     ▼
[LCEL 체인] ──> Prompt | Gemini LLM | StrOutputParser
     │
     ▼
[저장·응답] ──> SQLite 세션 기록 + 웹 화면 즉시 렌더링

```

(User Query ➜ Category Detector ➜ FAISS Context ➜ LCEL Chain Execution ➜ Output Parsing ➜ Streamlit Render)

### 2. RAG 파이프라인 세부 스펙

* **문서 청킹 (Chunking):** `RecursiveCharacterTextSplitter` 활용 (Chunk Size: 500자, Overlap: 100자)


* **인덱싱:** 768차원 벡터 임베딩, FAISS `IndexFlatL2` 정밀 탐색 인덱스 로컬 파일(`index.faiss`) 영속화


* **유사도 탐색:** 유클리드 거리 기반 연관도 최상위 문서 조항 10개 추출 ($k=10$)



---

## 📂 프로젝트 구조 (Vertical Slice Architecture)

기능(Feature) 단위로 UI와 비즈니스 로직을 독립 격리하여 모듈 간 간섭을 차단하는 버티컬 슬라이스 구조로 설계되었습니다.

```text
shopping_mall_ai/
├── app.py                      # 애플리케이션 메인 진입점[cite: 2]
├── config.py                   # 환경 변수 및 시스템 설정[cite: 2]
├── features/                   # 기능별 독립 모듈 폴더[cite: 2]
│   ├── chat/                   # 챗봇 서비스 로직 및 대화 화면 UI[cite: 2]
│   ├── dashboard/              # 상담 통계 및 품질 역추적 대시보드 UI[cite: 2]
│   ├── settings/               # 정책 파일 업로드 및 FAISS 인덱싱 관리[cite: 2]
│   └── rag/                    # Loader, Splitter, Retriever 모듈[cite: 2]
├── shared/                     # 공통 유틸리티[cite: 2]
│   ├── api.py                  # Gemini LLM API 연동 클라이언트[cite: 2]
│   └── db.py                   # SQLite3 데이터베이스 핸들러[cite: 2]
├── sample_data/                # AS·결제·반품·배송 등 정책 문서 텍스트 원본[cite: 2]
└── data/                       # 생성된 FAISS 인덱스(index.faiss) 및 DB 파일[cite: 2]

```

---

## 🖥 3대 주요 페이지 구성

* **💬 채팅 화면 (Chat Service):** 사내 정책에 근거한 실시간 질의응답 및 만족도(👍/😐/👎) 수집


* **📊 대시보드 (Analytics):** 일자별 상담 총량, 평균 평점 추이 차트, 오답(-1점) 세션의 질문·답변·검색청크 역추적 감사


* **⚙️ 관리자 설정 (Admin):** 신규 정책 텍스트 파일 동적 업로드 및 FAISS 벡터 인덱스 원클릭 재구축



---

## 🚀 시작 가이드 (Quickstart)

### 1. 사전 요구사항

* Python 3.10 이상
* [Ollama](https://ollama.ai/) 설치 및 768차원 임베딩 모델 준비


* Google Gemini API Key 발급



### 2. 가상환경 세팅 및 패키지 설치

```bash
# 레포지토리 클론
git clone https://github.com/your-username/shopping_mall_ai.git
cd shopping_mall_ai

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존 패키지 설치
pip install -r requirements.txt

```

### 3. 환경 변수 설정

프로젝트 루트 디렉토리에 `.env` 파일을 생성하고 발급받은 API 키를 입력합니다.

```env
GEMINI_API_KEY="your-gemini-api-key-here"

```

### 4. 실행

```bash
streamlit run app.py

```

---

## 🔮 향후 추진 과제 (Future Roadmap)

* **FastAPI 백엔드 전환 & React 위젯 분리:** Streamlit 스크립트 재실행 구조를 탈피하여 고성능 비동기 REST API 서버를 구축하고, 어디에나 임베딩 가능한 React 플로팅 챗봇 컴포넌트로 분리.


* **오픈소스 모델 LoRA 파인튜닝:** 피드백 루프로 축적된 우수 상담 로그(👍)를 데이터셋화하여 오픈소스 소형 모델에 LoRA 경량화 파인튜닝 적용.


* **지능형 FAQ 자동 생성:** 빈출 질의 패턴을 자동 분석하여 자주 묻는 질문(FAQ) 생성 및 사내 규정 자동 최신화.
