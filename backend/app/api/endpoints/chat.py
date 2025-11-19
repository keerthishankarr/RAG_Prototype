"""
Chat API endpoint for RAG queries.
"""
import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException

from app.core.rag_pipeline import get_rag_pipeline
from app.models.database import get_database
from app.models.schemas import ChatRequest, ChatResponse, ErrorResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process a chat query using the RAG pipeline.

    Args:
        request: Chat request with query and configuration.

    Returns:
        Chat response with answer and observability data.
    """
    try:
        logger.info(f"Processing chat query: {request.query[:100]}...")

        # Get enabled datasets if specified
        enabled_datasets = request.enabled_datasets

        # If no datasets specified, get all enabled datasets from database
        if enabled_datasets is None:
            db = get_database()
            all_datasets = db.list_datasets()
            enabled_datasets = [d["id"] for d in all_datasets if d["enabled"]]

        # Execute RAG pipeline
        rag_pipeline = get_rag_pipeline()
        result = rag_pipeline.query(
            query=request.query,
            top_k=request.top_k,
            enabled_datasets=enabled_datasets,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            min_score=request.min_score,
        )

        logger.info("Chat query processed successfully")
        return result

    except Exception as e:
        logger.error(f"Error processing chat query: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
