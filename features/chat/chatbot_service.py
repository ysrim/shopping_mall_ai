from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from features.rag import Retriever
from features.shared.api import GeminiAPI
from features.shared.db import ChatDatabase
from .prompts import GENERAL_PROMPT, SHIPPING_PROMPT, RETURN_PROMPT, CATEGORY_KEYWORDS
from config import GENERATION_MODEL, TEMPERATURE


class ChatbotService:
    def __init__(self, retriever: Retriever, api: GeminiAPI, db: ChatDatabase):
        self.retriever = retriever
        self.api = api
        self.db = db
        self._init_chains()

    def _init_chains(self):
        """LLM 체인 초기화"""
        self.llm = ChatGoogleGenerativeAI(
            model=GENERATION_MODEL,
            temperature=TEMPERATURE
        )

        # 여러 체인 생성 (LCEL)
        self.chains = {
            'general': GENERAL_PROMPT | self.llm | StrOutputParser(),
            'shipping': SHIPPING_PROMPT | self.llm | StrOutputParser(),
            'return': RETURN_PROMPT | self.llm | StrOutputParser()
        }

    def _detect_category(self, question: str) -> str:
        """질문 카테고리 감지"""
        for category, keywords in CATEGORY_KEYWORDS.items():
            if any(word in question for word in keywords):
                return category
        return 'general'

    def process_message(self, user_input: str) -> str:
        """사용자 입력 처리"""
        try:
            # RAG 검색
            results = self.retriever.retrieve(user_input, top_k=3)
            context = "\n".join([r["content"] for r in results]) if results else "관련 정보를 찾을 수 없습니다."

            # 카테고리 감지
            category = self._detect_category(user_input)
            print(f"🔍 Category detected: {category}")

            # 적절한 체인 선택
            chain = self.chains[category]

            # 체인 실행
            response = chain.invoke({
                'context': context,
                'question': user_input
            })

            # DB 저장
            self.db.save_chat(user_input, response)
            print(f"✅ Chat saved")

            return response
        except Exception as e:
            print(f"❌ Process message error: {e}")
            return "오류가 발생했습니다. 다시 시도해주세요."

    def rate_message(self, chat_id: int, rating: int) -> bool:
        """메시지 평가"""
        return self.db.save_rating(chat_id, rating)

    def get_history(self) -> list:
        """히스토리 조회"""
        return self.db.get_chat_history()
