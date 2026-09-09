import sqlite3
from pathlib import Path
import threading
from datetime import datetime

DB_PATH = Path("data/chat.db")

_thread_local = threading.local()


def _get_connection():
    if not hasattr(_thread_local, 'connection') or _thread_local.connection is None:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(DB_PATH), check_same_thread=False, timeout=10.0)
        conn.row_factory = sqlite3.Row
        _thread_local.connection = conn
    return _thread_local.connection


class ChatDatabase:
    def __init__(self):
        self.conn = _get_connection()
        self._create_tables()
        print("✅ ChatDatabase 초기화 완료")

    def _create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS chats
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           user_message
                           TEXT
                           NOT
                           NULL,
                           assistant_message
                           TEXT
                           NOT
                           NULL,
                           category
                           TEXT,
                           rating
                           INTEGER
                           DEFAULT
                           0,
                           llm_provider
                           TEXT,
                           timestamp
                           DATETIME
                           DEFAULT
                           CURRENT_TIMESTAMP
                       )
                       ''')
        self.conn.commit()
        print("✅ 테이블 생성 완료")

    def save_chat(self, user_message: str, assistant_message: str, category: str = None,
                  llm_provider: str = None) -> int:
        """대화를 저장합니다."""
        try:
            cursor = self.conn.cursor()
            current_time = datetime.now().isoformat()

            cursor.execute('''
                           INSERT INTO chats (user_message, assistant_message, category, llm_provider, timestamp)
                           VALUES (?, ?, ?, ?, ?)
                           ''', (user_message, assistant_message, category, llm_provider, current_time))

            self.conn.commit()
            chat_id = cursor.lastrowid
            print(f"✅ 대화 저장: ID={chat_id}, 카테고리={category}, 시간={current_time}")
            return chat_id
        except Exception as e:
            print(f"❌ 대화 저장 실패: {e}")
            raise

    def get_history(self, limit: int = 50):
        """대화 이력을 조회합니다 (최신순)."""
        try:
            cursor = self.conn.cursor()

            # 🎯 수정: ID 기준으로 정렬 (timestamp 보다 확실함)
            cursor.execute('''
                           SELECT id, user_message, assistant_message, category, rating, llm_provider, timestamp
                           FROM chats
                           ORDER BY id DESC
                               LIMIT ?
                           ''', (limit,))

            results = [dict(row) for row in cursor.fetchall()]

            print(f"✅ 대화 이력 조회: {len(results)}개 (ID 내림차순)")

            # 디버그: 첫 3개 표시
            if results:
                for i, r in enumerate(results[:3], 1):
                    print(f"   [{i}] ID={r['id']}, 시간={r['timestamp']}, 질문={r['user_message'][:30]}...")

            return results

        except Exception as e:
            print(f"❌ 대화 이력 조회 실패: {e}")
            import traceback
            print(traceback.format_exc())
            return []

    def rate_message(self, chat_id: int, rating: int) -> bool:
        """대화에 평가를 저장합니다."""
        try:
            cursor = self.conn.cursor()
            cursor.execute('UPDATE chats SET rating = ? WHERE id = ?', (rating, chat_id))
            self.conn.commit()

            rating_emoji = {1: "👍", 0: "😐", -1: "👎"}.get(rating, "❓")
            print(f"✅ 평가 저장: ID={chat_id}, 평가={rating_emoji}")
            return True

        except Exception as e:
            print(f"❌ 평가 저장 실패: {e}")
            return False

    def delete_chat(self, chat_id: int) -> bool:
        """특정 대화를 삭제합니다."""
        try:
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM chats WHERE id = ?', (chat_id,))
            self.conn.commit()
            print(f"✅ 대화 삭제: ID={chat_id}")
            return True

        except Exception as e:
            print(f"❌ 대화 삭제 실패: {e}")
            return False

    def clear_history(self) -> bool:
        """모든 대화를 삭제합니다."""
        try:
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM chats')
            self.conn.commit()
            print("✅ 모든 대화 삭제 완료")
            return True

        except Exception as e:
            print(f"❌ 모든 대화 삭제 실패: {e}")
            return False

    def get_statistics(self):
        """전체 통계를 반환합니다."""
        try:
            cursor = self.conn.cursor()

            # 1. 총 대화 수
            cursor.execute('SELECT COUNT(*) as total FROM chats')
            total = cursor.fetchone()['total']

            # 2. 평가된 대화
            cursor.execute('SELECT COUNT(*) as rated FROM chats WHERE rating != 0')
            rated = cursor.fetchone()['rated']

            # 3. 좋음 (👍)
            cursor.execute('SELECT COUNT(*) as positive FROM chats WHERE rating = 1')
            positive = cursor.fetchone()['positive']

            # 4. 보통 (😐)
            cursor.execute('SELECT COUNT(*) as neutral FROM chats WHERE rating = 0')
            neutral = cursor.fetchone()['neutral']

            # 5. 나쁨 (👎)
            cursor.execute('SELECT COUNT(*) as negative FROM chats WHERE rating = -1')
            negative = cursor.fetchone()['negative']

            print(f"✅ 통계 조회: 총 {total}개, 평가됨 {rated}개 (👍 {positive}, 😐 {neutral}, 👎 {negative})")

            return {
                'total_chats': total,
                'total_rated': rated,
                'positive_count': positive,
                'neutral_count': neutral,
                'negative_count': negative,
            }

        except Exception as e:
            print(f"❌ 통계 조회 실패: {e}")
            return {
                'total_chats': 0,
                'total_rated': 0,
                'positive_count': 0,
                'neutral_count': 0,
                'negative_count': 0,
            }

    def get_top_questions(self, limit: int = 10):
        """
        자주 받는 질문 TOP N을 반환합니다.
        같은 질문이 여러 번 나온 경우를 카운트합니다.
        """
        try:
            cursor = self.conn.cursor()

            cursor.execute('''
                           SELECT user_message,
                                  category,
                                  COUNT(*) as count,
                       COALESCE(AVG(CASE WHEN rating = 1 THEN 1 WHEN rating = -1 THEN 0 WHEN rating = 0 THEN 0.5 END), 0.5) as avg_satisfaction,
                       MIN(timestamp) as first_asked,
                       MAX(timestamp) as last_asked
                           FROM chats
                           GROUP BY user_message
                           ORDER BY count DESC, avg_satisfaction DESC
                               LIMIT ?
                           ''', (limit,))

            results = [dict(row) for row in cursor.fetchall()]
            print(f"✅ TOP {limit} 질문 조회 완료 (총 {len(results)}개)")

            # 결과 검증 및 로그
            for idx, r in enumerate(results, 1):
                if r['avg_satisfaction'] is None:
                    r['avg_satisfaction'] = 0.5
                print(f"   #{idx}. {r['user_message'][:40]} | 횟수: {r['count']}, 만족도: {r['avg_satisfaction']:.2f}")

            return results

        except Exception as e:
            print(f"❌ TOP 질문 조회 실패: {e}")
            import traceback
            print(traceback.format_exc())
            return []

    def get_category_stats(self):
        """
        카테고리별 질문 수, 만족도를 반환합니다.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                           SELECT category,
                                  COUNT(*)                                              as total,
                                  SUM(CASE WHEN rating = 1 THEN 1 ELSE 0 END)           as positive,
                                  SUM(CASE WHEN rating = -1 THEN 1 ELSE 0 END)          as negative,
                                  ROUND(AVG(CASE
                                                WHEN rating = 1 THEN 1
                                                WHEN rating = -1 THEN 0
                                                WHEN rating = 0 THEN 0.5 END) * 100, 1) as satisfaction_rate
                           FROM chats
                           WHERE category IS NOT NULL
                           GROUP BY category
                           ORDER BY total DESC
                           ''')

            results = [dict(row) for row in cursor.fetchall()]
            print(f"✅ 카테고리 통계 조회 완료 (총 {len(results)}개 카테고리)")

            # 결과 로그
            for r in results:
                print(f"   - {r['category']}: {r['total']}개, 만족도 {r['satisfaction_rate']}%")

            return results

        except Exception as e:
            print(f"❌ 카테고리 통계 조회 실패: {e}")
            return []

    def close(self):
        """데이터베이스 연결을 종료합니다."""
        if hasattr(_thread_local, 'connection') and _thread_local.connection:
            _thread_local.connection.close()
            print("✅ 데이터베이스 연결 종료")
