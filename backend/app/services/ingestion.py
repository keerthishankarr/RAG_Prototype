"""
Data ingestion service for processing and indexing documents.
"""
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import docx
from pypdf import PdfReader

from app.core.embeddings import get_embedding_service
from app.core.vector_store import get_vector_store
from app.services.chunking import chunk_text

logger = logging.getLogger(__name__)


class IngestionService:
    """Service for ingesting documents into the vector store."""

    def __init__(self):
        """Initialize the ingestion service."""
        self.embedding_service = get_embedding_service()
        self.vector_store = get_vector_store()

    def ingest_file(
        self,
        file_path: str,
        dataset_name: str,
        dataset_id: Optional[str] = None,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        chunking_strategy: str = "sentences",
    ) -> Dict:
        """
        Ingest a file into the vector store.

        Args:
            file_path: Path to the file to ingest.
            dataset_name: Name of the dataset.
            dataset_id: Optional dataset ID. If not provided, auto-generated.
            chunk_size: Maximum characters per chunk.
            chunk_overlap: Number of overlapping characters.
            chunking_strategy: Strategy for chunking ("characters" or "sentences").

        Returns:
            Dictionary with ingestion statistics.
        """
        logger.info(f"Starting ingestion for file: {file_path}")

        # Generate dataset ID if not provided
        if dataset_id is None:
            dataset_id = str(uuid.uuid4())

        # Extract text from file
        text = self._extract_text(file_path)
        file_size = len(text)

        logger.info(f"Extracted {file_size} characters from {file_path}")

        # Chunk the text
        chunks = chunk_text(
            text=text,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            strategy=chunking_strategy,
        )

        if not chunks:
            logger.warning("No chunks created from file")
            return {
                "dataset_id": dataset_id,
                "dataset_name": dataset_name,
                "num_chunks": 0,
                "file_size": file_size,
                "status": "no_chunks_created",
            }

        # Extract chunk texts for embedding
        chunk_texts = [chunk["text"] for chunk in chunks]

        # Generate embeddings
        logger.info(f"Generating embeddings for {len(chunks)} chunks")
        embeddings = self.embedding_service.embed_documents(
            chunk_texts, show_progress=True
        )

        # Prepare metadata for each chunk
        created_at = datetime.utcnow().isoformat()
        file_name = Path(file_path).name

        metadatas = []
        for chunk in chunks:
            metadatas.append(
                {
                    "dataset_id": dataset_id,
                    "dataset_name": dataset_name,
                    "source_title": file_name,
                    "chunk_index": chunk["chunk_index"],
                    "char_count": chunk["char_count"],
                    "created_at": created_at,
                }
            )

        # Store in vector database
        logger.info("Storing chunks in vector database")
        self.vector_store.add_documents(
            texts=chunk_texts, embeddings=embeddings, metadatas=metadatas
        )

        logger.info(f"Successfully ingested {len(chunks)} chunks")

        return {
            "dataset_id": dataset_id,
            "dataset_name": dataset_name,
            "num_chunks": len(chunks),
            "file_size": file_size,
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap,
            "chunking_strategy": chunking_strategy,
            "created_at": created_at,
            "status": "success",
        }

    def ingest_text(
        self,
        text: str,
        dataset_name: str,
        source_title: str = "Direct Text",
        dataset_id: Optional[str] = None,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        chunking_strategy: str = "sentences",
    ) -> Dict:
        """
        Ingest raw text into the vector store.

        Args:
            text: Text content to ingest.
            dataset_name: Name of the dataset.
            source_title: Title/name for the source.
            dataset_id: Optional dataset ID.
            chunk_size: Maximum characters per chunk.
            chunk_overlap: Number of overlapping characters.
            chunking_strategy: Strategy for chunking.

        Returns:
            Dictionary with ingestion statistics.
        """
        logger.info(f"Ingesting text: {len(text)} characters")

        # Generate dataset ID if not provided
        if dataset_id is None:
            dataset_id = str(uuid.uuid4())

        # Chunk the text
        chunks = chunk_text(
            text=text,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            strategy=chunking_strategy,
        )

        if not chunks:
            return {
                "dataset_id": dataset_id,
                "dataset_name": dataset_name,
                "num_chunks": 0,
                "status": "no_chunks_created",
            }

        # Extract chunk texts for embedding
        chunk_texts = [chunk["text"] for chunk in chunks]

        # Generate embeddings
        embeddings = self.embedding_service.embed_documents(
            chunk_texts, show_progress=True
        )

        # Prepare metadata
        created_at = datetime.utcnow().isoformat()
        metadatas = []
        for chunk in chunks:
            metadatas.append(
                {
                    "dataset_id": dataset_id,
                    "dataset_name": dataset_name,
                    "source_title": source_title,
                    "chunk_index": chunk["chunk_index"],
                    "char_count": chunk["char_count"],
                    "created_at": created_at,
                }
            )

        # Store in vector database
        self.vector_store.add_documents(
            texts=chunk_texts, embeddings=embeddings, metadatas=metadatas
        )

        return {
            "dataset_id": dataset_id,
            "dataset_name": dataset_name,
            "num_chunks": len(chunks),
            "file_size": len(text),
            "created_at": created_at,
            "status": "success",
        }

    def _extract_text(self, file_path: str) -> str:
        """
        Extract text from various file formats.

        Args:
            file_path: Path to the file.

        Returns:
            Extracted text content.
        """
        file_path_obj = Path(file_path)
        extension = file_path_obj.suffix.lower()

        if extension == ".txt" or extension == ".md":
            return self._extract_from_text(file_path)
        elif extension == ".pdf":
            return self._extract_from_pdf(file_path)
        elif extension == ".docx":
            return self._extract_from_docx(file_path)
        else:
            logger.warning(f"Unsupported file type: {extension}. Treating as text.")
            return self._extract_from_text(file_path)

    def _extract_from_text(self, file_path: str) -> str:
        """Extract text from plain text file."""
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file."""
        try:
            reader = PdfReader(file_path)
            text_parts = []
            for page in reader.pages:
                text_parts.append(page.extract_text())
            return "\n\n".join(text_parts)
        except Exception as e:
            logger.error(f"Error extracting from PDF: {e}")
            raise

    def _extract_from_docx(self, file_path: str) -> str:
        """Extract text from Word document."""
        try:
            doc = docx.Document(file_path)
            text_parts = []
            for paragraph in doc.paragraphs:
                text_parts.append(paragraph.text)
            return "\n\n".join(text_parts)
        except Exception as e:
            logger.error(f"Error extracting from DOCX: {e}")
            raise


# Global ingestion service instance
_ingestion_service = None


def get_ingestion_service() -> IngestionService:
    """
    Get or create the global ingestion service instance.

    Returns:
        The singleton ingestion service instance.
    """
    global _ingestion_service
    if _ingestion_service is None:
        _ingestion_service = IngestionService()
    return _ingestion_service
