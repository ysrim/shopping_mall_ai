from typing import List, Dict
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import CHUNK_SIZE, CHUNK_OVERLAP


class TextSplitter:
    def __init__(self, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP):
        """
        텍스트 분할기 초기화

        Args:
            chunk_size: 청크 크기 (기본: 500)
            chunk_overlap: 청크 겹침 (기본: 50)
        """
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", "。", "，", ""]
        )
        print(f"✂️ TextSplitter 초기화 (chunk_size={chunk_size}, overlap={chunk_overlap})")

    def split(self, documents: List[Dict[str, str]]) -> List[str]:
        """
        문서 리스트를 청크로 분할

        Args:
            documents: 문서 리스트 [{"filename": "...", "content": "..."}, ...]

        Returns:
            청크 문자열 리스트
        """
        chunks = []

        # documents가 리스트가 아니면 에러
        if not isinstance(documents, list):
            print(f"❌ documents는 리스트여야 합니다. 받은 타입: {type(documents)}")
            return chunks

        # 각 문서를 청킹
        for doc in documents:
            # 문서가 dict 형식 확인
            if isinstance(doc, dict):
                content = doc.get("content", "")
                filename = doc.get("filename", "unknown")
            else:
                # dict가 아니면 문자열로 취급
                content = str(doc)
                filename = "unknown"

            # 내용이 없으면 스킵
            if not content or len(content.strip()) < 10:
                print(f"⚠️ {filename}: 내용이 너무 짧아서 스킵됨")
                continue

            print(f"📄 청킹 중: {filename} ({len(content)}자)")

            try:
                # LangChain의 split_text 사용
                doc_chunks = self.splitter.split_text(content)
                chunks.extend(doc_chunks)
                print(f"   ✅ {len(doc_chunks)}개 청크 생성")
            except Exception as e:
                print(f"   ❌ 청킹 실패: {str(e)}")
                continue

        print(f"\n✅ 총 {len(chunks)}개 청크 생성 완료")
        return chunks
