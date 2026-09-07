import json
from pathlib import Path
from typing import List, Dict, Any
import numpy as np
from features.shared.api import GeminiAPI
from config import FAISS_INDEX_PATH


class Retriever:
    def __init__(self, api: GeminiAPI, index_path: Path = FAISS_INDEX_PATH):
        self.api = api
        self.index_path = index_path
        self.chunks = []
        self._load_metadata()

    def _load_metadata(self):
        try:
            meta_path = self.index_path / 'metadata.json'
            if meta_path.exists():
                with open(meta_path, 'r', encoding='utf-8') as f:
                    self.chunks = json.load(f).get('chunks', [])
        except Exception as e:
            print(f"⚠️ Metadata load error: {e}")

    def retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        try:
            if not self.chunks:
                print("❌ No chunk data")
                return []

            q_emb = self.api.embed(query)
            if not q_emb:
                print("❌ Query embedding failed")
                return []

            import faiss
            idx_file = self.index_path / 'index.faiss'
            if not idx_file.exists():
                print("❌ FAISS file missing")
                return []

            index = faiss.read_index(str(idx_file))
            D, I = index.search(np.array([q_emb], dtype=np.float32), min(top_k, len(self.chunks)))

            results = []
            for dist, idx in zip(D[0], I[0]):
                if 0 <= idx < len(self.chunks):
                    results.append(
                        {'content': self.chunks[int(idx)], 'source': 'Retrieved Document', 'relevance': float(dist)})

            if results:
                print(f"✅ Retrieved {len(results)} chunks")
            return results
        except Exception as e:
            print(f"❌ Retrieval error: {e}")
            return []
