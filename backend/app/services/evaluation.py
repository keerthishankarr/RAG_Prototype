"""
Evaluation service for assessing RAG performance.
"""
import logging
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class EvaluationService:
    """Service for evaluating RAG responses."""

    def __init__(self):
        """Initialize the evaluation service."""
        logger.info("Evaluation service initialized")

    def evaluate_response(
        self,
        query: str,
        response: str,
        retrieved_chunks: List[Dict],
        rating: Optional[int] = None,
        notes: Optional[str] = None,
    ) -> Dict:
        """
        Evaluate a RAG response with manual rating.

        Args:
            query: User query.
            response: Generated response.
            retrieved_chunks: List of retrieved chunks.
            rating: Manual rating (1-5 or thumbs up/down).
            notes: Optional evaluation notes.

        Returns:
            Evaluation result dictionary.
        """
        evaluation = {
            "query": query,
            "response": response,
            "rating": rating,
            "notes": notes,
            "num_chunks": len(retrieved_chunks),
            "evaluated_at": datetime.utcnow().isoformat(),
        }

        # Calculate simple metrics
        evaluation.update(self._calculate_basic_metrics(response, retrieved_chunks))

        return evaluation

    def _calculate_basic_metrics(
        self, response: str, retrieved_chunks: List[Dict]
    ) -> Dict:
        """
        Calculate basic metrics for the response.

        Args:
            response: Generated response.
            retrieved_chunks: List of retrieved chunks.

        Returns:
            Dictionary of metrics.
        """
        metrics = {
            "response_length": len(response),
            "avg_chunk_score": 0.0,
            "min_chunk_score": 0.0,
            "max_chunk_score": 0.0,
        }

        if retrieved_chunks:
            scores = [chunk.get("score", 0.0) for chunk in retrieved_chunks]
            metrics["avg_chunk_score"] = sum(scores) / len(scores)
            metrics["min_chunk_score"] = min(scores)
            metrics["max_chunk_score"] = max(scores)

        return metrics

    def evaluate_batch(
        self, test_questions: List[Dict], rag_pipeline, config: Dict
    ) -> Dict:
        """
        Run batch evaluation on test questions.

        Args:
            test_questions: List of test questions with expected answers.
            rag_pipeline: RAG pipeline instance to use.
            config: Configuration for RAG pipeline.

        Returns:
            Dictionary with batch evaluation results.
        """
        logger.info(f"Running batch evaluation on {len(test_questions)} questions")

        results = []
        for test_q in test_questions:
            question = test_q.get("question")
            expected_keywords = test_q.get("expected_keywords", [])

            # Run RAG query
            response = rag_pipeline.query(query=question, **config)

            # Check for keyword presence
            answer = response["answer"].lower()
            keywords_found = [kw for kw in expected_keywords if kw.lower() in answer]

            # Calculate keyword coverage
            keyword_coverage = (
                len(keywords_found) / len(expected_keywords)
                if expected_keywords
                else 0.0
            )

            results.append(
                {
                    "question": question,
                    "answer": response["answer"],
                    "expected_keywords": expected_keywords,
                    "keywords_found": keywords_found,
                    "keyword_coverage": keyword_coverage,
                    "observability": response["observability"],
                }
            )

        # Calculate aggregate metrics
        avg_keyword_coverage = (
            sum(r["keyword_coverage"] for r in results) / len(results)
            if results
            else 0.0
        )
        avg_latency = (
            sum(r["observability"]["total_latency_ms"] for r in results) / len(results)
            if results
            else 0.0
        )

        return {
            "total_questions": len(test_questions),
            "avg_keyword_coverage": avg_keyword_coverage,
            "avg_latency_ms": avg_latency,
            "results": results,
            "evaluated_at": datetime.utcnow().isoformat(),
        }


# Global evaluation service instance
_evaluation_service = None


def get_evaluation_service() -> EvaluationService:
    """
    Get or create the global evaluation service instance.

    Returns:
        The singleton evaluation service instance.
    """
    global _evaluation_service
    if _evaluation_service is None:
        _evaluation_service = EvaluationService()
    return _evaluation_service
