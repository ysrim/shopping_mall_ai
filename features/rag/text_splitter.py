import re
from typing import List


class TextSplitter:
    def __init__(self, chunk_size: int = 500, overlap: int = 100):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def split(self, text: str) -> List[str]:
        if not text or len(text.strip()) < 10:
            return []

        sentences = re.split(r'(?<=[.!?。\n])\s*', text)
        sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 5]

        if not sentences:
            return [text[i:i + self.chunk_size] for i in range(0, len(text), self.chunk_size - self.overlap)]

        chunks = []
        current_chunk = ""

        for sentence in sentences:
            test_chunk = f"{current_chunk} {sentence}".strip()

            if len(test_chunk) <= self.chunk_size:
                current_chunk = test_chunk
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = sentence

        if current_chunk:
            chunks.append(current_chunk)

        chunks = [c for c in chunks if len(c.strip()) > 20]
        return chunks if chunks else [text]
