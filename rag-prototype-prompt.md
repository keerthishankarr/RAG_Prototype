# RAG Learning Prototype - Build Instructions for Claude Code

## Project Overview
Build a complete RAG (Retrieval-Augmented Generation) learning prototype using Aesop's Fables. This is an educational tool to understand how RAG systems work, with full observability into every step of the pipeline.

**Key Goal:** Learn how RAG works through hands-on experimentation with configurable settings and detailed observability.

## Technology Stack

### Backend
- **Framework:** FastAPI (Python 3.10+)
- **Vector Database:** ChromaDB (embedded, no separate server needed)
- **Embeddings:** Sentence Transformers (`all-MiniLM-L6-v2`) - completely free and local
- **LLM:** Anthropic Claude or OpenAI (API-based)
- **Database:** SQLite for application data
- **Server:** Uvicorn

### Frontend
- **Framework:** React 18+ with Vite
- **Styling:** Tailwind CSS
- **State Management:** React Context API or Zustand
- **HTTP Client:** Axios

## Project Structure

```
rag-learning-prototype/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   ├── embeddings.py
│   │   │   ├── vector_store.py
│   │   │   ├── llm_client.py
│   │   │   └── rag_pipeline.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── chunking.py
│   │   │   ├── ingestion.py
│   │   │   └── evaluation.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── endpoints/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── chat.py
│   │   │   │   ├── datasets.py
│   │   │   │   ├── config.py
│   │   │   │   └── evaluate.py
│   │   │   └── routes.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── schemas.py
│   │   │   └── database.py
│   │   └── main.py
│   ├── data/
│   │   ├── aesops_fables.txt
│   │   └── test_questions.json
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ConfigPanel.jsx
│   │   │   ├── ChatInterface.jsx
│   │   │   ├── ObservabilityDashboard.jsx
│   │   │   ├── DatasetManager.jsx
│   │   │   └── EvaluationPanel.jsx
│   │   ├── hooks/
│   │   │   ├── useChat.js
│   │   │   ├── useConfig.js
│   │   │   └── useDatasets.js
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── index.html
└── README.md
```

## Phase 1: Backend Foundation

### 1.1 Setup Backend Structure
Create the project structure and install dependencies.

**requirements.txt:**
```
fastapi==0.104.0
uvicorn==0.24.0
pydantic==2.4.0
pydantic-settings==2.0.3
python-dotenv==1.0.0
python-multipart==0.0.6
chromadb==0.4.22
sentence-transformers==2.3.1
torch==2.1.0
transformers==4.36.0
anthropic==0.7.0
openai==1.12.0
pypdf==3.17.0
python-docx==1.1.0
tiktoken==0.5.1
pandas==2.1.0
numpy==1.24.0
aiosqlite==0.19.0
tqdm==4.66.0
```

**.env.example:**
```
# LLM API Keys
ANTHROPIC_API_KEY=your-key-here
OPENAI_API_KEY=your-key-here

# Embedding Configuration
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Vector Database
VECTOR_DB_PATH=./data/chromadb

# Application Database
DATABASE_URL=sqlite:///./data/app.db

# Default RAG Settings
DEFAULT_CHUNK_SIZE=500
DEFAULT_CHUNK_OVERLAP=50
DEFAULT_TOP_K=3
DEFAULT_TEMPERATURE=0.7
DEFAULT_MODEL=claude-sonnet-4-5
DEFAULT_MAX_TOKENS=500

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=true
CORS_ORIGINS=http://localhost:5173

# Directories
DATA_DIR=./data
UPLOAD_DIR=./data/uploads
```

### 1.2 Core Configuration (backend/app/core/config.py)
Create settings management using Pydantic BaseSettings. Load from .env file and provide defaults.

**Key requirements:**
- Use pydantic-settings for type-safe configuration
- Create necessary directories on initialization
- Parse CORS_ORIGINS as a list
- Provide sensible defaults for all RAG parameters

### 1.3 Embedding Service (backend/app/core/embeddings.py)
Implement the embedding service using Sentence Transformers.

**Key features:**
- Load `all-MiniLM-L6-v2` model on initialization
- `embed_documents(texts: List[str])` - batch embedding with progress bar
- `embed_query(query: str)` - single query embedding
- Normalize embeddings for cosine similarity
- `get_info()` - return model metadata (dimensions, max length, etc.)
- Implement as singleton pattern with `get_embedding_service()` function
- Log model loading time and dimensions

