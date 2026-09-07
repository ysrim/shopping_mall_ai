import json
from pathlib import Path
from typing import List, Dict
import numpy as np
from config import FAISS_INDEX_PATH


class FAISSIndexBuilder:
    def __init__(self, index_path: Path = FAISS_INDEX_PATH):
        self.index_path = index_path

    def build(self, chunks: List[str], embeddings: List[List[float]], documents: List[Dict]) -> bool:
        try:
            if not chunks or not embeddings:
                print("❌ No chunks or embeddings")
                return False

            print("🔄 Creating FAISS index...")
            import faiss

            dim = len(embeddings[0])
            arr = np.array(embeddings, dtype=np.float32)
            index = faiss.IndexFlatL2(dim)
            index.add(arr)

            self.index_path.mkdir(parents=True, exist_ok=True)
            meta = {
                'chunks': chunks,
                'documents': documents,
                'dimension': dim,
                'chunk_count': len(chunks)
            }

            with open(self.index_path / 'metadata.json', 'w', encoding='utf-8') as f:
                json.dump(meta, f, ensure_ascii=False, indent=2)

            faiss.write_index(index, str(self.index_path / 'index.faiss'))
            np.save(str(self.index_path / 'embeddings.npy'), arr)

            print(f"✅ Index created successfully")
            return True
        except Exception as e:
            print(f"❌ Index build error: {e}")
            return False
