from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from typing import Dict, Any


class RAGChain:
    """LCEL 기반 RAG 파이프라인 체인"""

    def __init__(self, llm, retriever):
        """
        RAG 체인 초기화

        Args:
            llm: LangChain LLM 인스턴스
            retriever: 문서 검색기
        """
        self.llm = llm
        self.retriever = retriever
        self.chain = self._build_chain()

    def _build_chain(self):
        """LCEL 파이프라인 구축 (명시적 파이프 연산자 사용)"""

        # 1️⃣ RAG 프롬프트 템플릿 정의
        rag_prompt = PromptTemplate(
            template="""당신은 전문적이고 친절한 쇼핑 고객 서비스 어시스턴트입니다.
아래의 제공된 정보를 바탕으로 사용자의 질문에 정확하고 도움이 되는 답변을 해주세요.

【제공된 정보】
{context}

【사용자의 질문】
{question}

【답변 지침】
1. 제공된 정보에서 질문과 관련된 내용을 모두 찾아서 답변하세요.
2. 배송 기간, 배송비, 배송 방법, 회원등급, 반품정책 등 구체적인 정보를 포함하세요.
3. 정보에 없는 내용은 "해당 정보는 제공되지 않았습니다"라고 명확히 답변하세요.
4. 친절하고 존중하는 태도로 답변하세요.
5. 필요한 경우 요약이나 구조화된 형식으로 답변하세요.

답변:""",
            input_variables=["context", "question"]
        )

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

        # 3️⃣ LCEL 파이프라인 구성 (| 연산자 사용)
        # 구조: input → retriever → format → prompt → llm → output_parser → string
        chain = (
                {
                    "context": RunnablePassthrough()
                               | (lambda x: self.retriever.retrieve(x["question"], top_k=10))
                               | format_docs,
                    "question": RunnablePassthrough() | (lambda x: x["question"])
                }
                | rag_prompt  # 프롬프트에 context, question 주입
                | self.llm  # LLM 호출
                | StrOutputParser()  # 문자열로 파싱
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
        print(f"🔗 LCEL 파이프라인 실행")
        print(f"{'=' * 60}")
        print(f"📝 질문: {user_question}\n")

        try:
            # LCEL 체인 실행 (자동으로 모든 단계 처리)
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
