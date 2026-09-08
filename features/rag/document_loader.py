from pathlib import Path
from typing import List, Dict


class DocumentLoader:
    def __init__(self, path: str | Path):
        """
        문서 로더 초기화

        Args:
            path: 문서 폴더 경로
        """
        self.path = Path(path)
        print(f"📂 DocumentLoader 초기화: {self.path}")

    def load(self) -> List[Dict[str, str]]:
        """
        폴더에서 .txt 파일 로드

        Returns:
            문서 리스트: [{"filename": "...", "content": "..."}, ...]
        """
        documents = []

        # 경로 확인
        if not self.path.exists():
            print(f"❌ 경로 없음: {self.path}")
            return documents

        if not self.path.is_dir():
            print(f"❌ 폴더가 아님: {self.path}")
            return documents

        # .txt 파일 로드
        txt_files = list(self.path.glob("*.txt"))

        if not txt_files:
            print(f"⚠️ {self.path}에 .txt 파일 없음")
            return documents

        for file in txt_files:
            try:
                content = file.read_text(encoding='utf-8')
                document = {
                    "filename": file.name,
                    "content": content
                }
                documents.append(document)
                print(f"✅ Loaded: {file.name}")
            except Exception as e:
                print(f"❌ 로드 실패 {file.name}: {str(e)}")
                continue

        return documents
