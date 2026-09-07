from langchain_core.prompts import PromptTemplate

# 일반 답변 프롬프트
GENERAL_PROMPT = PromptTemplate(
    input_variables=['context', 'question'],
    template="""당신은 쇼핑몰 고객 서비스 담당자입니다.

정책 문서:
{context}

질문: {question}

친절하게 답변해주세요."""
)

# 배송 관련 특화 프롬프트
SHIPPING_PROMPT = PromptTemplate(
    input_variables=['context', 'question'],
    template="""당신은 배송 전문 상담사입니다.

배송 정책:
{context}

고객 질문: {question}

정확하고 친절하게 답변해주세요."""
)

# 반품 관련 특화 프롬프트
RETURN_PROMPT = PromptTemplate(
    input_variables=['context', 'question'],
    template="""당신은 반품 처리 전문가입니다.

반품 정책:
{context}

고객 질문: {question}

정책에 따라 정확하게 답변해주세요."""
)

# 카테고리 분류 키워드
CATEGORY_KEYWORDS = {
    'shipping': ['배송', '언제', '얼마나', '배달', '도착', '며칠', '배송료'],
    'return': ['반품', '환불', '교환', '불량', '손상', '반품료', '반품정책']
}
