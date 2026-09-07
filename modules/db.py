import sqlite3
from datetime import datetime
from pathlib import Path
from config import DB_PATH, DATABASE_TIMEOUT


class ChatDatabase:
    def __init__(self):
        """데이터베이스 초기화"""
        self.db_path = Path(DB_PATH)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """데이터베이스 테이블 생성"""
        try:
            conn = sqlite3.connect(str(self.db_path), timeout=DATABASE_TIMEOUT)
            cursor = conn.cursor()

            # 채팅 히스토리 테이블
            cursor.execute('''
                           CREATE TABLE IF NOT EXISTS chat_history
                           (
                               id
                               INTEGER
                               PRIMARY
                               KEY
                               AUTOINCREMENT,
                               timestamp
                               DATETIME
                               DEFAULT
                               CURRENT_TIMESTAMP,
                               user_message
                               TEXT
                               NOT
                               NULL,
                               assistant_message
                               TEXT
                               NOT
                               NULL,
                               rating
                               INTEGER
                               DEFAULT
                               NULL
                           )
                           ''')

            conn.commit()
            conn.close()
            print(f"✅ Database initialized at {self.db_path}")
        except Exception as e:
            print(f"❌ Database init error: {e}")

    def save_chat(self, user_message: str, assistant_message: str) -> int:
        """채팅 저장 후 ID 반환"""
        try:
            conn = sqlite3.connect(str(self.db_path), timeout=DATABASE_TIMEOUT)
            cursor = conn.cursor()
            cursor.execute('''
                           INSERT INTO chat_history (user_message, assistant_message)
                           VALUES (?, ?)
                           ''', (user_message, assistant_message))
            conn.commit()
            chat_id = cursor.lastrowid
            conn.close()
            print(f"✅ Chat saved (ID: {chat_id})")
            return chat_id
        except Exception as e:
            print(f"❌ Save chat error: {e}")
            return -1

    def save_rating(self, chat_id: int, rating: int) -> bool:
        """평가 저장 (1=좋음, 3=보통, 5=나쁨)"""
        try:
            conn = sqlite3.connect(str(self.db_path), timeout=DATABASE_TIMEOUT)
            cursor = conn.cursor()
            cursor.execute('''
                           UPDATE chat_history
                           SET rating = ?
                           WHERE id = ?
                           ''', (rating, chat_id))
            affected_rows = cursor.rowcount
            conn.commit()
            conn.close()
            print(f"✅ Rating saved for chat {chat_id}: {rating} (affected: {affected_rows})")
            return True
        except Exception as e:
            print(f"❌ Rating save error: {e}")
            return False

    def get_chat_history(self, limit: int = 50):
        """최근 채팅 조회"""
        try:
            conn = sqlite3.connect(str(self.db_path), timeout=DATABASE_TIMEOUT)
            cursor = conn.cursor()
            cursor.execute('''
                           SELECT id, timestamp, user_message, assistant_message, rating
                           FROM chat_history
                           ORDER BY timestamp DESC
                               LIMIT ?
                           ''', (limit,))
            chats = cursor.fetchall()
            conn.close()
            return chats
        except Exception as e:
            print(f"❌ Get history error: {e}")
            return []

    def get_statistics(self):
        """통계 조회 (평균 평점 포함)"""
        try:
            conn = sqlite3.connect(str(self.db_path), timeout=DATABASE_TIMEOUT)
            cursor = conn.cursor()

            # 총 대화 수
            cursor.execute('SELECT COUNT(*) FROM chat_history')
            total_chats = cursor.fetchone()[0] or 0
            print(f"DEBUG: total_chats = {total_chats}")

            # 평가된 대화 수
            cursor.execute('SELECT COUNT(*) FROM chat_history WHERE rating IS NOT NULL')
            rated_chats = cursor.fetchone()[0] or 0
            print(f"DEBUG: rated_chats = {rated_chats}")

            # 평균 평점 (정수 변환)
            cursor.execute('''
                           SELECT AVG(CAST(rating AS FLOAT))
                           FROM chat_history
                           WHERE rating IS NOT NULL
                           ''')
            avg_result = cursor.fetchone()[0]
            avg_rating = round(avg_result, 2) if avg_result else 0
            print(f"DEBUG: avg_rating = {avg_rating}")

            # 각 평점별 개수
            cursor.execute('SELECT COUNT(*) FROM chat_history WHERE rating = 1')
            good_count = cursor.fetchone()[0] or 0

            cursor.execute('SELECT COUNT(*) FROM chat_history WHERE rating = 3')
            normal_count = cursor.fetchone()[0] or 0

            cursor.execute('SELECT COUNT(*) FROM chat_history WHERE rating = 5')
            bad_count = cursor.fetchone()[0] or 0

            print(f"DEBUG: good={good_count}, normal={normal_count}, bad={bad_count}")

            conn.close()

            # 만족도 계산 (좋음 / 전체 * 100)
            satisfaction = (good_count / total_chats * 100) if total_chats > 0 else 0

            return {
                'total_chats': total_chats,
                'avg_rating': avg_rating,
                'good_count': good_count,
                'normal_count': normal_count,
                'bad_count': bad_count,
                'satisfaction': round(satisfaction, 1),
                'rated_chats': rated_chats
            }
        except Exception as e:
            print(f"❌ Get statistics error: {e}")
            import traceback
            traceback.print_exc()
            return {
                'total_chats': 0,
                'avg_rating': 0,
                'good_count': 0,
                'normal_count': 0,
                'bad_count': 0,
                'satisfaction': 0,
                'rated_chats': 0
            }

    def clear_history(self):
        """히스토리 초기화"""
        try:
            conn = sqlite3.connect(str(self.db_path), timeout=DATABASE_TIMEOUT)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM chat_history')
            conn.commit()
            conn.close()
            print("✅ History cleared")
        except Exception as e:
            print(f"❌ Clear history error: {e}")

    def get_recent_chats(self, limit: int = 10):
        """최근 채팅 조회"""
        return self.get_chat_history(limit=limit)
