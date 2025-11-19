"""
Vector store implementation using ChromaDB.
"""
import logging
from datetime import datetime
from typing import Dict, List, Optional

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class VectorStore:
    """Wrapper for ChromaDB vector database."""

    def __init__(self, collection_name: str = "rag_learning_prototype"):
        """
        Initialize the vector store.

        Args:
            collection_name: Name of the ChromaDB collection.
        """
        settings = get_settings()
        self.collection_name = collection_name

        logger.info(f"Initializing ChromaDB at {settings.vector_db_path}")

        # Initialize persistent ChromaDB client
        self.client = chromadb.PersistentClient(
            path=settings.vector_db_path,
            settings=ChromaSettings(anonymized_telemetry=False),
        )

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},  # Use cosine similarity
        )

        logger.info(f"Collection '{self.collection_name}' initialized")

    def add_documents(
        self,
        texts: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict],
        ids: Optional[List[str]] = None,
    ) -> None:
        """
        Add documents to the vector store.

        Args:
            texts: List of document texts.
            embeddings: List of embedding vectors.
            metadatas: List of metadata dictionaries.
            ids: Optional list of document IDs. If not provided, auto-generated.
        """
        if not texts:
            logger.warning("No documents to add")
            return

        if ids is None:
            # Generate IDs based on dataset and index
            ids = [
                f"{meta.get('dataset_id', 'unknown')}_{meta.get('chunk_index', i)}"
                for i, meta in enumerate(metadatas)
            ]

        logger.info(f"Adding {len(texts)} documents to collection")

        self.collection.add(
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids,
        )

        logger.info(f"Successfully added {len(texts)} documents")

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 3,
        enabled_datasets: Optional[List[str]] = None,
        min_score: float = 0.0,
    ) -> List[Dict]:
        """
        Search for similar documents.

        Args:
            query_embedding: Query embedding vector.
            top_k: Number of results to return.
            enabled_datasets: List of dataset IDs to filter by. If None, search all. If empty list, return no results.
            min_score: Minimum similarity score threshold.

        Returns:
            List of results with text, score, and metadata.
        """
        # If enabled_datasets is an empty list, return no results
        if enabled_datasets is not None and len(enabled_datasets) == 0:
            logger.info("No enabled datasets - returning empty results")
            return []

        # Build where filter for datasets
        where_filter = None
        if enabled_datasets:
            if len(enabled_datasets) == 1:
                where_filter = {"dataset_id": enabled_datasets[0]}
            else:
                where_filter = {"dataset_id": {"$in": enabled_datasets}}

        # Query the collection
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_filter,
        )

        # Process results
        documents = []
        if results["ids"] and results["ids"][0]:
            for i in range(len(results["ids"][0])):
                # Convert ChromaDB distance to similarity score
                # ChromaDB returns L2 distance for cosine similarity
                # Similarity = 1 - (distance^2 / 2)
                distance = results["distances"][0][i]
                similarity = 1 - (distance**2 / 2)

                # Apply minimum score filter
                if similarity < min_score:
                    continue

                documents.append(
                    {
                        "text": results["documents"][0][i],
                        "score": similarity,
                        "metadata": results["metadatas"][0][i],
                        "id": results["ids"][0][i],
                    }
                )

        logger.info(f"Found {len(documents)} relevant documents (top-k={top_k})")
        return documents

    def delete_dataset(self, dataset_id: str) -> int:
        """
        Delete all documents for a specific dataset.

        Args:
            dataset_id: ID of the dataset to delete.

        Returns:
            Number of documents deleted.
        """
        logger.info(f"Deleting documents for dataset: {dataset_id}")

        # Get all document IDs for this dataset
        results = self.collection.get(where={"dataset_id": dataset_id})

        if not results["ids"]:
            logger.warning(f"No documents found for dataset: {dataset_id}")
            return 0

        # Delete the documents
        self.collection.delete(ids=results["ids"])

        count = len(results["ids"])
        logger.info(f"Deleted {count} documents for dataset: {dataset_id}")
        return count

    def get_dataset_count(self, dataset_id: str) -> int:
        """
        Get the number of documents for a specific dataset.

        Args:
            dataset_id: ID of the dataset.

        Returns:
            Number of documents.
        """
        results = self.collection.get(where={"dataset_id": dataset_id})
        return len(results["ids"])

    def get_stats(self) -> Dict:
        """
        Get statistics about the vector store.

        Returns:
            Dictionary with collection statistics.
        """
        count = self.collection.count()

        # Get unique datasets
        all_docs = self.collection.get()
        datasets = set()
        if all_docs["metadatas"]:
            datasets = {meta.get("dataset_id") for meta in all_docs["metadatas"]}

        return {
            "collection_name": self.collection_name,
            "total_documents": count,
            "unique_datasets": len(datasets),
            "dataset_ids": list(datasets),
        }

    def clear_collection(self) -> None:
        """Clear all documents from the collection."""
        logger.warning("Clearing all documents from collection")

        # Delete the collection and recreate it
        self.client.delete_collection(name=self.collection_name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )

        logger.info("Collection cleared and recreated")


# Global vector store instance
_vector_store = None


def get_vector_store() -> VectorStore:
    """
    Get or create the global vector store instance.

    Returns:
        The singleton vector store instance.
    """
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store
