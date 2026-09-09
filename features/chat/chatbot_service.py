from features.rag import Retriever
from features.chat.rag_chain import RAGChain
from features.shared.api import llm_factory
from features.shared.db import ChatDatabase
from features.chat.prompts import classify_category  # ✨ import 추가
from config import LLM_PROVIDER
from typing import Optional


class ChatbotService:
    def __init__(
        self,
        retriever: Retriever,
        db: ChatDatabase,
        llm_provider: Optional[str] = None
    ) -> None:  # ✨ 타입 힌트 강화
        """
        챗봇 서비스 초기화

        Args:
            retriever: RAG 문서 검색기
            db: 대화 저장 데이터베이스
            llm_provider: LLM 프로바이더 ("gemini" 또는 "ollama")
        """
        self.retriever = retriever
        self.db = db
        self.llm_provider = llm_provider or LLM_PROVIDER
        self.llm = None
        self.rag_chain = None

        print(f"🔗 ChatbotService 초기화")
        print(f"   - LLM 프로바이더: {self.llm_provider}\n")

        self._init_chains()

    def _init_chains(self) -> None:  # ✨ 반환 타입 명시
        """LLM 및 LCEL 체인 초기화"""
        try:
            print("🔗 LLM 체인 초기화 중...")
            self.llm_api = llm_factory.create_llm_api(self.llm_provider)
            self.llm = self.llm_api.get_llm()

            print("⛓️  LCEL RAG 체인 구축 중...")
            # ✨ 기본 카테고리는 'general'로 초기화, 실행 시 변경됨
            self.rag_chain = RAGChain(self.llm, self.retriever, category='general')

            print(f"✅ LLM & LCEL 체인 초기화 완료\n")
        except Exception as e:
            print(f"❌ 체인 초기화 실패: {str(e)}")
            raise

    def process_message(self, user_message: str) -> str:
        """
        사용자 메시지 처리 및 답변 생성

        ✨ 카테고리 분류 후 카테고리별 프롬프트 사용
        """
        try:
            print(f"\n{'=' * 60}")
            print(f"📝 메시지 처리 시작")
            print(f"{'=' * 60}")
            print(f"질문: {user_message}\n")

            # ✨ Step 1: 카테고리 분류
            category = classify_category(user_message)
            print(f"🏷️  카테고리: {category}")

            # ✨ Step 2: 카테고리별 RAGChain 생성
            rag_chain = RAGChain(
                self.llm,
                self.retriever,
                category=category  # ✨ 카테고리 전달
            )

            # ✨ Step 3: LCEL 체인 실행
            response = rag_chain.invoke(user_message)

            if not isinstance(response, str):
                response = str(response).strip()

            # ✨ Step 4: DB에 저장
            print("💾 대화 저장 중...")
            chat_id = self.db.save_chat(
                user_message=user_message,
                assistant_message=response,
                category=category,  # ✨ 분류된 카테고리 저장
                llm_provider=self.llm_provider
            )
            print(f"✅ 대화 저장 완료 (ID: {chat_id})\n")

            return response
        except Exception as e:
            print(f"❌ 메시지 처리 실패: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return f"오류가 발생했습니다: {str(e)}"

    def get_history(self, limit: int = 50) -> list:
        """대화 히스토리 조회"""
        return self.db.get_history(limit)

    def rate_message(self, chat_id: int, rating: int) -> bool:
        """메시지 평가 저장"""
        return self.db.rate_message(chat_id, rating)

    def delete_message(self, chat_id: int) -> bool:
        """메시지 삭제"""
        return self.db.delete_chat(chat_id)

    def clear_history(self) -> bool:
        """히스토리 삭제"""
        return self.db.clear_history()

    def get_statistics(self) -> dict:
        """통계 조회"""
        return self.db.get_statistics()
