from pathlib import Path


class DocumentLoader:
    def __init__(self, documents_dir: str):
        self.documents_dir = Path(documents_dir)
        self.documents = []

    def load(self) -> bool:
        try:
            if not self.documents_dir.exists():
                print(f"❌ No folder: {self.documents_dir}")
                return False

            txts = list(self.documents_dir.glob('*.txt'))
            if not txts:
                print(f"❌ No .txt files")
                return False

            self.documents = []
            for p in txts:
                try:
                    with open(p, 'r', encoding='utf-8') as f:
                        content = f.read()
                    if content.strip():
                        self.documents.append({'title': p.stem, 'content': content})
                        print(f"✅ Loaded: {p.name}")
                except Exception as e:
                    print(f"⚠️ Read error ({p.name}): {e}")

            print(f"✅ {len(self.documents)} documents loaded")
            return True
        except Exception as e:
            print(f"❌ Document load error: {e}")
            return False
