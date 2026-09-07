import json
from pathlib import Path
from config import STATE_FILE_PATH
from features.shared.db import ChatDatabase


class StateManager:
    def __init__(self):
        self.state_file = STATE_FILE_PATH
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

    def load_state(self) -> dict:
        """저장된 상태 로드"""
        try:
            if self.state_file.exists():
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️ State load error: {e}")

        return {'documents_loaded': False, 'index_loaded': False}

    def save_state(self, documents_loaded=None, index_loaded=None):
        """상태 저장"""
        try:
            current = self.load_state()

            if documents_loaded is not None:
                current['documents_loaded'] = documents_loaded
            if index_loaded is not None:
                current['index_loaded'] = index_loaded

            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(current, f, ensure_ascii=False, indent=2)
            print(f"✅ State saved: {current}")
        except Exception as e:
            print(f"❌ State save error: {e}")

    def load_chat_history(self):
        """채팅 히스토리 로드"""
        try:
            db = ChatDatabase()
            return db.get_chat_history()
        except Exception as e:
            print(f"⚠️ Chat history load error: {e}")
            return []
