import sqlite3
from pathlib import Path
from config import DATA_DIR
from datetime import datetime


class ChatDatabase:
    def __init__(self):
        self.db_path = DATA_DIR / "chat.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = None
        self._init_db()

    def _init_db(self):
        """데이터베이스 초기화"""
        try:
            self.conn = sqlite3.connect(str(self.db_path), timeout=10)
            self.conn.row_factory = sqlite3.Row
            cursor = self.conn.cursor()

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
            print("✅ Database initialized")
        except Exception as e:
            print(f"❌ Database init error: {e}")

    def save_chat(self, user_message: str, assistant_message: str) -> int:
        """대화 저장"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO chat_history (user_message, assistant_message) VALUES (?, ?)",
                (user_message, assistant_message)
            )
            self.conn.commit()
            chat_id = cursor.lastrowid
            print(f"✅ Chat saved (ID: {chat_id})")
            return chat_id
        except Exception as e:
            print(f"❌ Chat save error: {e}")
            return -1

    def save_rating(self, chat_id: int, rating: int) -> bool:
        """평가 저장"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "UPDATE chat_history SET rating = ? WHERE id = ?",
                (rating, chat_id)
            )
            self.conn.commit()
            if cursor.rowcount > 0:
                print(f"✅ Rating saved for chat {chat_id}: {rating}")
                return True
            return False
        except Exception as e:
            print(f"❌ Rating save error: {e}")
            return False

    def get_chat_history(self) -> list:
        """대화 히스토리 조회"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT id, timestamp, user_message, assistant_message, rating FROM chat_history ORDER BY id ASC"
                # DESC → ASC
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
            print(f"❌ Chat history error: {e}")
            return []

    def get_statistics(self) -> dict:
        """통계 정보 조회"""
        try:
            cursor = self.conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM chat_history")
            total_chats = cursor.fetchone()[0]

            cursor.execute("SELECT AVG(rating) FROM chat_history WHERE rating IS NOT NULL")
            avg_rating = cursor.fetchone()[0] or 0

            cursor.execute("SELECT COUNT(*) FROM chat_history WHERE rating = 1")
            like_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM chat_history WHERE rating = 0")
            neutral_count = cursor.fetchone()[0]

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
            print(f"❌ Statistics error: {e}")
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
            print("✅ Chat history cleared")
        except Exception as e:
            print(f"❌ Clear history error: {e}")

    def get_recent_chats(self, limit: int = 5) -> list:
        """최근 대화 조회"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT id, user_message, assistant_message FROM chat_history ORDER BY id DESC LIMIT ?",
                (limit,)
            )
            return cursor.fetchall()
        except Exception as e:
            print(f"❌ Recent chats error: {e}")
            return []
