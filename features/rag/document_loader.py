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
        """문서를 로드합니다."""
        documents = []

        if not self.path.exists():
            print(f"❌ 경로 없음: {self.path}")
            return documents

        if not self.path.is_dir():
            print(f"❌ 폴더가 아님: {self.path}")
            return documents

        txt_files = list(self.path.glob("*.txt"))
        print(f"📂 찾은 .txt 파일: {len(txt_files)}개")
        for f in txt_files:
            print(f"   - {f.name} ({f.stat().st_size} bytes)")  # ← 파일 크기도 출력

        if not txt_files:
            print(f"⚠️ {self.path}에 .txt 파일 없음")
            return documents

        for file in txt_files:
            try:
                print(f"📖 로드 시도: {file.name}")  # ← 각 파일 로드 시도 로그
                content = file.read_text(encoding='utf-8')
                documents.append({"filename": file.name, "content": content})
                print(f"✅ Loaded: {file.name} ({len(content)}자)")
            except UnicodeDecodeError:
                try:
                    print(f"⚠️ UTF-8 실패, EUC-KR 시도: {file.name}")
                    content = file.read_text(encoding='euc-kr')
                    documents.append({"filename": file.name, "content": content})
                    print(f"✅ Loaded (EUC-KR): {file.name} ({len(content)}자)")
                except Exception as e:
                    print(f"❌ 로드 실패 {file.name}: {e}")
            except Exception as e:
                print(f"❌ 로드 실패 {file.name}: {e}")

        print(f"\n✅ 총 {len(documents)}개 문서 로드 완료\n")
        return documents
