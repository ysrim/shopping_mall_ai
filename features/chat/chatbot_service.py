# features/chat/chatbot_service.py
from langchain_core.output_parsers import StrOutputParser
from features.rag import Retriever
from features.shared.api import llm_factory
from features.shared.db import ChatDatabase
from .prompts import GENERAL_PROMPT, SHIPPING_PROMPT, RETURN_PROMPT, CATEGORY_KEYWORDS
from config import TEMPERATURE


class ChatbotService:
    """채팅봇 서비스 (멀티 LLM 지원)"""

    def __init__(self, retriever: Retriever, db: ChatDatabase, llm_provider: str = "gemini"):
        """
        초기화

        Args:
            retriever: RAG 리트리버
            db: 채팅 데이터베이스
            llm_provider: "gemini" 또는 "ollama"
        """
        self.retriever = retriever
        self.db = db
        self.llm_provider = llm_provider
        self.embedding_provider = None
        self._init_chains()

    def _init_chains(self):
        """LLM 체인 초기화"""
        try:
            llm_api = llm_factory.create_llm_api(self.llm_provider)
            self.llm = llm_api.get_llm()

            self.chains = {
                'general': GENERAL_PROMPT | self.llm | StrOutputParser(),
                'shipping': SHIPPING_PROMPT | self.llm | StrOutputParser(),
                'return': RETURN_PROMPT | self.llm | StrOutputParser()
            }
            print(f"✅ {self.llm_provider.upper()} 체인 초기화 완료")
        except Exception as e:
            print(f"❌ 체인 초기화 실패: {e}")
            raise

    def switch_provider(self, new_provider: str):
        """
        런타임에 LLM 프로바이더 변경

        Args:
            new_provider: "gemini" 또는 "ollama"
        """
        if self.llm_provider != new_provider:
            print(f"🔄 LLM 프로바이더 변경: {self.llm_provider} → {new_provider}")
            self.llm_provider = new_provider
            self._init_chains()

    def set_embedding_provider(self, embedding_provider: str):
        """임베딩 프로바이더 설정"""
        self.embedding_provider = embedding_provider

    def _detect_category(self, question: str) -> str:
        """질문 카테고리 감지"""
        for category, keywords in CATEGORY_KEYWORDS.items():
            if any(word in question for word in keywords):
                return category
        return 'general'

    def process_message(self, user_input: str) -> str:
        """
        사용자 입력 처리

        Args:
            user_input: 사용자 질문

        Returns:
            AI 응답
        """
        try:
            # RAG 검색
            results = self.retriever.retrieve(
                user_input,
                top_k=3,
                embedding_provider=self.embedding_provider
            )
            context = "\n".join([r['content'] for r in results]) if results else "관련 정보를 찾을 수 없습니다."

            # 카테고리 감지
            category = self._detect_category(user_input)

            # 체인 실행
            chain = self.chains.get(category, self.chains['general'])
            response = chain.invoke({
                'context': context,
                'question': user_input
            })

            # DB 저장
            self.db.save_chat(user_input, response)
            print(f"✅ 채팅 저장 완료 (카테고리: {category}, LLM: {self.llm_provider})")

            return response
        except Exception as e:
            print(f"❌ 메시지 처리 오류: {e}")
            import traceback
            traceback.print_exc()
            return "오류가 발생했습니다. 다시 시도해주세요."

    def rate_message(self, chat_id: int, rating: int) -> bool:
        """메시지 평가"""
        return self.db.save_rating(chat_id, rating)

    def get_history(self):
        """데이터베이스에서 채팅 히스토리 조회"""
        try:
            chats = self.db.get_chat_history()

            # 각 채팅 항목이 필요한 필드를 모두 가지고 있는지 확인
            result = []
            for chat in chats:
                # 필드 검증
                if isinstance(chat, dict):
                    validated_chat = {
                        'id': chat.get('id'),
                        'user_message': chat.get('user_message', ''),
                        'assistant_message': chat.get('assistant_message', ''),
                        'rating': chat.get('rating'),
                        'timestamp': chat.get('timestamp')
                    }
                    result.append(validated_chat)

            return result
        except Exception as e:
            print(f"❌ 히스토리 조회 오류: {str(e)}")
            return []

