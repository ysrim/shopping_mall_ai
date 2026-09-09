from langchain_core.prompts import PromptTemplate

# ==================== 일반 프롬프트 ====================
GENERAL_PROMPT = PromptTemplate(
    input_variables=['context', 'question'],
    template="""당신은 전문적이고 친절한 쇼핑 고객 서비스 어시스턴트입니다.

제공된 정보:
{context}

질문: {question}

정보를 바탕으로 친절하고 정확하게 답변해주세요."""
)

# ==================== 배송 특화 프롬프트 ====================
SHIPPING_PROMPT = PromptTemplate(
    input_variables=['context', 'question'],
    template="""당신은 배송 전문 상담사입니다.

배송 정책:
{context}

고객 질문: {question}

다음 정보를 포함하여 정확하고 친절하게 답변해주세요:
- 배송 기간
- 배송료 (지역별, 금액별)
- 배송 추적 방법
- 배송 불가 지역 (있다면)"""
)

# ==================== 반품 특화 프롬프트 ====================
RETURN_PROMPT = PromptTemplate(
    input_variables=['context', 'question'],
    template="""당신은 반품 처리 전문가입니다.

반품 정책:
{context}

고객 질문: {question}

다음을 명확히 설명해주세요:
- 반품 기한
- 반품 조건 (개봉/미개봉, 사용 상태 등)
- 반품 절차
- 반품 불가 상품"""
)

# ==================== 환불 특화 프롬프트 ====================
REFUND_PROMPT = PromptTemplate(
    input_variables=['context', 'question'],
    template="""당신은 환불 처리 전문가입니다.

환불 정책:
{context}

고객 질문: {question}

다음을 명확히 설명해주세요:
- 환불 기한
- 환불 방식 (무료/유료)
- 환불 절차
- 환불 금액 계산
- 환불 완료 시간"""
)

# ==================== 결제 특화 프롬프트 ====================
PAYMENT_PROMPT = PromptTemplate(
    input_variables=['context', 'question'],
    template="""당신은 결제 전문 상담사입니다.

결제 정책:
{context}

고객 질문: {question}

다음을 명확히 설명해주세요:
- 사용 가능한 결제 수단
- 할부 조건 (무이자/유이자)
- 결제 보안 (OTP, 암호화 등)
- 결제 실패 원인 및 해결책"""
)

# ==================== AS 특화 프롬프트 ====================
AS_PROMPT = PromptTemplate(
    input_variables=['context', 'question'],
    template="""당신은 AS(품질보증) 전문가입니다.

AS 정책:
{context}

고객 질문: {question}

다음을 명확히 설명해주세요:
- AS 보증 기간
- AS 대상 상품
- 무상/유상 구분 기준
- AS 신청 방법
- 수리 기간 및 배송료"""
)

# ==================== 회원 특화 프롬프트 ====================
MEMBERSHIP_PROMPT = PromptTemplate(
    input_variables=['context', 'question'],
    template="""당신은 회원 관리 전문가입니다.

회원 정책:
{context}

고객 질문: {question}

다음을 명확히 설명해주세요:
- 회원 등급 및 혜택
- 포인트 적립/사용 방법
- 회원 정보 관리 (비밀번호, 이메일, 배송지 등)
- 개인정보 보호 및 보안"""
)

# ==================== 카테고리별 프롬프트 매핑 ====================
CATEGORY_PROMPTS = {
    'shipping': SHIPPING_PROMPT,
    'return': RETURN_PROMPT,
    'refund': REFUND_PROMPT,
    'payment': PAYMENT_PROMPT,
    'as': AS_PROMPT,
    'membership': MEMBERSHIP_PROMPT,
    'general': GENERAL_PROMPT,
}

# ==================== 카테고리 분류 키워드 ====================
CATEGORY_KEYWORDS = {
    'shipping': [
        '배송', '언제', '얼마나', '배달', '도착', '며칠', '배송료',
        '배송 기간', '배송지', '배송비', '배송 추적', '배송 상태',
        '언제 도착', '빠른 배송', '택배'
    ],
    'return': [
        '반품', '교환', '불량', '손상', '반품료', '반품정책',
        '반품 기한', '반품 방법', '반품 절차', '반품 불가', '교환하고 싶어'
    ],
    'refund': [
        '환불', '환불정책', '환불 기한', '환불 방법', '환불 절차',
        '환불 불가', '돈 돌려받고 싶어', '환불해주세요', '환불 신청',
        '환불 완료', '환불 금액'
    ],
    'payment': [
        '결제', '결제정책', '결제 수단', '할부', '결제 실패',
        '결제 보안', '무이자 할부', '결제 취소', '결제방법', '어떻게 결제',
        '신용카드', '계좌이체', '휴대폰 결제', '포인트 결제'
    ],
    'as': [
        '보증', 'AS', 'A/S', '수리', '수리 기간', '품질보증', '고장',
        '고장났어요', '안 돼요', '먹통', '작동 안 함', 'AS 신청',
        '무상 수리', '유상 수리'
    ],
    'membership': [
        '회원', '등급', '포인트', '포인트 적립', '포인트 사용', '생일 쿠폰',
        '멤버십', '회원정보', '비밀번호', '이메일', '배송지', '회원 탈퇴',
        '회원등급 확인', '포인트 조회', '계정', '로그인'
    ]
}


# ==================== 함수 ====================

def get_prompt_by_category(category: str) -> PromptTemplate:
    """
    카테고리에 따라 적절한 프롬프트 반환

    Args:
        category: 카테고리명 ('shipping', 'return', 'refund', 'payment', 'as', 'membership', 'general')

    Returns:
        PromptTemplate 인스턴스
    """
    return CATEGORY_PROMPTS.get(category, GENERAL_PROMPT)


def classify_category(question: str) -> str:
    """
    질문을 분석하여 카테고리 분류 (키워드 기반)

    Args:
        question: 사용자 질문

    Returns:
        카테고리명
    """
    question_lower = question.lower()

    # 점수 기반 분류
    scores = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword in question_lower)
        if score > 0:
            scores[category] = score

    # 최고 점수 카테고리 반환 (없으면 general)
    return max(scores, key=scores.get) if scores else 'general'
