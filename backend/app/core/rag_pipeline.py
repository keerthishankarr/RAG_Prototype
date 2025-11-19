"""
RAG pipeline orchestration with complete observability.
"""
import logging
import time
from typing import Dict, List, Optional

from app.core.config import get_settings
from app.core.embeddings import get_embedding_service
from app.core.llm_client import get_llm_client
from app.core.vector_store import get_vector_store

logger = logging.getLogger(__name__)


class RAGPipeline:
    """Orchestrates the complete RAG workflow with observability."""

    def __init__(self):
        """Initialize the RAG pipeline with required services."""
        self.embedding_service = get_embedding_service()
        self.vector_store = get_vector_store()
        self.llm_client = get_llm_client()
        logger.info("RAG pipeline initialized")

    def query(
        self,
        query: str,
        top_k: int = 3,
        enabled_datasets: Optional[List[str]] = None,
        model: str = "gpt-4o",
        temperature: float = 0.7,
        max_tokens: int = 500,
        min_score: float = 0.0,
    ) -> Dict:
        """
        Execute the complete RAG pipeline.

        Args:
            query: User query.
            top_k: Number of chunks to retrieve.
            enabled_datasets: List of dataset IDs to search. None = only enabled datasets.
            model: LLM model to use.
            temperature: LLM temperature.
            max_tokens: Maximum tokens to generate.
            min_score: Minimum similarity score for retrieval.

        Returns:
            Dictionary with response and complete observability data.
        """
        logger.info(f"Processing query: {query[:100]}...")
        pipeline_start = time.time()

        # If no datasets specified, get only enabled datasets from database
        if enabled_datasets is None:
            from app.models.database import get_database
            db = get_database()
            all_datasets = db.list_datasets()
            enabled_datasets = [d["id"] for d in all_datasets if d["enabled"]]
            logger.info(f"Auto-detected {len(enabled_datasets)} enabled dataset(s)")

        # Track all steps for observability
        steps = []

        # Step 1: Generate query embedding
        embedding_start = time.time()
        query_embedding = self.embedding_service.embed_query(query)
        embedding_latency = int((time.time() - embedding_start) * 1000)

        embedding_info = self.embedding_service.get_info()
        steps.append(
            {
                "name": "embedding",
                "latency_ms": embedding_latency,
                "details": {
                    "model": embedding_info["model_name"],
                    "dimensions": embedding_info["dimensions"],
                    "request": {
                        "query_text": query,
                    },
                    "response": {
                        "embedding_vector_preview": query_embedding[:5],  # First 5 values
                        "vector_length": len(query_embedding),
                    },
                },
            }
        )

        logger.info(f"Query embedded in {embedding_latency}ms")

        # Step 2: Retrieve relevant chunks
        retrieval_start = time.time()
        retrieved_chunks = self.vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k,
            enabled_datasets=enabled_datasets,
            min_score=min_score,
        )
        retrieval_latency = int((time.time() - retrieval_start) * 1000)

        # Format chunks for display (without metadata as per user request)
        chunks_data = [
            {
                "text": chunk["text"],
                "score": round(chunk["score"], 4),
                "metadata": chunk["metadata"],
            }
            for chunk in retrieved_chunks
        ]

        steps.append(
            {
                "name": "retrieval",
                "latency_ms": retrieval_latency,
                "details": {
                    "chunks_found": len(retrieved_chunks),
                    "chunks": chunks_data,
                    "request": {
                        "query_embedding_preview": query_embedding[:5],  # First 5 values
                        "vector_length": len(query_embedding),
                        "top_k": top_k,
                        "enabled_datasets": enabled_datasets or "all",
                        "min_score": min_score,
                    },
                    "response": {
                        "chunks_retrieved": len(retrieved_chunks),
                        "chunks_data": [
                            {
                                "text": chunk["text"],
                                "score": round(chunk["score"], 4),
                            }
                            for chunk in retrieved_chunks
                        ],
                    },
                },
            }
        )

        logger.info(f"Retrieved {len(retrieved_chunks)} chunks in {retrieval_latency}ms")

        # Step 3: Construct prompt
        settings = get_settings()
        context = self._format_context(retrieved_chunks)
        full_prompt = settings.system_prompt.format(
            retrieved_chunks=context, user_query=query
        )

        # Step 4: Generate LLM response
        llm_start = time.time()
        llm_response = self.llm_client.generate(
            prompt=full_prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        llm_latency = int((time.time() - llm_start) * 1000)

        steps.append(
            {
                "name": "llm_generation",
                "latency_ms": llm_latency,
                "details": {
                    "model": llm_response["model"],
                    "prompt_tokens": llm_response["prompt_tokens"],
                    "completion_tokens": llm_response["completion_tokens"],
                    "total_tokens": llm_response["total_tokens"],
                    "cost": llm_response["cost"],
                    "temperature": llm_response["temperature"],
                    "request": {
                        "prompt": full_prompt,
                        "model": model,
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                    },
                    "response": {
                        "generated_text": llm_response["text"],
                        "tokens_used": llm_response["total_tokens"],
                    },
                },
            }
        )

        logger.info(f"LLM generated response in {llm_latency}ms")

        # Calculate total pipeline latency
        total_latency = int((time.time() - pipeline_start) * 1000)

        # Construct final response with complete observability
        response = {
            "answer": llm_response["text"],
            "observability": {
                "total_latency_ms": total_latency,
                "steps": steps,
                "full_prompt": full_prompt,
            },
        }

        logger.info(f"RAG pipeline completed in {total_latency}ms")
        return response

    def _format_context(self, chunks: List[Dict]) -> str:
        """
        Format retrieved chunks for the prompt.

        Args:
            chunks: List of retrieved chunks with metadata.

        Returns:
            Formatted context string.
        """
        if not chunks:
            return "No relevant context found."

        formatted = []
        for i, chunk in enumerate(chunks, 1):
            source = chunk["metadata"].get("source_title", "Unknown")
            score = chunk.get("score", 0.0)
            text = chunk["text"]

            formatted.append(f"[Source {i}: {source} (relevance: {score:.2f})]\n{text}")

        return "\n\n".join(formatted)


# Global RAG pipeline instance
_rag_pipeline = None


def get_rag_pipeline() -> RAGPipeline:
    """
    Get or create the global RAG pipeline instance.

    Returns:
        The singleton RAG pipeline instance.
    """
    global _rag_pipeline
    if _rag_pipeline is None:
        _rag_pipeline = RAGPipeline()
    return _rag_pipeline
