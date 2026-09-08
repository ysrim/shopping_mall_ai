# features/shared/db.py
import sqlite3
from pathlib import Path
from config import DB_PATH, DATABASE_TIMEOUT


class ChatDatabase:
    """채팅 히스토리 및 평가 관리"""

    def __init__(self):
        """데이터베이스 초기화"""
        self.db_path = DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = None
        self._init_db()

    def _init_db(self):
        """데이터베이스 테이블 초기화"""
        try:
            self.conn = sqlite3.connect(str(self.db_path), timeout=DATABASE_TIMEOUT)
            self.conn.row_factory = sqlite3.Row
            cursor = self.conn.cursor()

            # 테이블 생성
            cursor.execute("""
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
                           )
                           """)
            self.conn.commit()
            print("✅ 데이터베이스 초기화 완료")
        except Exception as e:
            print(f"❌ 데이터베이스 초기화 오류: {e}")

    def save_chat(self, user_message: str, assistant_message: str) -> int:
        """
        대화 저장

        Args:
            user_message: 사용자 메시지
            assistant_message: AI 응답

        Returns:
            채팅 ID
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO chat_history (user_message, assistant_message) VALUES (?, ?)",
                (user_message, assistant_message)
            )
            self.conn.commit()
            chat_id = cursor.lastrowid
            print(f"✅ 채팅 저장 완료 (ID: {chat_id})")
            return chat_id
        except Exception as e:
            print(f"❌ 채팅 저장 오류: {e}")
            return -1

    def save_rating(self, chat_id: int, rating: int) -> bool:
        """
        평가 저장

        Args:
            chat_id: 채팅 ID
            rating: 평점 (-1: 나쁨, 0: 보통, 1: 좋음)

        Returns:
            성공 여부
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "UPDATE chat_history SET rating = ? WHERE id = ?",
                (rating, chat_id)
            )
            self.conn.commit()
            if cursor.rowcount > 0:
                print(f"✅ 평가 저장 완료 (ID: {chat_id}, 평점: {rating})")
                return True
            return False
        except Exception as e:
            print(f"❌ 평가 저장 오류: {e}")
            return False

    def get_chat_history(self) -> list:
        """
        채팅 히스토리 조회

        Returns:
            히스토리 리스트
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT id, timestamp, user_message, assistant_message, rating FROM chat_history ORDER BY id ASC"
            )
            rows = cursor.fetchall()
            return [
                {
                    'id': row[0],
                    'timestamp': row[1],
                    'user_message': row[2],
                    'assistant_message': row[3],
                    'rating': row[4]
                }
                for row in rows
            ]
        except Exception as e:
            print(f"❌ 히스토리 조회 오류: {e}")
            return []

    def get_statistics(self) -> dict:
        """
        통계 정보 조회

        Returns:
            통계 딕셔너리
        """
        try:
            cursor = self.conn.cursor()

            # 전체 채팅 수
            cursor.execute("SELECT COUNT(*) FROM chat_history")
            total_chats = cursor.fetchone()[0]

            # 평균 평점
            cursor.execute("SELECT AVG(rating) FROM chat_history WHERE rating IS NOT NULL")
            avg_rating = cursor.fetchone()[0] or 0

            # 좋음 개수
            cursor.execute("SELECT COUNT(*) FROM chat_history WHERE rating = 1")
            like_count = cursor.fetchone()[0]

            # 보통 개수
            cursor.execute("SELECT COUNT(*) FROM chat_history WHERE rating = 0")
            neutral_count = cursor.fetchone()[0]

            # 나쁨 개수
            cursor.execute("SELECT COUNT(*) FROM chat_history WHERE rating = -1")
            dislike_count = cursor.fetchone()[0]

            return {
                'total_chats': total_chats,
                'avg_rating': float(avg_rating),
                'like_count': like_count,
                'neutral_count': neutral_count,
                'dislike_count': dislike_count
            }
        except Exception as e:
            print(f"❌ 통계 조회 오류: {e}")
            return {
                'total_chats': 0,
                'avg_rating': 0,
                'like_count': 0,
                'neutral_count': 0,
                'dislike_count': 0
            }

    def clear_history(self):
        """히스토리 전체 삭제"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM chat_history")
            self.conn.commit()
            print("✅ 히스토리 전체 삭제 완료")
        except Exception as e:
            print(f"❌ 히스토리 삭제 오류: {e}")

    def get_recent_chats(self, limit: int = 5) -> list:
        """
        최근 대화 조회

        Args:
            limit: 조회 개수

        Returns:
            최근 대화 리스트
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT id, user_message, assistant_message FROM chat_history ORDER BY id DESC LIMIT ?",
                (limit,)
            )
            return cursor.fetchall()
        except Exception as e:
            print(f"❌ 최근 대화 조회 오류: {e}")
            return []
