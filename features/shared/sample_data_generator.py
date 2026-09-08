import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import random

DB_PATH = Path("data/chat.db")


class SampleDataGenerator:
    """
    쇼핑몰 대화 샘플 데이터를 생성합니다.
    반품정책, 배송정책 등 다양한 주제의 Q&A를 포함합니다.
    """

    # 샘플 질문-답변 쌍들
    SAMPLE_DIALOGS = [
        # ==================== 배송 정책 ====================
        {
            "question": "배송료는 얼마예요?",
            "answer": "배송료는 주문 금액에 따라 다릅니다. 30,000원 이상 주문 시 무료 배송, 미만일 경우 2,500원입니다. 제주도/도서산간 지역은 추가 5,000원이 발생합니다.",
            "category": "배송",
            "rating": 1
        },
        {
            "question": "배송은 며칠 걸려요?",
            "answer": "일반 배송은 주중 기준 2-3일 소요됩니다. 제주/도서산간 지역은 3-5일 추가로 걸릴 수 있습니다. 주말/공휴일은 배송이 없습니다.",
            "category": "배송",
            "rating": 1
        },
        {
            "question": "당일배송이 가능한가요?",
            "answer": "네, 서울/경기 지역에 한해 당일배송이 가능합니다. 오후 2시 이전에 주문하면 당일배송되며, 배송비는 3,000원입니다.",
            "category": "배송",
            "rating": 1
        },
        {
            "question": "배송 조회는 어떻게 하나요?",
            "answer": "주문 후 1시간 이내에 배송장번호가 SMS/이메일로 발송됩니다. 마이페이지의 '주문 조회'에서 배송 상태를 실시간으로 확인할 수 있습니다.",
            "category": "배송",
            "rating": 1
        },
        {
            "question": "제주도로 배송 가능한가요?",
            "answer": "네, 제주도로 배송 가능합니다. 다만 배송비가 추가로 5,000원 발생하며, 일반 배송보다 3-5일 더 소요됩니다.",
            "category": "배송",
            "rating": 1
        },
        {
            "question": "산간지역으로 배송 가능한가요?",
            "answer": "산간벽지의 경우 택배사 제약으로 배송이 불가능할 수 있습니다. 주문 시 배송 가능 여부를 확인해주시거나, 고객센터로 문의해주세요.",
            "category": "배송",
            "rating": 0
        },
        {
            "question": "배송을 받지 못했어요.",
            "answer": "배송장번호로 배송 상태를 확인해주세요. 배송 지연이 발생한 경우 1-2일 더 대기 후 도착하지 않으면 고객센터(02-XXXX-XXXX)로 연락 주세요.",
            "category": "배송",
            "rating": -1
        },
        {
            "question": "야간 배송이 가능한가요?",
            "answer": "야간 배송은 불가능합니다. 새벽 6시 ~ 오전 9시 사이에는 배송이 이루어지지 않습니다.",
            "category": "배송",
            "rating": 0
        },
        {
            "question": "배송 주소를 변경할 수 있나요?",
            "answer": "배송장번호가 발급되기 전이면 마이페이지에서 주소 변경이 가능합니다. 이미 배송장번호가 발급된 경우 고객센터로 연락해주세요.",
            "category": "배송",
            "rating": 1
        },
        {
            "question": "군부대로 배송 가능한가요?",
            "answer": "죄송하지만, 군부대, 교도소 등 특수시설로는 배송이 불가능합니다. 대신 근처 일반 주소로 배송받으신 후 수령하시기 바랍니다.",
            "category": "배송",
            "rating": 0
        },

        # ==================== 반품 정책 ====================
        {
            "question": "반품은 언제까지 가능한가요?",
            "answer": "구매 후 14일 이내에 반품 신청이 가능합니다. 미개봉/미사용 상태여야 하며, 택이 제거되지 않은 상품만 반품 가능합니다.",
            "category": "반품",
            "rating": 1
        },
        {
            "question": "반품 절차는 어떻게 되나요?",
            "answer": "1) 고객센터(02-XXXX-XXXX)에 반품 신청 → 2) 반송 배송비 확인 → 3) 상품 반송 → 4) 창고 수령 후 환불 처리. 환불까지 영업일 기준 3-5일 소요됩니다.",
            "category": "반품",
            "rating": 1
        },
        {
            "question": "반품 배송료는?",
            "answer": "상품 불량이나 배송 오류인 경우 반품 배송료가 무료입니다. 고객 변심인 경우 2,500원(선불)의 배송료가 발생합니다.",
            "category": "반품",
            "rating": 1
        },
        {
            "question": "반품 후 환불은 언제 되나요?",
            "answer": "반품 상품을 창고에서 수령한 후 3-5 영업일 이내에 환불됩니다. 결제 수단별로 신용카드 1-3일, 계좌이체 1-2일, 핸드폰결제 2-3일이 소요됩니다.",
            "category": "반품",
            "rating": 1
        },
        {
            "question": "식품도 반품 가능한가요?",
            "answer": "죄송하지만, 식품과 음료는 반품이 불가능합니다. 위생상 이유로 상품 수령 후 반품 불가 정책을 운영하고 있습니다.",
            "category": "반품",
            "rating": 0
        },
        {
            "question": "화장품은 반품 가능한가요?",
            "answer": "화장품과 향수는 개봉 여부와 관계없이 반품이 불가능합니다. 안전 및 위생상 이유로 이 정책을 유지하고 있습니다.",
            "category": "반품",
            "rating": 0
        },
        {
            "question": "의료용품도 반품 불가인가요?",
            "answer": "네, 의료용품, 약품, 개인 위생용품은 모두 반품이 불가능합니다. 구매 전 상품 정보를 꼼꼼히 확인해주세요.",
            "category": "반품",
            "rating": 0
        },
        {
            "question": "이미 사용한 상품도 반품 가능한가요?",
            "answer": "아니요, 개봉하거나 사용한 상품은 반품이 불가능합니다. 미개봉/미사용이면서 택이 제거되지 않은 상품만 반품 가능합니다.",
            "category": "반품",
            "rating": 1
        },
        {
            "question": "택을 제거했는데 반품 가능한가요?",
            "answer": "죄송하지만, 택을 제거한 상품은 반품이 불가능합니다. 반품을 원하신다면 택을 떼지 않은 상태로 보관해주세요.",
            "category": "반품",
            "rating": -1
        },
        {
            "question": "교환은 가능한가요?",
            "answer": "네, 14일 이내 교환이 가능합니다. 상품 결함이나 배송 오류인 경우 무료 교환 가능하며, 고객 변심인 경우 배송료가 발생합니다.",
            "category": "반품",
            "rating": 1
        },
        {
            "question": "반품할 때 원래 포장재가 없어요.",
            "answer": "원래 포장재가 없어도 반품 가능합니다. 다만 상품이 손상되지 않도록 잘 포장하여 반송해주세요.",
            "category": "반품",
            "rating": 1
        },

        # ==================== 결제 수단 ====================
        {
            "question": "신용카드로 결제할 수 있나요?",
            "answer": "네, 모든 신용카드사의 카드로 결제 가능합니다. 국내 주요 카드사를 모두 지원합니다.",
            "category": "결제",
            "rating": 1
        },
        {
            "question": "무이자 할부가 있나요?",
            "answer": "50,000원 이상 구매 시 신용카드 무이자 할부 이벤트가 진행 중입니다. 카드사별로 다를 수 있으니 확인 후 결제해주세요.",
            "category": "결제",
            "rating": 1
        },
        {
            "question": "휴대폰 결제는 가능한가요?",
            "answer": "네, 휴대폰 결제가 가능합니다. 월 한도는 통신사마다 다르니 확인 후 진행해주세요.",
            "category": "결제",
            "rating": 1
        },
        {
            "question": "계좌이체로 결제할 수 있나요?",
            "answer": "네, 계좌이체 결제가 가능합니다. 즉시 결제로 진행되며, 우리은행, 신한은행 등 주요 은행을 지원합니다.",
            "category": "결제",
            "rating": 1
        },
        {
            "question": "페이팔이나 외국 카드로 결제 가능한가요?",
            "answer": "현재는 국내 결제 수단만 지원합니다. 신용카드, 휴대폰결제, 계좌이체만 가능합니다.",
            "category": "결제",
            "rating": 0
        },
        {
            "question": "결제 후 영수증은 어떻게 받나요?",
            "answer": "결제 완료 후 이메일과 마이페이지에서 영수증을 다운로드할 수 있습니다. 필요시 고객센터로 요청하면 재발급해드립니다.",
            "category": "결제",
            "rating": 1
        },
        {
            "question": "결제 도중 오류가 났어요.",
            "answer": "결제 오류가 발생한 경우, 다시 시도하거나 다른 결제 수단을 사용해주세요. 문제가 계속되면 고객센터(02-XXXX-XXXX)로 연락해주세요.",
            "category": "결제",
            "rating": -1
        },
        {
            "question": "할부금 관련 문의가 있어요.",
            "answer": "할부 관련 상세 내용은 카드사별로 다릅니다. 결제 시점에 할부 옵션이 표시되며, 추가 문의는 해당 카드사로 연락해주세요.",
            "category": "결제",
            "rating": 0
        },

        # ==================== 상품 정보 ====================
        {
            "question": "상품 사이즈는 어떻게 되나요?",
            "answer": "상품 페이지의 '상세정보' 탭에서 사이즈 가이드를 확인하실 수 있습니다. 사이즈별 착용감 정보도 제공됩니다.",
            "category": "상품",
            "rating": 1
        },
        {
            "question": "색상 옵션은 몇 가지가 있나요?",
            "answer": "상품마다 다양한 색상 옵션이 있습니다. 상품 페이지의 옵션 버튼에서 선택 가능한 색상을 확인할 수 있습니다.",
            "category": "상품",
            "rating": 1
        },
        {
            "question": "이 상품 재입고는 언제예요?",
            "answer": "현재 품절된 상품의 재입고 일정은 상품 페이지의 '재입고 알림' 신청으로 확인하실 수 있습니다. 보통 1-2주 소요됩니다.",
            "category": "상품",
            "rating": 0
        },
        {
            "question": "상품 소재가 뭐예요?",
            "answer": "상품의 소재 정보는 상품 페이지의 '상세정보' 탭에서 확인할 수 있습니다. 세탁 방법 및 주의사항도 함께 표기되어 있습니다.",
            "category": "상품",
            "rating": 1
        },
        {
            "question": "모델이 입은 상품의 사이즈가 뭐예요?",
            "answer": "상품 페이지의 사진 하단에 모델 착용 정보가 표시됩니다. 모델의 키, 체형, 입은 사이즈를 확인할 수 있습니다.",
            "category": "상품",
            "rating": 1
        },
        {
            "question": "상품 이미지를 더 크게 보고 싶어요.",
            "answer": "상품 이미지를 클릭하면 확대되어 상세하게 볼 수 있습니다. 360도 회전 이미지도 제공되는 상품이 있습니다.",
            "category": "상품",
            "rating": 1
        },
        {
            "question": "정품 보증이 되나요?",
            "answer": "모든 상품은 100% 정품입니다. 위조품 발견 시 반품/환불이 가능하며, 고객센터로 신고해주시기 바랍니다.",
            "category": "상품",
            "rating": 1
        },

        # ==================== 회원 관련 ====================
        {
            "question": "회원가입 혜택이 뭐예요?",
            "answer": "회원가입 시 5,000원 할인 쿠폰을 드립니다. 추가로 포인트 적립 및 멤버십 등급 시스템으로 더 많은 혜택을 받으실 수 있습니다.",
            "category": "회원",
            "rating": 1
        },
        {
            "question": "비밀번호를 잊어버렸어요.",
            "answer": "로그인 페이지의 '비밀번호 찾기' 버튼을 클릭하고 이메일 인증 후 새로운 비밀번호를 설정하실 수 있습니다.",
            "category": "회원",
            "rating": 1
        },
        {
            "question": "구매 내역은 어디서 확인하나요?",
            "answer": "마이페이지의 '구매 내역' 탭에서 모든 구매 내역을 확인하실 수 있습니다. 최대 1년간의 내역이 저장됩니다.",
            "category": "회원",
            "rating": 1
        },
        {
            "question": "포인트는 어떻게 사용하나요?",
            "answer": "적립된 포인트는 다음 구매 시 1포인트 = 1원으로 결제 시 사용 가능합니다. 마이페이지에서 보유 포인트를 확인하실 수 있습니다.",
            "category": "회원",
            "rating": 1
        },
        {
            "question": "포인트는 언제 적립되나요?",
            "answer": "구매 금액의 5%가 자동으로 포인트로 적립됩니다. 배송 완료 후에 적립되며, 환불 시 차감됩니다.",
            "category": "회원",
            "rating": 1
        },
        {
            "question": "회원 탈퇴는 어떻게 하나요?",
            "answer": "마이페이지의 '회원 정보' 탭에서 '회원 탈퇴' 버튼을 클릭하면 됩니다. 탈퇴 후 보유 포인트는 소멸됩니다.",
            "category": "회원",
            "rating": 0
        },
        {
            "question": "등급이 뭔가요?",
            "answer": "회원 등급은 구매 금액에 따라 결정됩니다. SILVER(0~100만원), GOLD(100~300만원), PLATINUM(300만원 이상)이 있으며, 등급별 혜택이 다릅니다.",
            "category": "회원",
            "rating": 1
        },
        {
            "question": "생일 쿠폰이 있나요?",
            "answer": "네, 생일 달에 3,000원 생일 축하 쿠폰을 드립니다. 생일 정보를 정확하게 입력했다면 자동으로 발급됩니다.",
            "category": "회원",
            "rating": 1
        },
        {
            "question": "이메일 변경은 가능한가요?",
            "answer": "마이페이지의 '회원 정보' 탭에서 이메일을 변경할 수 있습니다. 변경 후 인증이 필요합니다.",
            "category": "회원",
            "rating": 1
        },

        # ==================== 고객센터/기타 ====================
        {
            "question": "고객센터 전화번호는?",
            "answer": "고객센터 전화번호는 02-XXXX-XXXX입니다. 평일 09:00-18:00, 토요일 10:00-16:00에 운영됩니다. 일요일/공휴일은 휴무입니다.",
            "category": "기타",
            "rating": 1
        },
        {
            "question": "이메일 문의는 어떻게 하나요?",
            "answer": "이메일 주소는 support@example.com입니다. 평일 기준 48시간 이내에 답변 드립니다.",
            "category": "기타",
            "rating": 1
        },
        {
            "question": "채팅 상담이 가능한가요?",
            "answer": "네, 홈페이지의 '채팅 상담' 버튼으로 평일 09:00-18:00 중 상담이 가능합니다.",
            "category": "기타",
            "rating": 1
        },
        {
            "question": "반품/교환 신청은 어디서 하나요?",
            "answer": "마이페이지의 '주문 조회'에서 해당 주문을 선택 후 '반품/교환 신청' 버튼을 클릭하거나, 고객센터(02-XXXX-XXXX)로 직접 신청하실 수 있습니다.",
            "category": "기타",
            "rating": 1
        },
        {
            "question": "뉴스레터는 어떻게 구독하나요?",
            "answer": "홈페이지 하단의 '뉴스레터 구독' 입력창에 이메일을 입력하면 됩니다. 최신 상품 정보와 할인 소식을 받으실 수 있습니다.",
            "category": "기타",
            "rating": 1
        },
        {
            "question": "앱에서 주문 가능한가요?",
            "answer": "네, iOS/Android 모바일 앱에서도 구매 가능합니다. 앱 전용 쿠폰도 제공됩니다.",
            "category": "기타",
            "rating": 1
        },
    ]

    def __init__(self):
        self.conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row

    def generate_sample_data(self, count_per_dialog: int = 10):
        """
        각 샘플 대화를 count_per_dialog번 반복해서 삽입합니다.
        타임스탬프는 최근 2개월 내로 랜덤 설정됩니다.
        """
        cursor = self.conn.cursor()

        print(f"\n{'=' * 60}")
        print(f"📊 샘플 데이터 생성 시작")
        print(f"{'=' * 60}\n")

        total_inserted = 0

        # 각 샘플 대화를 여러 번 반복
        for sample in self.SAMPLE_DIALOGS:
            for i in range(count_per_dialog):
                # 타임스탬프: 최근 2개월 내 랜덤
                days_ago = random.randint(0, 60)
                timestamp = (datetime.now() - timedelta(days=days_ago)).isoformat()

                # 평가를 약간 변동시킴 (일관성 있으면서도 다양함)
                rating = sample['rating']
                if random.random() < 0.2:  # 20% 확률로 다른 평가
                    rating = random.choice([-1, 0, 1])

                try:
                    cursor.execute('''
                                   INSERT INTO chats (user_message, assistant_message, category, rating, llm_provider,
                                                      timestamp)
                                   VALUES (?, ?, ?, ?, ?, ?)
                                   ''', (
                                       sample['question'],
                                       sample['answer'],
                                       sample['category'],
                                       rating,
                                       'ollama',
                                       timestamp
                                   ))
                    total_inserted += 1
                except Exception as e:
                    print(f"❌ 삽입 실패: {e}")

        self.conn.commit()

        # 통계 계산
        cursor.execute('SELECT COUNT(*) as total FROM chats')
        total_in_db = cursor.fetchone()['total']

        cursor.execute('SELECT COUNT(DISTINCT category) as categories FROM chats')
        category_count = cursor.fetchone()['categories']

        print(f"✅ 총 {total_inserted}개의 샘플 데이터 삽입 완료!")
        print(f"\n📊 요약:")
        print(f"  - 총 샘플 대화 유형: {len(self.SAMPLE_DIALOGS)}개")
        print(f"  - 각 유형별 반복: {count_per_dialog}회")
        print(f"  - 총 삽입된 데이터: {total_inserted}개")
        print(f"  - DB에 저장된 전체 데이터: {total_in_db}개")
        print(f"  - 카테고리 수: {category_count}개")
        print(f"    • 배송 (Shipping): 10개 질문")
        print(f"    • 반품 (Return): 12개 질문")
        print(f"    • 결제 (Payment): 8개 질문")
        print(f"    • 상품 (Product): 7개 질문")
        print(f"    • 회원 (Member): 9개 질문")
        print(f"    • 기타 (Other): 6개 질문")
        print(f"{'=' * 60}\n")

        return total_inserted

    def clear_sample_data(self):
        """모든 데이터를 삭제합니다."""
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM chats')
        self.conn.commit()
        print("✅ 모든 데이터 삭제 완료")

    def close(self):
        self.conn.close()
