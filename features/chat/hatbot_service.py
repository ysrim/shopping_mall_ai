from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from features.rag import Retriever
from features.shared.api import GeminiAPI
from features.shared.db import ChatDatabase


class ChatbotService:
    def __init__(self, retriever: Retriever, api: GeminiAPI, db: ChatDatabase):
        self.retriever = retriever
        self.api = api
        self.db = db
        self._init_chain()

    def _init_chain(self):
        """LLM 체인 초기화"""
        # 프롬프트 템플릿
        template = """당신은 쇼핑몰 고객 서비스 담당자입니다.

다음은 쇼핑몰 정책 문서입니다:
{context}

사용자 질문: {question}

위의 문서를 참고하여 친절하게 답변해주세요."""

        self.prompt = PromptTemplate(
            input_variables=['context', 'question'],
            template=template
        )

        # LLM
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.7
        )

        # 체인 (LCEL)
        self.chain = self.prompt | self.llm

    def process_message(self, user_input: str) -> str:
        """사용자 입력 처리"""
        # RAG 검색
        results = self.retriever.retrieve(user_input, top_k=3)
        context = "\n".join([r["content"] for r in results]) if results else "문서에서 관련 정보를 찾을 수 없습니다."

        # 체인 실행 (prompt | llm)
        response = self.chain.invoke({
            'context': context,
            'question': user_input
        })

        # DB 저장
        self.db.save_chat(user_input, response.content)

        return response.content

    def rate_message(self, chat_id: int, rating: int) -> bool:
        """메시지 평가"""
        return self.db.save_rating(chat_id, rating)

    def get_history(self) -> list:
        """히스토리 조회"""
        return self.db.get_chat_history()
