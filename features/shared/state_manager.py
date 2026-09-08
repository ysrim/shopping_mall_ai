# features/shared/state_manager.py
import json
from pathlib import Path
from config import STATE_FILE_PATH


class StateManager:
    """애플리케이션 상태 관리"""

    def __init__(self, state_file: Path = STATE_FILE_PATH):
        self.state_file = Path(state_file)
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

        # 파일이 없으면 초기 상태로 생성
        if not self.state_file.exists():
            self._initialize_state()

    def _initialize_state(self):
        """초기 상태 파일 생성"""
        initial_state = {
            'documents_loaded': False,
            'index_loaded': False,
            'llm_provider': 'gemini'
        }
        try:
            with open(self.state_file, 'w') as f:
                json.dump(initial_state, f, indent=2)
            print(f"✅ 초기 상태 파일 생성됨: {self.state_file}")
        except Exception as e:
            print(f"❌ 초기 상태 파일 생성 실패: {e}")

    def save_state(self, **kwargs):
        """
        상태 저장

        Args:
            **kwargs: 저장할 상태 데이터
        """
        try:
            with open(self.state_file, 'w') as f:
                json.dump(kwargs, f, indent=2)
            print(f"✅ 상태 저장됨: {kwargs}")
        except Exception as e:
            print(f"❌ 상태 저장 실패: {e}")

    def load_state(self) -> dict:
        """
        상태 로드

        Returns:
            저장된 상태 딕셔너리
        """
        try:
            if self.state_file.exists():
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                print(f"✅ 상태 로드됨: {state}")
                return state
            else:
                print("⚠️ 상태 파일이 없음 (초기 상태)")
                return {
                    'documents_loaded': False,
                    'index_loaded': False,
                    'llm_provider': 'gemini'
                }
        except Exception as e:
            print(f"❌ 상태 로드 실패: {e}")
            return {
                'documents_loaded': False,
                'index_loaded': False,
                'llm_provider': 'gemini'
            }

    def clear_state(self):
        """상태 초기화"""
        try:
            if self.state_file.exists():
                self.state_file.unlink()
            self._initialize_state()
            print("✅ 상태 초기화 완료")
        except Exception as e:
            print(f"❌ 상태 초기화 실패: {e}")
