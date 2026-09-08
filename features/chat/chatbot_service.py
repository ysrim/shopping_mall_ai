from features.rag import Retriever
from features.shared.api import llm_factory
from features.shared.db import ChatDatabase
from config import LLM_PROVIDER
from typing import Optional


class ChatbotService:
    def __init__(self, retriever: Retriever, db: ChatDatabase, llm_provider: str = None):
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
        self.top_k = 5  # 검색 결과 상위 K개

        print(f"🔗 ChatbotService 초기화")
        print(f"   - LLM 프로바이더: {self.llm_provider}")
        print(f"   - 검색 결과: {self.top_k}개\n")

        self._init_chains()

    def _init_chains(self):
        """LLM 체인 초기화"""
        try:
            print("🔗 LLM 체인 초기화 중...")
            self.llm_api = llm_factory.create_llm_api(self.llm_provider)
            self.llm = self.llm_api.get_llm()
            print(f"✅ LLM 체인 초기화 완료\n")
        except Exception as e:
            print(f"❌ LLM 체인 초기화 실패: {str(e)}")
            raise

    def _build_prompt(self, query: str, context: str) -> str:
        """
        RAG 프롬프트 생성

        Args:
            query: 사용자 질문
            context: 검색된 문서 내용

        Returns:
            생성된 프롬프트
        """
        prompt = f"""당신은 전문적이고 친절한 쇼핑 고객 서비스 어시스턴트입니다.
아래의 제공된 정보를 바탕으로 사용자의 질문에 정확하고 도움이 되는 답변을 해주세요.

【제공된 정보】
{context}

【사용자의 질문】
{query}

【답변 지침】
1. 제공된 정보에만 기반하여 답변하세요.
2. 정보에 없는 내용은 "해당 정보는 제공되지 않았습니다"라고 명확히 답변하세요.
3. 친절하고 존중하는 태도로 답변하세요.
4. 필요한 경우 요약이나 구조화된 형식으로 답변하세요.

답변:"""
        return prompt

    def _format_context(self, retrieved_docs: list) -> str:
        """
        검색된 문서들을 컨텍스트로 포맷팅

        Args:
            retrieved_docs: 검색된 문서 리스트

        Returns:
            포맷팅된 컨텍스트 문자열
        """
        if not retrieved_docs:
            return "검색된 정보가 없습니다."

        context_parts = []
        for i, doc in enumerate(retrieved_docs, 1):
            content = doc.get('chunk', doc.get('content', ''))
            relevance = doc.get('distance', 'N/A')
            context_parts.append(f"[정보 {i}] (유사도: {relevance})\n{content}")

        return "\n\n".join(context_parts)

    def _extract_response(self, llm_response) -> str:
        """
        LLM 응답에서 텍스트 추출
        """
        print(f"\n{'=' * 60}")
        print(f"📦 LLM 응답 처리 시작")
        print(f"{'=' * 60}")
        print(f"응답 타입: {type(llm_response).__name__}")

        # 1. 문자열
        if isinstance(llm_response, str):
            print("✅ [방법 1] 문자열 타입 → 직접 반환")
            result = llm_response.strip()
            print(f"결과 길이: {len(result)}자\n")
            return result

        # 2. dict 타입
        if isinstance(llm_response, dict):
            if 'text' in llm_response:
                print("✅ [방법 2] dict['text'] → 추출")
                result = str(llm_response['text']).strip()
                print(f"결과 길이: {len(result)}자\n")
                return result

            if 'content' in llm_response:
                print("✅ [방법 3] dict['content'] → 추출")
                result = str(llm_response['content']).strip()
                print(f"결과 길이: {len(result)}자\n")
                return result

        # 3. 객체의 content 속성 (AIMessage 등)
        if hasattr(llm_response, 'content'):
            print(f"✅ [방법 4] content 속성 찾음")
            content = llm_response.content
            print(f"   content 타입: {type(content).__name__}")

            # content가 리스트인 경우 (AIMessage)
            if isinstance(content, list):
                print(f"   content는 리스트, 길이: {len(content)}")
                if len(content) > 0:
                    first_item = content[0]
                    print(f"   첫 번째 항목 타입: {type(first_item).__name__}")

                    # 첫 번째 항목이 dict인 경우
                    if isinstance(first_item, dict):
                        if 'text' in first_item:
                            print("   ✅ first_item['text'] 추출")
                            result = str(first_item['text']).strip()
                            print(f"   결과 길이: {len(result)}자\n")
                            return result
                        elif 'content' in first_item:
                            print("   ✅ first_item['content'] 추출")
                            result = str(first_item['content']).strip()
                            print(f"   결과 길이: {len(result)}자\n")
                            return result

                    # 첫 번째 항목이 문자열인 경우
                    print("   ✅ first_item을 문자열로 변환")
                    result = str(first_item).strip()
                    print(f"   결과 길이: {len(result)}자\n")
                    return result

            # content가 문자열인 경우
            elif isinstance(content, str):
                print("✅ [방법 5] content는 문자열")
                result = content.strip()
                print(f"결과 길이: {len(result)}자\n")
                return result

        # 4. 리스트 타입
        if isinstance(llm_response, list):
            print(f"✅ [방법 6] 리스트 타입")
            if len(llm_response) > 0:
                first = llm_response[0]

                if isinstance(first, dict) and 'text' in first:
                    print("   ✅ list[0]['text'] 추출")
                    result = str(first['text']).strip()
                    print(f"   결과 길이: {len(result)}자\n")
                    return result

                print("   ✅ list[0]을 문자열로 변환")
                result = str(first).strip()
                print(f"   결과 길이: {len(result)}자\n")
                return result

        # 최후의 수단
        print(f"⚠️ [방법 7] str() 변환")
        result = str(llm_response).strip()
        print(f"결과 길이: {len(result)}자\n")
        return result

    def process_message(self, user_message: str) -> str:
        """
        사용자 메시지 처리 및 답변 생성

        Args:
            user_message: 사용자 질문

        Returns:
            생성된 답변
        """
        try:
            print(f"📝 메시지 처리 중: {user_message[:50]}...\n")

            # 1. 문서 검색 (RAG)
            print("🔍 문서 검색 중...")
            retrieved_docs = self.retriever.retrieve(user_message, top_k=self.top_k)

            if not retrieved_docs:
                print("⚠️ 검색된 문서 없음\n")
                response = "죄송합니다. 관련 정보를 찾을 수 없습니다. 다시 질문해주세요."
            else:
                print(f"✅ {len(retrieved_docs)}개 문서 검색 완료")
                for i, doc in enumerate(retrieved_docs, 1):
                    print(f"   [{i}] 유사도: {doc.get('distance', 'N/A')}, 내용길이: {len(doc.get('chunk', ''))}자")
                print()

                # 2. 컨텍스트 구성
                print("📋 컨텍스트 구성 중...")
                context = self._format_context(retrieved_docs)
                print(f"✅ 컨텍스트 구성 완료 (길이: {len(context)}자)\n")

                # 3. 프롬프트 생성
                print("🎯 프롬프트 생성 중...")
                prompt = self._build_prompt(user_message, context)
                print(f"✅ 프롬프트 생성 완료 (길이: {len(prompt)}자)\n")

                # 4. LLM으로 응답 생성
                print("🤖 LLM으로 응답 생성 중...")
                llm_response = self.llm.invoke(prompt)

                # 5. 응답 처리 (여러 타입 지원)
                response = self._extract_response(llm_response)

                # 6. 응답이 문자열인지 최종 확인
                if not isinstance(response, str):
                    print(f"⚠️ 최종 응답이 문자열이 아님: {type(response)}")
                    response = str(response).strip()

                print(f"✅ 응답 생성 완료 (길이: {len(response)}자)\n")

            # 7. 카테고리 분류 (선택)
            category = self._classify_category(user_message)

            # 8. 대화 저장
            print("💾 대화 저장 중...")

            # response가 문자열인지 확인
            if not isinstance(response, str):
                print(f"⚠️ 응답이 문자열이 아님: {type(response)}")
                response = str(response)

            chat_id = self.db.save_chat(
                user_message=user_message,
                assistant_message=response,
                category=category,
                llm_provider=self.llm_provider
            )
            print(f"✅ 대화 저장 완료 (ID: {chat_id})\n")

            return response

        except Exception as e:
            print(f"❌ 메시지 처리 실패: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return f"오류가 발생했습니다: {str(e)}"

    def _classify_category(self, query: str) -> Optional[str]:
        """
        질문의 카테고리 분류 (간단한 키워드 기반)

        Args:
            query: 사용자 질문

        Returns:
            카테고리
        """
        query_lower = query.lower()

        # 배송 관련
        if any(word in query_lower for word in ['배송', '택배', '배달', '도착', 'shipping', 'delivery']):
            return 'shipping'

        # 반품/교환 관련
        elif any(word in query_lower for word in ['반품', '교환', '환불', 'return', 'exchange', 'refund']):
            return 'return'

        # 결제 관련
        elif any(word in query_lower for word in ['결제', '결제방법', '카드', '계좌', 'payment', 'pay']):
            return 'payment'

        # 상품 관련
        elif any(word in query_lower for word in ['상품', '제품', '상세', '사양', 'product', 'item']):
            return 'product'

        # 계정/개인정보 관련
        elif any(word in query_lower for word in ['계정', '로그인', '회원', '비밀번호', 'account', 'login']):
            return 'account'

        # 기타
        else:
            return 'general'

    def get_history(self, limit: int = 50) -> list:
        """
        대화 히스토리 조회

        Args:
            limit: 조회 개수 (기본: 50)

        Returns:
            대화 리스트
        """
        try:
            print(f"📋 히스토리 조회 중 (최대 {limit}개)...")
            history = self.db.get_history(limit)
            print(f"✅ 히스토리 조회 완료: {len(history)}개\n")
            return history
        except Exception as e:
            print(f"❌ 히스토리 조회 실패: {str(e)}")
            return []

    def rate_message(self, chat_id: int, rating: int) -> bool:
        """
        메시지에 평가 추가

        Args:
            chat_id: 대화 ID
            rating: 평가 (1: 좋음, 0: 보통, -1: 나쁨)

        Returns:
            성공 여부
        """
        try:
            rating_emoji = {1: "👍", 0: "😐", -1: "👎"}.get(rating, "❓")
            print(f"⭐ 평가 저장 중: {rating_emoji} (ID: {chat_id})...")
            success = self.db.rate_message(chat_id, rating)
            if success:
                print(f"✅ 평가 저장 완료\n")
            return success
        except Exception as e:
            print(f"❌ 평가 저장 실패: {str(e)}")
            return False

    def delete_message(self, chat_id: int) -> bool:
        """
        대화 삭제

        Args:
            chat_id: 대화 ID

        Returns:
            성공 여부
        """
        try:
            print(f"🗑️ 대화 삭제 중 (ID: {chat_id})...")
            success = self.db.delete_chat(chat_id)
            if success:
                print(f"✅ 대화 삭제 완료\n")
            return success
        except Exception as e:
            print(f"❌ 대화 삭제 실패: {str(e)}")
            return False

    def clear_history(self) -> bool:
        """
        모든 대화 히스토리 삭제

        Returns:
            성공 여부
        """
        try:
            print(f"🗑️ 모든 대화 삭제 중...")
            success = self.db.clear_history()
            if success:
                print(f"✅ 모든 대화 삭제 완료\n")
            return success
        except Exception as e:
            print(f"❌ 대화 삭제 실패: {str(e)}")
            return False

    def get_statistics(self) -> dict:
        """
        대화 통계 조회

        Returns:
            통계 정보
        """
        try:
            print(f"📊 통계 조회 중...")
            stats = self.db.get_statistics()
            print(f"✅ 통계 조회 완료\n")
            return stats
        except Exception as e:
            print(f"❌ 통계 조회 실패: {str(e)}")
            return {}

    def change_llm_provider(self, provider: str) -> bool:
        """
        LLM 프로바이더 변경

        Args:
            provider: 새로운 프로바이더 ("gemini" 또는 "ollama")

        Returns:
            성공 여부
        """
        try:
            if provider not in ["gemini", "ollama"]:
                print(f"❌ 유효하지 않은 프로바이더: {provider}")
                return False

            print(f"🔄 LLM 프로바이더 변경 중: {self.llm_provider} → {provider}...")
            self.llm_provider = provider
            self._init_chains()
            print(f"✅ LLM 프로바이더 변경 완료\n")
            return True
        except Exception as e:
            print(f"❌ 프로바이더 변경 실패: {str(e)}")
            return False

    def update_retriever(self, retriever: Retriever) -> bool:
        """
        문서 검색기 업데이트

        Args:
            retriever: 새로운 Retriever 객체

        Returns:
            성공 여부
        """
        try:
            print(f"🔄 Retriever 업데이트 중...")
            self.retriever = retriever
            print(f"✅ Retriever 업데이트 완료\n")
            return True
        except Exception as e:
            print(f"❌ Retriever 업데이트 실패: {str(e)}")
            return False