**Important:** Use `normalize_embeddings=True` for proper similarity calculation.

### 1.4 Vector Store (backend/app/core/vector_store.py)
Implement ChromaDB vector store wrapper.

**Key features:**
- Use `PersistentClient` for data persistence
- Collection name: "rag_learning_prototype"
- `add_documents()` - add with embeddings and metadata
- `search()` - query with filters for enabled datasets
- Convert ChromaDB L2 distance to similarity score: `similarity = 1 - (distance^2 / 2)`
- `delete_dataset()` - remove all docs for a dataset
- `get_dataset_count()` - count docs per dataset
- `get_stats()` - collection statistics
- Filter by `enabled_datasets` list in search
- Implement as singleton with `get_vector_store()` function

**Metadata structure for each document:**
```python
{
    "dataset_id": str,
    "dataset_name": str,
    "source_title": str,
    "chunk_index": int,
    "char_count": int,
    "created_at": str
}
```

### 1.5 Chunking Service (backend/app/services/chunking.py)
Implement text chunking strategies.

**Required methods:**
- `chunk_by_characters(text, chunk_size, chunk_overlap)` - simple character-based chunking
- `chunk_by_sentences(text, chunk_size, chunk_overlap)` - sentence-aware chunking
- Return list of dictionaries with: text, chunk_index, start_char, end_char, char_count

**Sentence chunking:** Use regex to split on sentence boundaries: `r'(?<=[.!?])\s+'`

### 1.6 LLM Client (backend/app/core/llm_client.py)
Create abstraction for LLM APIs (Anthropic Claude and OpenAI).

**Key features:**
- Support both Anthropic and OpenAI APIs
- `generate(prompt, model, temperature, max_tokens)` method
- Track token usage and estimate cost
- Return response with metadata: text, prompt_tokens, completion_tokens, latency_ms, cost
- Support streaming (optional for Phase 1)

**Token cost estimates (approximate):**
- Claude Sonnet: $3 per 1M input tokens, $15 per 1M output tokens
- GPT-4: Similar pricing
- GPT-3.5-turbo: ~10x cheaper

### 1.7 RAG Pipeline (backend/app/core/rag_pipeline.py)
Orchestrate the complete RAG workflow with observability.

**Pipeline steps:**
1. Generate query embedding (track time)
2. Search vector database (track time, return chunks with scores)
3. Construct prompt with retrieved context
4. Call LLM (track tokens, time, cost)
5. Return response with full observability data

**Observability structure:**
```python
{
    "total_latency_ms": int,
    "steps": [
        {
            "name": "embedding",
            "latency_ms": int,
            "details": {"model": str, "dimensions": int}
        },
        {
            "name": "retrieval",
            "latency_ms": int,
            "details": {
                "chunks_found": int,
                "chunks": [
                    {
                        "text": str,
                        "score": float,
                        "metadata": dict
                    }
                ]
            }
        },
        {
            "name": "llm_generation",
            "latency_ms": int,
            "details": {
                "model": str,
                "prompt_tokens": int,
                "completion_tokens": int,
                "total_tokens": int,
                "cost": float,
                "temperature": float
            }
        }
    ],
    "full_prompt": str
}
```

**Prompt template:**
```
You are a helpful assistant that answers questions based on Aesop's Fables.

Use the following context to answer the question. If the answer cannot be found in the context, say so.

Context:
{retrieved_chunks}

Question: {user_query}

Answer:
```

### 1.8 Data Ingestion Service (backend/app/services/ingestion.py)
Handle dataset upload and processing.

**Key features:**
- Load text files (txt, md)
- Parse PDFs (using pypdf)
- Parse Word documents (using python-docx)
- Chunk text using chunking service
- Generate embeddings in batches
- Store in vector database with metadata
- Return ingestion statistics

**Process:**
1. Read file and extract text
2. Chunk text based on settings
3. Generate embeddings for all chunks
4. Store in ChromaDB with metadata
5. Update SQLite database with dataset info

## Phase 2: Backend API Endpoints

### 2.1 Data Models (backend/app/models/schemas.py)
Define Pydantic models for API requests/responses.

