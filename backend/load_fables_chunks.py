"""
Script to load pre-chunked fables from JSONL file into the vector database.
"""
import json
import sys
import uuid
from datetime import datetime
from pathlib import Path

# Add the backend directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.embeddings import get_embedding_service
from app.core.vector_store import get_vector_store
from app.models.database import get_database


def load_fables_chunks(jsonl_path: str):
    """Load fables chunks from JSONL file into vector database."""

    print(f"Loading chunks from {jsonl_path}")

    # Initialize services
    embedding_service = get_embedding_service()
    vector_store = get_vector_store()
    db = get_database()

    # Read all chunks
    chunks = []
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                chunks.append(json.loads(line))

    print(f"Loaded {len(chunks)} chunks from file")

    # Check if dataset already exists
    existing_datasets = db.list_datasets()
    existing = next((d for d in existing_datasets if d['name'] == "Aesop's Fables"), None)

    if existing:
        print(f"Dataset already exists with ID: {existing['id']}")
        dataset_id = existing['id']
        # Delete existing vectors
        vector_store.delete_dataset(dataset_id)
        print("Deleted existing vectors from vector store")
    else:
        dataset_id = str(uuid.uuid4())
        db.create_dataset({
            "dataset_id": dataset_id,
            "name": "Aesop's Fables",
            "num_chunks": len(chunks),
            "file_size": Path(jsonl_path).stat().st_size,
            "chunk_size": 500,  # Approximate
            "chunk_overlap": 50,  # Approximate
            "chunking_strategy": "pre-chunked",
        })
        print(f"Created dataset with ID: {dataset_id}")

    # Prepare data for embedding
    texts = [chunk['chunk'] for chunk in chunks]

    # Generate embeddings
    print("Generating embeddings...")
    embeddings = embedding_service.embed_documents(texts, show_progress=True)
    print(f"Generated {len(embeddings)} embeddings")

    # Prepare metadata
    metadatas = [
        {
            "dataset_id": dataset_id,
            "dataset_name": "Aesop's Fables",
            "source_title": chunk['title'],
            "chunk_index": idx,
            "char_count": len(chunk['chunk']),
            "created_at": datetime.utcnow().isoformat(),
        }
        for idx, chunk in enumerate(chunks)
    ]

    # Prepare IDs
    ids = [f"{dataset_id}_{idx}" for idx in range(len(chunks))]

    # Add to vector store
    print("Adding documents to vector store...")
    vector_store.add_documents(
        texts=texts,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )

    print(f"✓ Successfully loaded {len(chunks)} chunks into vector database")
    print(f"✓ Dataset ID: {dataset_id}")
    print(f"✓ Dataset name: Aesop's Fables")

    # Verify
    stats = vector_store.get_stats()
    print(f"\nVector store stats: {stats}")


if __name__ == "__main__":
    jsonl_path = "../fables_chunks.jsonl"
    load_fables_chunks(jsonl_path)
