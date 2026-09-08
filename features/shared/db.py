import sqlite3
from pathlib import Path
from typing import List, Dict, Optional
from config import DB_PATH
import threading

class ChatDatabase:
    # 스레드별 연결 저장
    _thread_local = threading.local()

    def __init__(self):
        """데이터베이스 초기화"""
        self.db_path = Path(DB_PATH)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        print(f"📊 ChatDatabase 초기화: {self.db_path}")
        self._init_db()

    def _get_connection(self):
        """스레드별 데이터베이스 연결 획득"""
        if not hasattr(self._thread_local, 'connection'):
            self._thread_local.connection = sqlite3.connect(
                str(self.db_path),
                check_same_thread=False,  # 스레드 체크 비활성화
                timeout=10.0
            )
            self._thread_local.connection.row_factory = sqlite3.Row
        return self._thread_local.connection

    def _init_db(self):
        """데이터베이스 테이블 생성"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_message TEXT NOT NULL,
                assistant_message TEXT NOT NULL,
                category TEXT,
                rating INTEGER DEFAULT NULL,
                llm_provider TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        print("✅ 데이터베이스 테이블 생성 완료")

    def save_chat(self, user_message: str, assistant_message: str,
                  category: str = None, llm_provider: str = None) -> int:
        """
        대화 저장

        Args:
            user_message: 사용자 메시지
            assistant_message: 어시스턴트 응답
            category: 카테고리 (선택)
            llm_provider: LLM 프로바이더 (선택)

        Returns:
            저장된 대화의 ID
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO chats (user_message, assistant_message, category, llm_provider)
                VALUES (?, ?, ?, ?)
            ''', (user_message, assistant_message, category, llm_provider))

            conn.commit()
            chat_id = cursor.lastrowid

            print(f"✅ 채팅 저장 완료 (ID: {chat_id})")
            return chat_id

        except Exception as e:
            print(f"❌ 채팅 저장 실패: {str(e)}")
            raise

    def get_history(self, limit: int = 50) -> List[Dict]:
        """
        대화 히스토리 조회

        Args:
            limit: 조회 개수 (기본: 50)

        Returns:
            대화 리스트
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT id, user_message, assistant_message, category, rating, llm_provider, timestamp
                FROM chats
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))

            rows = cursor.fetchall()

            # Row를 dict로 변환
            chats = []
            for row in rows:
                chat = {
                    'id': row['id'],
                    'user_message': row['user_message'],
                    'assistant_message': row['assistant_message'],
                    'category': row['category'],
                    'rating': row['rating'],
                    'llm_provider': row['llm_provider'],
                    'timestamp': row['timestamp']
                }
                chats.append(chat)

            print(f"✅ 히스토리 조회 완료: {len(chats)}개")
            return chats

        except Exception as e:
            print(f"❌ 히스토리 조회 실패: {str(e)}")
            return []

    def rate_message(self, chat_id: int, rating: int) -> bool:
        """
        대화에 평가 추가

        Args:
            chat_id: 대화 ID
            rating: 평가 (1: 좋음, 0: 중간, -1: 나쁨)

        Returns:
            성공 여부
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE chats SET rating = ? WHERE id = ?
            ''', (rating, chat_id))

            conn.commit()
            print(f"✅ 평가 저장 완료 (ID: {chat_id}, 평가: {rating})")
            return True

        except Exception as e:
            print(f"❌ 평가 저장 실패: {str(e)}")
            return False

    def update_category(self, chat_id: int, category: str) -> bool:
        """
        대화 카테고리 업데이트

        Args:
            chat_id: 대화 ID
            category: 새로운 카테고리

        Returns:
            성공 여부
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE chats SET category = ? WHERE id = ?
            ''', (category, chat_id))

            conn.commit()
            print(f"✅ 카테고리 업데이트 완료 (ID: {chat_id}, 카테고리: {category})")
            return True

        except Exception as e:
            print(f"❌ 카테고리 업데이트 실패: {str(e)}")
            return False

    def delete_chat(self, chat_id: int) -> bool:
        """
        대화 삭제

        Args:
            chat_id: 대화 ID

        Returns:
            성공 여부
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute('DELETE FROM chats WHERE id = ?', (chat_id,))
            conn.commit()

            print(f"✅ 대화 삭제 완료 (ID: {chat_id})")
            return True

        except Exception as e:
            print(f"❌ 대화 삭제 실패: {str(e)}")
            return False

    def clear_history(self) -> bool:
        """
        모든 대화 삭제

        Returns:
            성공 여부
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute('DELETE FROM chats')
            conn.commit()

            print(f"✅ 모든 대화 삭제 완료")
            return True

        except Exception as e:
            print(f"❌ 대화 삭제 실패: {str(e)}")
            return False

    def get_statistics(self) -> Dict:
        """
        대화 통계 조회

        Returns:
            통계 정보
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # 총 대화 수
            cursor.execute('SELECT COUNT(*) as count FROM chats')
            total_count = cursor.fetchone()['count']

            # 평가별 통계
            cursor.execute('''
                SELECT rating, COUNT(*) as count 
                FROM chats 
                WHERE rating IS NOT NULL
                GROUP BY rating
            ''')
            rating_stats = {}
            for row in cursor.fetchall():
                rating_stats[row['rating']] = row['count']

            # 카테고리별 통계
            cursor.execute('''
                SELECT category, COUNT(*) as count
                FROM chats
                WHERE category IS NOT NULL
                GROUP BY category
            ''')
            category_stats = {}
            for row in cursor.fetchall():
                category_stats[row['category']] = row['count']

            return {
                'total_chats': total_count,
                'rating_stats': rating_stats,
                'category_stats': category_stats
            }

        except Exception as e:
            print(f"❌ 통계 조회 실패: {str(e)}")
            return {}

    def close(self):
        """데이터베이스 연결 종료"""
        if hasattr(self._thread_local, 'connection'):
            try:
                self._thread_local.connection.close()
                delattr(self._thread_local, 'connection')
                print("✅ 데이터베이스 연결 종료")
            except Exception as e:
                print(f"⚠️ 연결 종료 실패: {str(e)}")