**Key schemas:**
- `ChatRequest` - query, config (top_k, temperature, model, etc.)
- `ChatResponse` - response, observability data
- `DatasetInfo` - id, name, enabled, chunks count, size, created_at
- `DatasetUploadRequest` - file, name, chunk_size, chunk_overlap
- `ConfigUpdate` - various RAG settings
- `EvaluationRequest` - query, response, rating, notes

### 2.2 Database Models (backend/app/models/database.py)
Create SQLite database schema using raw SQL or SQLAlchemy.

**Tables:**
- `datasets` - id, name, enabled, chunk_size, chunk_overlap, num_chunks, size_bytes, created_at, updated_at
- `evaluations` - id, query, response, rating, notes, config (JSON), observability_data (JSON), created_at
- `test_questions` - id, question, expected_answer, expected_sources (JSON), test_suite_id

### 2.3 Chat Endpoint (backend/app/api/endpoints/chat.py)
**POST /api/chat**

**Functionality:**
- Accept query and config
- Execute RAG pipeline
- Return response with full observability data
- Handle errors gracefully

**Response includes:**
- Generated answer
- Complete observability data (embeddings, retrieval, LLM details)
- Retrieved chunks with scores and sources

### 2.4 Dataset Endpoints (backend/app/api/endpoints/datasets.py)
**Endpoints:**
- `GET /api/datasets` - list all datasets with stats
- `POST /api/datasets/upload` - upload and ingest new dataset
- `PATCH /api/datasets/{id}` - update dataset (enable/disable)
- `DELETE /api/datasets/{id}` - delete dataset and vectors
- `POST /api/datasets/rechunk` - re-chunk existing dataset with new settings

### 2.5 Config Endpoint (backend/app/api/endpoints/config.py)
**Endpoints:**
- `GET /api/config` - get current configuration
- `PATCH /api/config` - update RAG settings

### 2.6 Evaluation Endpoints (backend/app/api/endpoints/evaluate.py)
**Endpoints:**
- `POST /api/evaluate` - submit manual evaluation (thumbs up/down, notes)
- `GET /api/evaluations` - list all evaluations
- `POST /api/evaluate/batch` - run test suite (optional for Phase 1)

### 2.7 Main App (backend/app/main.py)
**Setup:**
- Initialize FastAPI app
- Configure CORS for frontend
- Include all routers
- Add startup event to initialize services
- Add health check endpoint
- Enable debug logging if DEBUG=true

**Startup sequence:**
1. Load configuration
2. Initialize embedding service (download model if needed)
3. Initialize vector store
4. Initialize LLM client
5. Create database tables if not exist

## Phase 3: Initial Data Loading

### 3.1 Aesop's Fables Dataset (backend/data/aesops_fables.txt)
Download or create a text file with Aesop's Fables. Format:

```
THE TORTOISE AND THE HARE

A Hare was making fun of the Tortoise one day for being so slow...

Moral: Slow and steady wins the race.

---

THE FOX AND THE GRAPES

A Fox one day spied a beautiful bunch of ripe grapes...

Moral: It is easy to despise what you cannot get.

---
```

### 3.2 Test Questions (backend/data/test_questions.json)
Create sample questions for testing:

```json
[
  {
    "question": "What lesson does the tortoise teach us?",
    "expected_keywords": ["perseverance", "steady", "patience"],
    "expected_source": "The Tortoise and the Hare"
  },
  {
    "question": "Which fables involve foxes?",
    "expected_keywords": ["fox", "grapes", "crow"],
    "expected_sources": ["The Fox and the Grapes", "The Fox and the Crow"]
  },
  {
    "question": "Tell me about the boy who cried wolf",
    "expected_keywords": ["wolf", "lie", "trust"],
    "expected_source": "The Boy Who Cried Wolf"
  }
]
```

### 3.3 Initial Load Script
Create a script or endpoint to load Aesop's Fables on first run:
- Parse the fables file
- Chunk each fable
- Generate embeddings
- Store in ChromaDB
- Save dataset info to SQLite

## Phase 4: Frontend Development

### 4.1 Setup Frontend (frontend/)
**Initialize with Vite:**
```bash
npm create vite@latest frontend -- --template react
cd frontend
npm install
npm install axios tailwindcss postcss autoprefixer
npm install lucide-react # for icons
npx tailwindcss init -p
```

