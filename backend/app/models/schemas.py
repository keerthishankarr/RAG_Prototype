"""
Pydantic schemas for API requests and responses.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# Configuration schemas
class ConfigUpdate(BaseModel):
    """Schema for updating RAG configuration."""

    default_chunk_size: Optional[int] = Field(None, ge=50, le=2000)
    default_chunk_overlap: Optional[int] = Field(None, ge=0, le=500)
    default_top_k: Optional[int] = Field(None, ge=1, le=100)
    default_temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    default_model: Optional[str] = None
    default_max_tokens: Optional[int] = Field(None, ge=50, le=4000)
    default_min_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    system_prompt: Optional[str] = None


class ConfigResponse(BaseModel):
    """Schema for configuration response."""

    default_chunk_size: int
    default_chunk_overlap: int
    default_top_k: int
    default_temperature: float
    default_model: str
    default_max_tokens: int
    default_min_score: float
    system_prompt: str


# Chat schemas
class ChatRequest(BaseModel):
    """Schema for chat request."""

    query: str = Field(..., min_length=1, max_length=2000)
    top_k: Optional[int] = Field(3, ge=1, le=100)
    enabled_datasets: Optional[List[str]] = None
    model: Optional[str] = "gpt-4o"
    temperature: Optional[float] = Field(0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(500, ge=50, le=4000)
    min_score: Optional[float] = Field(0.0, ge=0.0, le=1.0)


class ChunkInfo(BaseModel):
    """Schema for retrieved chunk information."""

    text: str
    score: float
    metadata: Dict[str, Any]


class ObservabilityStep(BaseModel):
    """Schema for a single observability step."""

    name: str
    latency_ms: int
    details: Dict[str, Any]


class ObservabilityData(BaseModel):
    """Schema for complete observability data."""

    total_latency_ms: int
    steps: List[ObservabilityStep]
    full_prompt: str


class ChatResponse(BaseModel):
    """Schema for chat response."""

    answer: str
    observability: ObservabilityData


# Dataset schemas
class DatasetInfo(BaseModel):
    """Schema for dataset information."""

    id: str
    name: str
    enabled: bool
    num_chunks: int
    file_size: int
    chunk_size: int
    chunk_overlap: int
    chunking_strategy: str
    created_at: str
    updated_at: str


class DatasetCreate(BaseModel):
    """Schema for creating a dataset."""

    name: str = Field(..., min_length=1, max_length=200)
    chunk_size: Optional[int] = Field(500, ge=50, le=2000)
    chunk_overlap: Optional[int] = Field(50, ge=0, le=500)
    chunking_strategy: Optional[str] = Field("sentences", pattern="^(characters|sentences)$")


class DatasetUpdate(BaseModel):
    """Schema for updating a dataset."""

    name: Optional[str] = Field(None, min_length=1, max_length=200)
    enabled: Optional[bool] = None


class DatasetUploadResponse(BaseModel):
    """Schema for dataset upload response."""

    dataset_id: str
    dataset_name: str
    num_chunks: int
    file_size: int
    chunk_size: int
    chunk_overlap: int
    chunking_strategy: str
    status: str
    message: str


class DatasetListResponse(BaseModel):
    """Schema for dataset list response."""

    datasets: List[DatasetInfo]
    total: int


# Evaluation schemas
class EvaluationSubmit(BaseModel):
    """Schema for submitting an evaluation."""

    query: str
    response: str
    retrieved_chunks: List[Dict[str, Any]]
    rating: Optional[int] = Field(None, ge=1, le=5)
    notes: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    observability_data: Optional[Dict[str, Any]] = None


class EvaluationInfo(BaseModel):
    """Schema for evaluation information."""

    id: int
    query: str
    response: str
    rating: Optional[int]
    notes: Optional[str]
    num_chunks: int
    response_length: int
    avg_chunk_score: float
    config: Optional[Dict[str, Any]]
    observability_data: Optional[Dict[str, Any]]
    created_at: str


class EvaluationListResponse(BaseModel):
    """Schema for evaluation list response."""

    evaluations: List[EvaluationInfo]
    total: int


class TestQuestion(BaseModel):
    """Schema for a test question."""

    question: str
    expected_keywords: List[str]
    expected_source: Optional[str] = None


class BatchEvaluationRequest(BaseModel):
    """Schema for batch evaluation request."""

    test_questions: List[TestQuestion]
    top_k: Optional[int] = Field(3, ge=1, le=100)
    model: Optional[str] = "gpt-4o"
    temperature: Optional[float] = Field(0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(500, ge=50, le=4000)


class BatchEvaluationResult(BaseModel):
    """Schema for a single batch evaluation result."""

    question: str
    answer: str
    expected_keywords: List[str]
    keywords_found: List[str]
    keyword_coverage: float
    observability: Dict[str, Any]


class BatchEvaluationResponse(BaseModel):
    """Schema for batch evaluation response."""

    total_questions: int
    avg_keyword_coverage: float
    avg_latency_ms: float
    results: List[BatchEvaluationResult]
    evaluated_at: str


# Health check schema
class HealthResponse(BaseModel):
    """Schema for health check response."""

    status: str
    timestamp: str
    services: Dict[str, str]


# Error schema
class ErrorResponse(BaseModel):
    """Schema for error response."""

    error: str
    detail: Optional[str] = None
    timestamp: str
