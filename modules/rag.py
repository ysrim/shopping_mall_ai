import json
import re
from pathlib import Path
from typing import List, Dict, Any
import numpy as np
from modules.api import GeminiAPI
from config import FAISS_INDEX_PATH, EMBEDDING_DIM


class RAGPipeline:
    def __init__(self):
        self.api = GeminiAPI()
        self.vectorstore = None
        self.documents = []  # ✅ 추가
        self.embeddings_data = []
        self.index_path = FAISS_INDEX_PATH
        self.chunks = []
        self._auto_load_index()

    def _auto_load_index(self):
        """Load existing FAISS index metadata if present."""
        try:
            meta = self.index_path / "metadata.json"
            if meta.exists():
                with open(meta, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.chunks = data.get('chunks', [])
                    self.documents = data.get('documents', [])  # ✅ 추가
                print(f"✅ Index loaded")
        except Exception as e:
            print(f"⚠️ FAISS load failed: {e}")

    def _split_text(self, text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
        """고급 텍스트 청크 분할 (문장 + 문자 길이 기반)."""
        if not text or len(text.strip()) < 10:
            return []

        # 문장 분리 (한글 마침표 포함)
        sentences = re.split(r'(?<=[.!?。\n])\s*', text)
        sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 5]

        if not sentences:
            # 문장 분리 실패시 고정 길이로 분할
            return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size - overlap)]

        chunks = []
        current_chunk = ""

        for sentence in sentences:
            test_chunk = f"{current_chunk} {sentence}".strip()

            if len(test_chunk) <= chunk_size:
                current_chunk = test_chunk
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = sentence

        if current_chunk:
            chunks.append(current_chunk)

        # 최소 길이 필터링
        chunks = [c for c in chunks if len(c.strip()) > 20]
        return chunks if chunks else [text]

    def load_documents(self, documents_dir: str) -> bool:
        """Load all .txt files from a folder."""
        try:
            path = Path(documents_dir)
            if not path.exists():
                print(f"❌ No folder: {documents_dir}")
                return False
            txts = list(path.glob('*.txt'))
            if not txts:
                print(f"❌ No .txt files in {documents_dir}")
                return False
            self.documents = []
            for p in txts:
                try:
                    with open(p, 'r', encoding='utf-8') as f:
                        cnt = f.read()
                    if cnt.strip():
                        self.documents.append({'title': p.stem, 'content': cnt})
                        print(f"✅ Loaded: {p.name}")
                except Exception as e:
                    print(f"⚠️ Read error ({p.name}): {e}")
            print(f"✅ {len(self.documents)} documents loaded")
            return True
        except Exception as e:
            print(f"❌ Document load error: {e}")
            return False

    def build_index(self) -> bool:
        """Create chunks, embed them via GeminiAPI, and store a FAISS index."""
        try:
            if not self.documents:
                print("❌ No documents loaded")
                return False

            # 문서 결합
            combined = '\n\n'.join(d['content'] for d in self.documents)
            self.chunks = self._split_text(combined)
            print(f"✅ Chunks: {len(self.chunks)}")

            if not self.chunks:
                print("❌ No chunks created")
                return False

            # 임베딩 생성
            print("🔄 Generating embeddings...")
            embeddings = self.api.embed_batch(self.chunks)

            if not embeddings:
                print("❌ Embedding failed")
                return False

            dim = len(embeddings[0])
            print(f"✅ Embeddings: {len(embeddings)}, Dim: {dim}")

            if dim != EMBEDDING_DIM:
                print(f"⚠️ Dimension mismatch: config {EMBEDDING_DIM}, got {dim}")

            # FAISS 인덱스 생성
            print("🔄 Creating FAISS index...")
            import faiss
            arr = np.array(embeddings, dtype=np.float32)
            index = faiss.IndexFlatL2(dim)
            index.add(arr)

            # 저장
            self.index_path.mkdir(parents=True, exist_ok=True)
            meta = {
                'chunks': self.chunks,
                'documents': self.documents,
                'dimension': dim,
                'chunk_count': len(self.chunks)
            }

            with open(self.index_path / 'metadata.json', 'w', encoding='utf-8') as f:
                json.dump(meta, f, ensure_ascii=False, indent=2)

            faiss.write_index(index, str(self.index_path / 'index.faiss'))
            np.save(str(self.index_path / 'embeddings.npy'), arr)

            self.vectorstore = index
            self.embeddings_data = embeddings

            print(f"✅ Index created successfully")
            return True
        except Exception as e:
            print(f"❌ Indexing error: {e}")
            import traceback
            traceback.print_exc()
            return False

    def retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Search the FAISS index for the most similar chunks."""
        try:
            if not self.chunks:
                meta_path = self.index_path / 'metadata.json'
                if meta_path.exists():
                    with open(meta_path, 'r', encoding='utf-8') as f:
                        self.chunks = json.load(f).get('chunks', [])
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

    def clear_cache(self):
        """Clear embedding cache"""
        try:
            self.api.embedding_cache.clear()
            print("✅ Cache cleared")
        except Exception as e:
            print(f"❌ Cache clear error: {e}")

    def reset_index(self):
        """Reset FAISS index"""
        try:
            if self.index_path.exists():
                import shutil
                shutil.rmtree(self.index_path)
                print("✅ Index reset")
            self.vectorstore = None
            self.documents = []
            self.chunks = []
        except Exception as e:
            print(f"❌ Reset error: {e}")
