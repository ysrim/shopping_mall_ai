import json
from pathlib import Path
from config import STATE_FILE_PATH


class StateManager:
    """앱 상태 관리"""

    @staticmethod
    def load_state() -> dict:
        """저장된 상태 로드"""
        try:
            if STATE_FILE_PATH.exists():
                with open(STATE_FILE_PATH, "r", encoding="utf-8") as f:
                    state = json.load(f)
                    print(f"✅ State loaded: {state}")
                    return state
        except Exception as e:
            print(f"❌ State load error: {e}")

        return {"documents_loaded": False, "index_loaded": False}

    @staticmethod
    def save_state(documents_loaded: bool, index_loaded: bool):
        """상태 저장"""
        try:
            state = {
                "documents_loaded": documents_loaded,
                "index_loaded": index_loaded
            }
            with open(STATE_FILE_PATH, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
            print(f"✅ State saved")
        except Exception as e:
            print(f"❌ State save error: {e}")

    @staticmethod
    def reset_state():
        """상태 초기화"""
        try:
            if STATE_FILE_PATH.exists():
                STATE_FILE_PATH.unlink()
            print("✅ State reset")
        except Exception as e:
            print(f"❌ State reset error: {e}")

    @staticmethod
    def load_chat_history():
        """DB에서 채팅 히스토리 로드"""
        try:
            from modules.db import ChatDatabase
            db = ChatDatabase()
            chats = db.get_chat_history(limit=100)
            print(f"✅ Chat history loaded: {len(chats)} chats")
            return chats
        except Exception as e:
            print(f"❌ Chat history load error: {e}")
            return []
