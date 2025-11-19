"""
Configuration API endpoints.
"""
import logging

from fastapi import APIRouter, HTTPException

from app.core.config import get_settings
from app.models.schemas import ConfigResponse, ConfigUpdate

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/config", response_model=ConfigResponse)
async def get_config():
    """
    Get current RAG configuration.

    Returns:
        Current configuration settings.
    """
    try:
        settings = get_settings()

        return ConfigResponse(
            default_chunk_size=settings.default_chunk_size,
            default_chunk_overlap=settings.default_chunk_overlap,
            default_top_k=settings.default_top_k,
            default_temperature=settings.default_temperature,
            default_model=settings.default_model,
            default_max_tokens=settings.default_max_tokens,
            default_min_score=settings.default_min_score,
            system_prompt=settings.system_prompt,
        )

    except Exception as e:
        logger.error(f"Error getting config: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/config", response_model=ConfigResponse)
async def update_config(update: ConfigUpdate):
    """
    Update RAG configuration.

    Note: This updates the in-memory settings only.
    For persistent changes, update the .env file.

    Args:
        update: Configuration updates.

    Returns:
        Updated configuration.
    """
    try:
        settings = get_settings()

        # Update settings (note: this is in-memory only)
        if update.default_chunk_size is not None:
            settings.default_chunk_size = update.default_chunk_size
        if update.default_chunk_overlap is not None:
            settings.default_chunk_overlap = update.default_chunk_overlap
        if update.default_top_k is not None:
            settings.default_top_k = update.default_top_k
        if update.default_temperature is not None:
            settings.default_temperature = update.default_temperature
        if update.default_model is not None:
            settings.default_model = update.default_model
        if update.default_max_tokens is not None:
            settings.default_max_tokens = update.default_max_tokens
        if update.default_min_score is not None:
            settings.default_min_score = update.default_min_score
        if update.system_prompt is not None:
            settings.system_prompt = update.system_prompt

        logger.info("Configuration updated")

        return ConfigResponse(
            default_chunk_size=settings.default_chunk_size,
            default_chunk_overlap=settings.default_chunk_overlap,
            default_top_k=settings.default_top_k,
            default_temperature=settings.default_temperature,
            default_model=settings.default_model,
            default_max_tokens=settings.default_max_tokens,
            default_min_score=settings.default_min_score,
            system_prompt=settings.system_prompt,
        )

    except Exception as e:
        logger.error(f"Error updating config: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
