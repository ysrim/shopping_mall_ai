from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough  # ✨ 추가
from typing import Dict, Any


class RAGChain:
    """LCEL 기반 RAG 파이프라인 체인"""

    def __init__(self, llm, retriever, category: str = 'general'):
        """
        RAG 체인 초기화

        Args:
            llm: LangChain LLM 인스턴스
            retriever: 문서 검색기
            category: 질문 카테고리 ('shipping', 'return', 'refund', 'payment', 'as', 'membership', 'general')
        """
        self.llm = llm
        self.retriever = retriever
        self.category = category
        self.chain = self._build_chain()

    def _build_chain(self):
        """LCEL 파이프라인 구축 (카테고리별 프롬프트 사용)"""

        # ✨ 프롬프트 import 추가
        from features.chat.prompts import get_prompt_by_category

        # 카테고리별 프롬프트 선택
        rag_prompt = get_prompt_by_category(self.category)

        # 2️⃣ 문서 검색 함수 (context 준비)
        def format_docs(docs):
            """검색된 문서를 포맷팅"""
            parts = []
            for i, doc in enumerate(docs, 1):
                content = doc.get('chunk', doc.get('content', ''))
                relevance = doc.get('distance', 'N/A')
                if content:
                    parts.append(f"[정보 {i}] (유사도: {relevance})\n{content}")
            return "\n\n".join(parts) if parts else "검색된 관련 정보가 없습니다."

        # 3️⃣ LCEL 파이프라인 구성
        chain = (
                {
                    "context": RunnablePassthrough()
                               | (lambda x: self.retriever.retrieve(x["question"], top_k=10))
                               | format_docs,
                    "question": RunnablePassthrough() | (lambda x: x["question"])
                }
                | rag_prompt
                | self.llm
                | StrOutputParser()
        )

        return chain

    def invoke(self, user_question: str) -> str:
        """
        LCEL 체인 실행

        Args:
            user_question: 사용자 질문

        Returns:
            생성된 답변
        """
        print(f"\n{'=' * 60}")
        print(f"🔗 LCEL 파이프라인 실행 (카테고리: {self.category})")
        print(f"{'=' * 60}")
        print(f"📝 질문: {user_question}\n")

        try:
            response = self.chain.invoke({"question": user_question})

            print(f"✅ LCEL 파이프라인 완료")
            print(f"📄 응답 길이: {len(response)}자\n")
            print(f"{'=' * 60}\n")

            return response
        except Exception as e:
            print(f"❌ LCEL 실행 실패: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return f"오류가 발생했습니다: {str(e)}"