### 4.2 API Service (frontend/src/services/api.js)
Create axios instance and API functions:
- `chat(query, config)` - POST /api/chat
- `getDatasets()` - GET /api/datasets
- `uploadDataset(file, name, chunkSize, chunkOverlap)` - POST /api/datasets/upload
- `updateDataset(id, updates)` - PATCH /api/datasets/{id}
- `deleteDataset(id)` - DELETE /api/datasets/{id}
- `getConfig()` - GET /api/config
- `updateConfig(config)` - PATCH /api/config
- `submitEvaluation(evaluation)` - POST /api/evaluate

### 4.3 Layout (frontend/src/App.jsx)
Create three-panel layout:
- Left panel (30%): Configuration Panel
- Center panel (40%): Chat Interface
- Right panel (30%): Observability Dashboard

**Responsive behavior:** Make panels collapsible on smaller screens.

### 4.4 Configuration Panel (frontend/src/components/ConfigPanel.jsx)
**Sections:**

1. **Dataset Management**
   - List all datasets with toggle switches
   - Show: name, chunk count, size, status (active/inactive)
   - "Add Dataset" button → file upload modal
   - Delete button per dataset

2. **Chunking Settings**
   - Chunk size (number input)
   - Chunk overlap (number input)
   - "Re-chunk & Re-index" button

3. **Retrieval Settings**
   - Top-K chunks (number input, 1-10)
   - Similarity threshold (slider, 0.0-1.0)

4. **LLM Settings**
   - Model selection (dropdown: claude-sonnet-4-5, gpt-4o, gpt-3.5-turbo)
   - Temperature (slider, 0.0-1.0)
   - Max tokens (number input)

**State management:** Use React Context or local state with props.

### 4.5 Chat Interface (frontend/src/components/ChatInterface.jsx)
**Components:**

1. **Sample Questions Bar** (top)
   - Display 3-5 sample questions as clickable chips
   - Click → populate input field

2. **Message List** (center, scrollable)
   - User messages (right-aligned, blue)
   - Bot messages (left-aligned, white)
   - Show avatar icons
   - Auto-scroll to bottom on new message

3. **Evaluation Actions** (below each bot message)
   - Thumbs up button
   - Thumbs down button
   - "Add Note" button → text input modal

4. **Input Area** (bottom)
   - Textarea for query
   - Send button
   - "Clear conversation" button

**Features:**
- Loading state while waiting for response
- Error handling with user-friendly messages
- Keyboard shortcut: Enter to send (Shift+Enter for new line)

### 4.6 Observability Dashboard (frontend/src/components/ObservabilityDashboard.jsx)
**Sections:**

1. **Query Pipeline Timeline**
   - Visual timeline with 4 steps:
     1. Query Received
     2. Embedding Generated
     3. Vector Search
     4. LLM Generation
   - Show latency for each step
   - Highlight current/completed steps

2. **Retrieved Chunks**
   - Display each retrieved chunk in a card:
     - Source title (from metadata)
     - Similarity score (0.00-1.00, color-coded)
     - Chunk text preview
     - Dataset name badge

3. **LLM Details**
   - Token usage card:
     - Prompt tokens
     - Completion tokens
     - Total tokens
     - Estimated cost
   - Performance card:
     - Total latency
     - Model name
     - Temperature used
   
4. **Full Prompt** (expandable section)
   - Show complete prompt sent to LLM
   - Syntax highlighting or formatted text

**Update on every new query response.**

### 4.7 Dataset Manager Component (frontend/src/components/DatasetManager.jsx)
Modal or inline component for uploading datasets:
- File input (accept: .txt, .pdf, .docx, .md)
- Dataset name input
- Chunk size input
- Chunk overlap input
- Progress indicator during upload
- Success/error messages

### 4.8 Styling (Tailwind CSS)
Use the color scheme from the prototype:
- Primary blue: #2563eb
- Background: #f5f5f5
- Panel background: white
- Borders: #e5e7eb
- Text primary: #1f2937
- Text secondary: #6b7280

**Consistent spacing, rounded corners, subtle shadows.**

## Phase 5: Integration & Testing

### 5.1 End-to-End Flow Testing
Test the complete flow:
1. Start backend server
2. Start frontend dev server
3. Upload Aesop's Fables dataset
4. Wait for ingestion to complete
5. Send test queries
6. Verify responses make sense
7. Check observability data is populated
8. Test configuration changes (top-k, temperature)
9. Test dataset enable/disable
10. Test evaluation features

