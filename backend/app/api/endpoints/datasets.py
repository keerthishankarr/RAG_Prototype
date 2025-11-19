"""
Dataset management API endpoints.
"""
import logging
import os
import uuid
from typing import List

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.core.vector_store import get_vector_store
from app.models.database import get_database
from app.models.schemas import (
    DatasetInfo,
    DatasetListResponse,
    DatasetUpdate,
    DatasetUploadResponse,
)
from app.services.ingestion import get_ingestion_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/datasets", response_model=DatasetListResponse)
async def list_datasets():
    """
    List all datasets.

    Returns:
        List of datasets with metadata.
    """
    try:
        db = get_database()
        datasets = db.list_datasets()

        # Convert to response format
        dataset_infos = [
            DatasetInfo(
                id=d["id"],
                name=d["name"],
                enabled=bool(d["enabled"]),
                num_chunks=d["num_chunks"],
                file_size=d["file_size"],
                chunk_size=d["chunk_size"],
                chunk_overlap=d["chunk_overlap"],
                chunking_strategy=d["chunking_strategy"],
                created_at=d["created_at"],
                updated_at=d["updated_at"],
            )
            for d in datasets
        ]

        return DatasetListResponse(datasets=dataset_infos, total=len(dataset_infos))

    except Exception as e:
        logger.error(f"Error listing datasets: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/datasets/upload", response_model=DatasetUploadResponse)
async def upload_dataset(
    file: UploadFile = File(...),
    name: str = Form(...),
    chunk_size: int = Form(500),
    chunk_overlap: int = Form(50),
    chunking_strategy: str = Form("sentences"),
):
    """
    Upload and ingest a new dataset.

    Args:
        file: File to upload.
        name: Dataset name.
        chunk_size: Chunk size in characters.
        chunk_overlap: Chunk overlap in characters.
        chunking_strategy: Chunking strategy (characters or sentences).

    Returns:
        Upload response with dataset information.
    """
    try:
        logger.info(f"Uploading dataset: {name}")

        # Save uploaded file temporarily
        upload_dir = "./data/uploads"
        os.makedirs(upload_dir, exist_ok=True)

        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Ingest the file
        ingestion_service = get_ingestion_service()
        result = ingestion_service.ingest_file(
            file_path=file_path,
            dataset_name=name,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            chunking_strategy=chunking_strategy,
        )

        # Save dataset to database
        db = get_database()
        db.create_dataset(
            {
                "dataset_id": result["dataset_id"],
                "name": result["dataset_name"],
                "num_chunks": result["num_chunks"],
                "file_size": result["file_size"],
                "chunk_size": chunk_size,
                "chunk_overlap": chunk_overlap,
                "chunking_strategy": chunking_strategy,
            }
        )

        # Clean up temporary file
        try:
            os.remove(file_path)
        except:
            pass

        logger.info(f"Dataset uploaded successfully: {result['dataset_id']}")

        return DatasetUploadResponse(
            dataset_id=result["dataset_id"],
            dataset_name=result["dataset_name"],
            num_chunks=result["num_chunks"],
            file_size=result["file_size"],
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            chunking_strategy=chunking_strategy,
            status="success",
            message=f"Successfully ingested {result['num_chunks']} chunks",
        )

    except Exception as e:
        logger.error(f"Error uploading dataset: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/datasets/{dataset_id}", response_model=DatasetInfo)
async def update_dataset(dataset_id: str, update: DatasetUpdate):
    """
    Update a dataset.

    Args:
        dataset_id: ID of the dataset to update.
        update: Update data.

    Returns:
        Updated dataset information.
    """
    try:
        db = get_database()

        # Build update dict
        updates = {}
        if update.name is not None:
            updates["name"] = update.name
        if update.enabled is not None:
            updates["enabled"] = 1 if update.enabled else 0

        # Update in database
        success = db.update_dataset(dataset_id, updates)
        if not success:
            raise HTTPException(status_code=404, detail="Dataset not found")

        # Get updated dataset
        dataset = db.get_dataset(dataset_id)
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")

        return DatasetInfo(
            id=dataset["id"],
            name=dataset["name"],
            enabled=bool(dataset["enabled"]),
            num_chunks=dataset["num_chunks"],
            file_size=dataset["file_size"],
            chunk_size=dataset["chunk_size"],
            chunk_overlap=dataset["chunk_overlap"],
            chunking_strategy=dataset["chunking_strategy"],
            created_at=dataset["created_at"],
            updated_at=dataset["updated_at"],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating dataset: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/datasets/{dataset_id}")
async def delete_dataset(dataset_id: str):
    """
    Delete a dataset.

    Args:
        dataset_id: ID of the dataset to delete.

    Returns:
        Success message.
    """
    try:
        db = get_database()
        vector_store = get_vector_store()

        # Delete from vector store
        vector_store.delete_dataset(dataset_id)

        # Delete from database
        success = db.delete_dataset(dataset_id)
        if not success:
            raise HTTPException(status_code=404, detail="Dataset not found")

        logger.info(f"Dataset deleted: {dataset_id}")
        return {"message": "Dataset deleted successfully", "dataset_id": dataset_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting dataset: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
