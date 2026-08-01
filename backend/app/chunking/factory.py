from langchain_text_splitters import RecursiveCharacterTextSplitter, TextSplitter

from app.constants.chunks import DEFAULT_CHUNK_OVERLAP, DEFAULT_CHUNK_SIZE


class ChunkerFactory:
    """Factory for creating configurable text splitter instances."""

    @staticmethod
    def create(strategy: str = "recursive") -> TextSplitter:
        if strategy == "recursive":
            return RecursiveCharacterTextSplitter(
                chunk_size=DEFAULT_CHUNK_SIZE,
                chunk_overlap=DEFAULT_CHUNK_OVERLAP,
                length_function=len,
                separators=["\n\n", "\n", ". ", " ", ""],
            )
        raise ValueError(f"Unsupported chunking strategy: '{strategy}'")
