from pathlib import Path
import numpy as np
from config import SAMPLE_DATA_PATH, FAISS_INDEX_PATH, EMBEDDING_DIM, FAISS_AVAILABLE
from modules.api import GeminiAPI

try:
    import faiss
except ImportError:
    pass


class RAGPipeline:
    """RAG 파이프라인"""

    def __init__(self):
        """초기화"""
        self.api = GeminiAPI()
        self.documents = []
        self.embeddings = None
        self.index = None
        self.index_loaded = False

        # 프로그램 시작 시 저장된 인덱스 로드 시도
        self._auto_load_index()

    def _auto_load_index(self):
        """프로그램 시작 시 저장된 인덱스 자동 로드"""
        if FAISS_INDEX_PATH.exists():
            try:
                self.index = faiss.read_index(str(FAISS_INDEX_PATH))
                self.index_loaded = True
                print(f"✅ 저장된 FAISS 인덱스 자동 로드됨: {FAISS_INDEX_PATH}")
            except Exception as e:
                print(f"⚠️ 인덱스 자동 로드 실패: {e}")

    def load_documents(self, doc_dir: Path = None) -> int:
        """문서 로드"""
        doc_dir = Path(doc_dir or SAMPLE_DATA_PATH)
        self.documents = []

        print(f"📂 문서 폴더: {doc_dir}")

        if not doc_dir.exists():
            print(f"❌ 폴더가 없습니다: {doc_dir}")
            return 0

        txt_files = list(doc_dir.glob("*.txt"))
        print(f"📄 발견된 .txt 파일: {len(txt_files)}개")

        for doc_file in txt_files:
            try:
                with open(doc_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        self.documents.append({
                            "title": doc_file.stem,
                            "content": content,
                            "source": str(doc_file)
                        })
                        print(f"✅ 로드됨: {doc_file.stem}")
            except Exception as e:
                print(f"❌ 로드 실패 {doc_file}: {e}")

        print(f"📚 총 로드된 문서: {len(self.documents)}개")
        return len(self.documents)

    def build_index(self) -> bool:
        """FAISS 인덱스 생성"""
        print("\n🔍 인덱싱 시작...")

        if not self.documents:
            print("❌ 로드된 문서가 없습니다")
            return False

        if not FAISS_AVAILABLE:
            print("❌ FAISS가 설치되지 않았습니다")
            return False

        try:
            print("🔄 임베딩 생성 중...")
            texts = [doc["content"] for doc in self.documents]
            self.embeddings = self.api.embed_batch(texts)

            print(f"✅ 임베딩 생성 완료: {len(self.embeddings)}개, 차원: {len(self.embeddings[0])}")

            embeddings_array = np.array(self.embeddings, dtype=np.float32)
            embedding_dim = embeddings_array.shape[1]

            if embedding_dim != EMBEDDING_DIM:
                print(f"⚠️ 차원 불일치! {embedding_dim} != {EMBEDDING_DIM}, 자동 조정 중...")
                if embedding_dim < EMBEDDING_DIM:
                    padding = np.zeros((embeddings_array.shape[0], EMBEDDING_DIM - embedding_dim), dtype=np.float32)
                    embeddings_array = np.hstack([embeddings_array, padding])
                else:
                    embeddings_array = embeddings_array[:, :EMBEDDING_DIM]

            self.index = faiss.IndexFlatL2(EMBEDDING_DIM)
            self.index.add(embeddings_array)

            FAISS_INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
            faiss.write_index(self.index, str(FAISS_INDEX_PATH))

            self.index_loaded = True
            print(f"✅ 인덱싱 성공! 저장 위치: {FAISS_INDEX_PATH}")
            return True

        except Exception as e:
            print(f"❌ 인덱싱 오류: {e}")
            import traceback
            traceback.print_exc()
            return False

    def search(self, query: str, top_k: int = 5) -> list:
        """쿼리로 검색"""
        if not self.index_loaded:
            print("❌ 인덱스가 로드되지 않았습니다")
            return []

        try:
            query_embedding = np.array([self.api.embed(query)], dtype=np.float32)
            distances, indices = self.index.search(query_embedding, top_k)

            results = []
            for idx, distance in zip(indices[0], distances[0]):
                if idx < len(self.documents):
                    doc = self.documents[idx]
                    results.append({
                        "title": doc["title"],
                        "content": doc["content"][:500],
                        "similarity": 1 / (1 + distance)
                    })
            return results
        except Exception as e:
            print(f"❌ 검색 오류: {e}")
            return []

    def generate_prompt(self, query: str, search_results: list) -> str:
        """프롬프트 생성"""
        references = "\n\n".join([
            f"[{r['title']}]\n{r['content']}"
            for r in search_results
        ])

        return f"""당신은 전문적인 고객 상담원입니다.

[참고 자료]
{references}

[질문]
{query}

위의 참고 자료를 기반으로 정확하고 친절하게 답변하세요."""

    def generate_response(self, prompt: str, temperature: float = 0.3, max_tokens: int = 2000) -> str:
        """응답 생성"""
        return self.api.generate(prompt, temperature, max_tokens)

    def generate_response_streaming(self, prompt: str, temperature: float = 0.3, max_tokens: int = 2000):
        """스트리밍 응답"""
        for text in self.api.generate_streaming(prompt, temperature, max_tokens):
            yield text

    def clear_cache(self):
        """임베딩 캐시 초기화"""
        try:
            self.api.embedding_cache.clear()  # ← 이제 정상 작동
            print("✅ 임베딩 캐시가 초기화되었습니다")
        except Exception as e:
            print(f"❌ 캐시 초기화 오류: {e}")

    def get_usage_stats(self) -> dict:
        """사용 통계"""
        stats = self.api.get_usage_stats()
        stats.update({
            "documents_loaded": len(self.documents),
            "index_loaded": self.index_loaded
        })
        return stats
