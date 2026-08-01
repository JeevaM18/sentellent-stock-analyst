import logging
from typing import Any
import tiktoken

from app.constants.chunks import TOKENIZER_ENCODING
from app.rag.constants import CONTEXT_SEPARATOR, DEFAULT_PROMPT_VERSION, MAX_CONTEXT_CHARACTERS
from app.rag.prompts import get_system_prompt
from app.rag.types import ContextChunk, RAGContext
from app.retrieval.types import RetrievalSummary

logger = logging.getLogger(__name__)


class ContextBuilder:
    """Builder responsible for assembling retrieved semantic chunks into formatted LLM prompt context."""

    _encoding: Any = None

    @classmethod
    def _get_encoding(cls):
        if cls._encoding is None:
            try:
                cls._encoding = tiktoken.get_encoding(TOKENIZER_ENCODING)
            except Exception as e:
                logger.warning("Failed to initialize tiktoken encoding '%s': %s. Falling back to char estimation.", TOKENIZER_ENCODING, e)
        return cls._encoding

    @classmethod
    def estimate_tokens(cls, text: str) -> int:
        """Accurately estimate token count using tiktoken cl100k_base encoding."""
        if not text:
            return 0
        encoding = cls._get_encoding()
        if encoding:
            return len(encoding.encode(text))
        return len(text) // 4

    @staticmethod
    def estimate_context_size(context: str) -> dict[str, int]:
        """Return character, word, and estimated token counts for context text."""
        return {
            "characters": len(context),
            "words": len(context.split()),
            "tokens": ContextBuilder.estimate_tokens(context),
        }

    @staticmethod
    def build(
        *,
        query: str,
        retrieval: RetrievalSummary,
        chat_history: str = "",
        prompt_version: str = DEFAULT_PROMPT_VERSION,
        max_characters: int = MAX_CONTEXT_CHARACTERS,
    ) -> RAGContext:
        """
        Transform RetrievalSummary results and prior chat_history into a RAGContext object.
        Applies chunk deduplication, structured block formatting, and a strict character limit guard.
        """
        system_prompt = get_system_prompt(prompt_version)
        if not retrieval.results:
            return RAGContext(
                question=query,
                system_prompt=system_prompt,
                context="",
                chat_history=chat_history,
                chunks=[],
                chunk_count=0,
                total_characters=0,
                estimated_words=0,
                estimated_tokens=0,
                prompt_version=prompt_version,
            )

        seen_chunk_ids: set[Any] = set()
        seen_contents: set[str] = set()
        structured_chunks: list[ContextChunk] = []
        formatted_blocks: list[str] = []
        current_length = 0

        rank_counter = 1
        for res in retrieval.results:
            # Deduplication check
            if res.chunk_id in seen_chunk_ids or res.content.strip() in seen_contents:
                logger.debug("Skipping duplicate chunk_id %s", res.chunk_id)
                continue

            seen_chunk_ids.add(res.chunk_id)
            seen_contents.add(res.content.strip())

            published_str = res.published_at.strftime("%Y-%m-%d") if res.published_at else "N/A"
            comp_str = res.company_name or "N/A"
            ticker_str = res.ticker or "N/A"
            url_str = res.source_url or "N/A"

            block = (
                f"[Chunk {rank_counter}]\n"
                f"Company: {comp_str}\n"
                f"Ticker: {ticker_str}\n"
                f"Title: {res.source_title}\n"
                f"Published: {published_str}\n"
                f"Similarity: {res.similarity:.4f}\n"
                f"URL: {url_str}\n\n"
                f"Content:\n{res.content}"
            )

            # Character limit guard check (including separator length)
            block_len = len(block)
            sep_len = len(CONTEXT_SEPARATOR) if formatted_blocks else 0
            if current_length + sep_len + block_len > max_characters:
                logger.warning(
                    "Context character limit reached (%d + %d > %d). Stopping context assembly at rank %d.",
                    current_length,
                    block_len,
                    max_characters,
                    rank_counter,
                )
                break

            context_chunk = ContextChunk(
                rank=rank_counter,
                chunk_id=res.chunk_id,
                document_id=res.document_id,
                company_name=res.company_name,
                ticker=res.ticker,
                source_title=res.source_title,
                source_url=res.source_url,
                published_at=res.published_at,
                similarity=res.similarity,
                content=res.content,
            )

            structured_chunks.append(context_chunk)
            formatted_blocks.append(block)
            current_length += sep_len + block_len
            rank_counter += 1

        rendered_context = CONTEXT_SEPARATOR.join(formatted_blocks)
        total_chars = len(rendered_context)
        words = len(rendered_context.split()) if rendered_context else 0
        tokens = ContextBuilder.estimate_tokens(rendered_context)

        return RAGContext(
            question=query,
            system_prompt=system_prompt,
            context=rendered_context,
            chat_history=chat_history,
            chunks=structured_chunks,
            chunk_count=len(structured_chunks),
            total_characters=total_chars,
            estimated_words=words,
            estimated_tokens=tokens,
            prompt_version=prompt_version,
        )
