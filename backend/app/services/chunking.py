"""
Text chunking strategies for RAG.
"""
import logging
import re
from typing import Dict, List

logger = logging.getLogger(__name__)


def chunk_by_characters(
    text: str, chunk_size: int = 500, chunk_overlap: int = 50
) -> List[Dict]:
    """
    Split text into chunks by character count with overlap.

    Args:
        text: Input text to chunk.
        chunk_size: Maximum characters per chunk.
        chunk_overlap: Number of overlapping characters between chunks.

    Returns:
        List of dictionaries with chunk information.
    """
    if not text:
        return []

    chunks = []
    start = 0
    chunk_index = 0

    while start < len(text):
        end = start + chunk_size

        # Get the chunk text
        chunk_text = text[start:end]

        # Skip empty chunks
        if chunk_text.strip():
            chunks.append(
                {
                    "text": chunk_text,
                    "chunk_index": chunk_index,
                    "start_char": start,
                    "end_char": end,
                    "char_count": len(chunk_text),
                }
            )
            chunk_index += 1

        # Move to next chunk with overlap
        start = end - chunk_overlap

        # Prevent infinite loop
        if start >= len(text):
            break

    logger.info(
        f"Created {len(chunks)} character-based chunks "
        f"(size={chunk_size}, overlap={chunk_overlap})"
    )

    return chunks


def chunk_by_sentences(
    text: str, chunk_size: int = 500, chunk_overlap: int = 50
) -> List[Dict]:
    """
    Split text into chunks by sentences, respecting chunk size.

    This strategy attempts to keep complete sentences together while
    staying within the chunk size limit.

    Args:
        text: Input text to chunk.
        chunk_size: Target maximum characters per chunk.
        chunk_overlap: Number of overlapping characters between chunks.

    Returns:
        List of dictionaries with chunk information.
    """
    if not text:
        return []

    # Split text into sentences using regex
    # Matches sentence boundaries: period, exclamation, or question mark followed by space
    sentence_pattern = r'(?<=[.!?])\s+'
    sentences = re.split(sentence_pattern, text)

    # Remove empty sentences
    sentences = [s.strip() for s in sentences if s.strip()]

    if not sentences:
        # Fallback to character-based chunking if no sentences found
        return chunk_by_characters(text, chunk_size, chunk_overlap)

    chunks = []
    current_chunk = ""
    chunk_index = 0
    char_position = 0

    for sentence in sentences:
        # If adding this sentence exceeds chunk size and we already have content
        if current_chunk and len(current_chunk) + len(sentence) + 1 > chunk_size:
            # Save current chunk
            chunks.append(
                {
                    "text": current_chunk.strip(),
                    "chunk_index": chunk_index,
                    "start_char": char_position - len(current_chunk),
                    "end_char": char_position,
                    "char_count": len(current_chunk.strip()),
                }
            )
            chunk_index += 1

            # Handle overlap: keep last part of current chunk for overlap
            if chunk_overlap > 0 and len(current_chunk) > chunk_overlap:
                overlap_text = current_chunk[-chunk_overlap:]
                current_chunk = overlap_text + " " + sentence
            else:
                current_chunk = sentence

        else:
            # Add sentence to current chunk
            if current_chunk:
                current_chunk += " " + sentence
            else:
                current_chunk = sentence

        char_position += len(sentence) + 1  # +1 for the space

    # Add the last chunk if not empty
    if current_chunk.strip():
        chunks.append(
            {
                "text": current_chunk.strip(),
                "chunk_index": chunk_index,
                "start_char": char_position - len(current_chunk),
                "end_char": char_position,
                "char_count": len(current_chunk.strip()),
            }
        )

    logger.info(
        f"Created {len(chunks)} sentence-based chunks "
        f"(size={chunk_size}, overlap={chunk_overlap})"
    )

    return chunks


def chunk_text(
    text: str,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
    strategy: str = "sentences",
) -> List[Dict]:
    """
    Chunk text using the specified strategy.

    Args:
        text: Input text to chunk.
        chunk_size: Maximum characters per chunk.
        chunk_overlap: Number of overlapping characters between chunks.
        strategy: Chunking strategy - "characters" or "sentences".

    Returns:
        List of dictionaries with chunk information.
    """
    if strategy == "characters":
        return chunk_by_characters(text, chunk_size, chunk_overlap)
    elif strategy == "sentences":
        return chunk_by_sentences(text, chunk_size, chunk_overlap)
    else:
        logger.warning(f"Unknown chunking strategy: {strategy}. Using sentences.")
        return chunk_by_sentences(text, chunk_size, chunk_overlap)
