"""
Evaluation API endpoints.
"""
import logging

from fastapi import APIRouter, HTTPException

from app.core.rag_pipeline import get_rag_pipeline
from app.models.database import get_database
from app.models.schemas import (
    BatchEvaluationRequest,
    BatchEvaluationResponse,
    EvaluationInfo,
    EvaluationListResponse,
    EvaluationSubmit,
)
from app.services.evaluation import get_evaluation_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/evaluate", response_model=EvaluationInfo)
async def submit_evaluation(evaluation: EvaluationSubmit):
    """
    Submit a manual evaluation for a response.

    Args:
        evaluation: Evaluation data.

    Returns:
        Created evaluation information.
    """
    try:
        logger.info("Submitting evaluation")

        # Process evaluation
        eval_service = get_evaluation_service()
        processed = eval_service.evaluate_response(
            query=evaluation.query,
            response=evaluation.response,
            retrieved_chunks=evaluation.retrieved_chunks,
            rating=evaluation.rating,
            notes=evaluation.notes,
        )

        # Add config and observability data
        processed["config"] = evaluation.config
        processed["observability_data"] = evaluation.observability_data

        # Save to database
        db = get_database()
        eval_id = db.create_evaluation(processed)

        # Get the saved evaluation
        evaluations = db.list_evaluations(limit=1)
        if not evaluations:
            raise HTTPException(status_code=500, detail="Failed to retrieve evaluation")

        saved_eval = evaluations[0]

        return EvaluationInfo(
            id=saved_eval["id"],
            query=saved_eval["query"],
            response=saved_eval["response"],
            rating=saved_eval.get("rating"),
            notes=saved_eval.get("notes"),
            num_chunks=saved_eval.get("num_chunks", 0),
            response_length=saved_eval.get("response_length", 0),
            avg_chunk_score=saved_eval.get("avg_chunk_score", 0.0),
            config=saved_eval.get("config"),
            observability_data=saved_eval.get("observability_data"),
            created_at=saved_eval["created_at"],
        )

    except Exception as e:
        logger.error(f"Error submitting evaluation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/evaluations", response_model=EvaluationListResponse)
async def list_evaluations(limit: int = 100):
    """
    List all evaluations.

    Args:
        limit: Maximum number of evaluations to return.

    Returns:
        List of evaluations.
    """
    try:
        db = get_database()
        evaluations = db.list_evaluations(limit=limit)

        eval_infos = [
            EvaluationInfo(
                id=e["id"],
                query=e["query"],
                response=e["response"],
                rating=e.get("rating"),
                notes=e.get("notes"),
                num_chunks=e.get("num_chunks", 0),
                response_length=e.get("response_length", 0),
                avg_chunk_score=e.get("avg_chunk_score", 0.0),
                config=e.get("config"),
                observability_data=e.get("observability_data"),
                created_at=e["created_at"],
            )
            for e in evaluations
        ]

        return EvaluationListResponse(evaluations=eval_infos, total=len(eval_infos))

    except Exception as e:
        logger.error(f"Error listing evaluations: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/evaluate/batch", response_model=BatchEvaluationResponse)
async def batch_evaluate(request: BatchEvaluationRequest):
    """
    Run batch evaluation on test questions.

    Args:
        request: Batch evaluation request with test questions.

    Returns:
        Batch evaluation results.
    """
    try:
        logger.info(f"Running batch evaluation on {len(request.test_questions)} questions")

        # Get enabled datasets
        db = get_database()
        all_datasets = db.list_datasets()
        enabled_datasets = [d["id"] for d in all_datasets if d["enabled"]]

        # Prepare config
        config = {
            "top_k": request.top_k,
            "model": request.model,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
            "enabled_datasets": enabled_datasets,
        }

        # Run evaluation
        eval_service = get_evaluation_service()
        rag_pipeline = get_rag_pipeline()

        # Convert Pydantic models to dicts
        test_questions = [q.model_dump() for q in request.test_questions]

        results = eval_service.evaluate_batch(
            test_questions=test_questions, rag_pipeline=rag_pipeline, config=config
        )

        return BatchEvaluationResponse(**results)

    except Exception as e:
        logger.error(f"Error in batch evaluation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
