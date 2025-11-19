"""
FastAPI main application for RAG Learning Prototype.
"""
import logging
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.endpoints import chat, config, datasets, evaluate
from app.core.config import get_settings
from app.core.embeddings import get_embedding_service
from app.core.llm_client import get_llm_client
from app.core.rag_pipeline import get_rag_pipeline
from app.core.vector_store import get_vector_store
from app.models.database import get_database
from app.models.schemas import HealthResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    logger.info("Starting RAG Learning Prototype API")

    settings = get_settings()

    # Initialize services
    logger.info("Initializing services...")

    try:
        # Initialize database
        db = get_database()
        logger.info("✓ Database initialized")

        # Initialize vector store
        vector_store = get_vector_store()
        stats = vector_store.get_stats()
        logger.info(
            f"✓ Vector store initialized ({stats['total_documents']} documents)"
        )

        # Initialize embedding service
        embedding_service = get_embedding_service()
        info = embedding_service.get_info()
        logger.info(f"✓ Embedding service initialized (model: {info['model_name']})")

        # Initialize LLM client
        llm_client = get_llm_client()
        logger.info("✓ LLM client initialized")

        # Initialize RAG pipeline
        rag_pipeline = get_rag_pipeline()
        logger.info("✓ RAG pipeline initialized")

        logger.info("All services initialized successfully")

    except Exception as e:
        logger.error(f"Error during initialization: {e}", exc_info=True)
        raise

    yield

    # Shutdown
    logger.info("Shutting down RAG Learning Prototype API")


# Create FastAPI app
app = FastAPI(
    title="RAG Learning Prototype",
    description="A complete RAG system for learning and experimentation",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(datasets.router, prefix="/api", tags=["Datasets"])
app.include_router(config.router, prefix="/api", tags=["Configuration"])
app.include_router(evaluate.router, prefix="/api", tags=["Evaluation"])


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "message": "RAG Learning Prototype API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint."""
    try:
        # Check services
        services_status = {}

        # Check database
        try:
            db = get_database()
            services_status["database"] = "healthy"
        except Exception as e:
            services_status["database"] = f"unhealthy: {str(e)}"

        # Check vector store
        try:
            vector_store = get_vector_store()
            vector_store.get_stats()
            services_status["vector_store"] = "healthy"
        except Exception as e:
            services_status["vector_store"] = f"unhealthy: {str(e)}"

        # Check embedding service
        try:
            embedding_service = get_embedding_service()
            services_status["embedding_service"] = "healthy"
        except Exception as e:
            services_status["embedding_service"] = f"unhealthy: {str(e)}"

        # Check LLM client
        try:
            llm_client = get_llm_client()
            services_status["llm_client"] = "healthy"
        except Exception as e:
            services_status["llm_client"] = f"unhealthy: {str(e)}"

        # Overall status
        all_healthy = all(status == "healthy" for status in services_status.values())
        overall_status = "healthy" if all_healthy else "degraded"

        return HealthResponse(
            status=overall_status,
            timestamp=datetime.utcnow().isoformat(),
            services=services_status,
        )

    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        return HealthResponse(
            status="unhealthy",
            timestamp=datetime.utcnow().isoformat(),
            services={"error": str(e)},
        )


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info",
    )
