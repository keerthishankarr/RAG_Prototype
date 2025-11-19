"""
Embedding service using Sentence Transformers.
"""
import logging
import time
from typing import List

import numpy as np
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating text embeddings using Sentence Transformers."""

    def __init__(self, model_name: str = None):
        """
        Initialize the embedding service.

        Args:
            model_name: Name of the sentence transformer model to use.
        """
        settings = get_settings()
        self.model_name = model_name or settings.embedding_model

        logger.info(f"Loading embedding model: {self.model_name}")
        start_time = time.time()

        self.model = SentenceTransformer(self.model_name)

        load_time = time.time() - start_time
        logger.info(f"Model loaded in {load_time:.2f} seconds")

        # Get model metadata
        self.dimensions = self.model.get_sentence_embedding_dimension()
        self.max_seq_length = self.model.max_seq_length

        logger.info(
            f"Model info - Dimensions: {self.dimensions}, Max length: {self.max_seq_length}"
        )

    def embed_documents(self, texts: List[str], show_progress: bool = True) -> List[List[float]]:
        """
        Generate embeddings for a list of documents.

        Args:
            texts: List of text documents to embed.
            show_progress: Whether to show a progress bar.

        Returns:
            List of embedding vectors (normalized).
        """
        if not texts:
            return []

        logger.info(f"Embedding {len(texts)} documents")
        start_time = time.time()

        # Generate embeddings with batch processing
        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,  # Normalize for cosine similarity
            show_progress_bar=show_progress,
            batch_size=32,
            convert_to_numpy=True,
        )

        elapsed_time = time.time() - start_time
        logger.info(f"Embedded {len(texts)} documents in {elapsed_time:.2f} seconds")

        # Convert numpy arrays to lists
        return embeddings.tolist()

    def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding for a single query.

        Args:
            query: Query text to embed.

        Returns:
            Embedding vector (normalized).
        """
        embedding = self.model.encode(
            query,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )
        return embedding.tolist()

    def get_info(self) -> dict:
        """
        Get metadata about the embedding model.

        Returns:
            Dictionary with model information.
        """
        return {
            "model_name": self.model_name,
            "dimensions": self.dimensions,
            "max_seq_length": self.max_seq_length,
        }


# Global embedding service instance
_embedding_service = None


def get_embedding_service() -> EmbeddingService:
    """
    Get or create the global embedding service instance.

    Returns:
        The singleton embedding service instance.
    """
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
