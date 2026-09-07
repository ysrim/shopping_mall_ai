from typing import List
from features.shared.api import GeminiAPI
from config import EMBEDDING_DIM


class EmbeddingGenerator:
    def __init__(self, api: GeminiAPI):
        self.api = api

    def generate(self, texts: List[str]) -> List[List[float]]:
        print("🔄 Generating embeddings...")
        embeddings = self.api.embed_batch(texts)

        if not embeddings:
            print("❌ Embedding failed")
            return []

        dim = len(embeddings[0])
        print(f"✅ Embeddings: {len(embeddings)}, Dim: {dim}")

        if dim != EMBEDDING_DIM:
            print(f"⚠️ Dimension mismatch: config {EMBEDDING_DIM}, got {dim}")

        return embeddings