### 5.2 Sample Interactions to Test
- "What lesson does the tortoise teach us?"
- "Which fables involve foxes?"
- "Tell me about the boy who cried wolf"
- "What do the fables say about greed?"
- "Compare two different fables"

### 5.3 Configuration Experiments
- Change top-k from 3 to 5 → observe more chunks retrieved
- Increase temperature → observe more creative responses
- Disable a dataset → verify it's excluded from search
- Change chunk size → re-index and see different results

## Phase 6: Documentation

### 6.1 Main README.md
Create project README with:
- Project overview
- Features list
- Technology stack
- Setup instructions
- Usage guide
- Learning objectives
- Troubleshooting

### 6.2 Backend README
Include:
- API documentation
- Environment variables
- Architecture overview
- How to add new datasets
- How to switch embedding models

### 6.3 Frontend README
Include:
- Component structure
- State management approach
- How to customize UI
- Available scripts

## Important Implementation Notes

### Error Handling
- Validate file uploads (size, type)
- Handle missing API keys gracefully
- Catch embedding/LLM API errors
- Show user-friendly error messages
- Log errors for debugging

### Performance Optimization
- Batch embed documents (not one at a time)
- Cache embedding service (singleton)
- Show progress bars for long operations
- Lazy load large datasets

### User Experience
- Show loading states
- Disable buttons during processing
- Auto-save evaluations
- Persist configuration changes
- Provide helpful tooltips

### Code Quality
- Use type hints in Python
- Add docstrings to functions
- Use PropTypes or TypeScript in React
- Follow consistent naming conventions
- Keep functions small and focused

### Logging
- Log all RAG pipeline steps
- Log API requests/responses
- Log errors with full context
- Use appropriate log levels (DEBUG, INFO, ERROR)

## Testing Checklist

### Backend Tests
- [ ] Embedding service loads model correctly
- [ ] Chunking produces expected output
- [ ] Vector search returns relevant results
- [ ] RAG pipeline returns complete observability data
- [ ] File upload and ingestion works
- [ ] Dataset enable/disable filters correctly
- [ ] Configuration updates are applied

### Frontend Tests
- [ ] All panels render correctly
- [ ] Chat sends messages and displays responses
- [ ] Configuration changes update UI
- [ ] Dataset list updates on upload/delete
- [ ] Observability data displays correctly
- [ ] Sample questions populate input
- [ ] Evaluation buttons work

### Integration Tests
- [ ] Frontend can communicate with backend
- [ ] CORS is configured correctly
- [ ] File uploads work end-to-end
- [ ] Real-time updates work
- [ ] Error messages display properly

## Success Criteria

The prototype is complete when:
1. ✅ User can upload Aesop's Fables and query it
2. ✅ Responses are contextually relevant using RAG
3. ✅ All observability data is visible (embeddings, retrieval, LLM)
4. ✅ Configuration changes immediately affect results
5. ✅ Multiple datasets can be managed
6. ✅ Evaluation features work
7. ✅ UI is clean and intuitive
8. ✅ Documentation is complete

## Additional Learning Features (Optional Enhancements)

If time permits, consider adding:
- Compare different embedding models side-by-side
- Visualize embeddings in 2D (using UMAP/t-SNE)
- Add more evaluation metrics (RAGAS framework)
- Export chat history
- Save/load configuration presets
- Add more chunking strategies
- Implement query reformulation
- Add conversation memory

## Getting Started Command for Claude Code

Once you receive this prompt, start by:
1. Creating the project structure
2. Setting up the backend with requirements.txt
3. Implementing core services (embeddings, vector store, chunking)
4. Creating the RAG pipeline
5. Building API endpoints
6. Setting up the frontend
7. Integrating everything
8. Testing end-to-end

Focus on getting a minimal working version first, then iterate to add features.

## Resources

- Sentence Transformers: https://www.sbert.net/
- ChromaDB: https://docs.trychroma.com/
- FastAPI: https://fastapi.tiangolo.com/
- React: https://react.dev/
- Aesop's Fables: https://www.gutenberg.org/ (Project Gutenberg)

---

**Remember:** This is a learning prototype. Prioritize clarity and observability over optimization. Every step should be transparent so the user can understand how RAG works.

Good luck building!
