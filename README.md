# RAG Learning Prototype

A complete Retrieval-Augmented Generation (RAG) system built with Aesop's Fables for learning and experimentation. This prototype provides full observability into every step of the RAG pipeline.

## Features

- 🚀 **Complete RAG Pipeline**: Embedding generation → Vector search → LLM generation
- 📊 **Full Observability**: Track latency, tokens, costs, and relevance scores for every query
- 📚 **Dataset Management**: Upload and manage multiple datasets with different chunking strategies
- ⚙️ **Configurable**: Adjust chunk size, top-k, temperature, and model in real-time
- 📈 **Evaluation Tools**: Manual ratings and batch evaluation with test questions
- 🎨 **Modern UI**: Clean three-panel interface built with React + TypeScript + Tailwind

## Technology Stack

### Backend
- **FastAPI** (Python 3.10+) - High-performance API framework
- **ChromaDB** - Vector database for embeddings
- **Sentence Transformers** (`all-MiniLM-L6-v2`) - Local, free embeddings
- **OpenAI API** - LLM for response generation
- **SQLite** - Application data storage

### Frontend
- **React 18** with TypeScript
- **Vite** - Fast build tool
- **Tailwind CSS** - Utility-first styling
- **Axios** - HTTP client
- **Lucide React** - Icon library

## Project Structure

```
RAG-POC/
├── backend/
│   ├── app/
│   │   ├── core/          # Core services (embeddings, vector store, LLM, RAG pipeline)
│   │   ├── services/      # Business logic (chunking, ingestion, evaluation)
│   │   ├── api/endpoints/ # API endpoints
│   │   ├── models/        # Data models and database
│   │   └── main.py        # FastAPI application
│   ├── data/              # Data files and databases
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── services/      # API service layer
│   │   ├── types/         # TypeScript types
│   │   └── App.tsx        # Main application
│   └── .env
├── Aesop_fables.txt       # Dataset file
└── README.md
```

## Setup Instructions

### Prerequisites

- Python 3.10+
- Node.js 18+
- OpenAI API key

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create and activate virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   - Edit `backend/.env`
   - Add your OpenAI API key: `OPENAI_API_KEY=your-key-here`

5. **Start the backend server**:
   ```bash
   python -m app.main
   ```

   The API will be available at `http://localhost:8000`
   API documentation: `http://localhost:8000/docs`

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start the development server**:
   ```bash
   npm run dev
   ```

   The app will be available at `http://localhost:5173`

## Usage Guide

### 1. Upload Dataset

1. Click "Add" button in the Configuration panel (left side)
2. Select a file (.txt, .pdf, .docx, .md)
3. Set dataset name, chunk size, and overlap
4. Click "Upload"
5. Wait for processing to complete

**Using the included Aesop's Fables**:
- File is located at: `../Aesop_fables.txt`
- Recommended settings:
  - Chunk size: 500
  - Chunk overlap: 50
  - Strategy: Sentences

### 2. Ask Questions

1. Use sample questions or type your own
2. Enable/disable datasets in Configuration panel
3. Adjust retrieval settings (Top-K) and LLM settings (temperature, model)
4. Send query and observe:
   - Chat response (center panel)
   - Observability data (right panel)

### 3. View Observability

The right panel shows:
- **Pipeline Timeline**: Latency for each step
- **Retrieved Chunks**: Relevant passages with similarity scores
- **LLM Details**: Token usage, costs, model parameters
- **Full Prompt**: Complete prompt sent to the LLM

### 4. Evaluate Responses

- Click thumbs up/down on assistant messages
- Evaluations are saved for analysis
- View evaluation history via API: `GET /api/evaluations`

### 5. Run Batch Evaluation

Use the test questions file:
```bash
curl -X POST http://localhost:8000/api/evaluate/batch \
  -H "Content-Type: application/json" \
  -d @backend/data/test_questions.json
```

## Configuration Options

### Chunking Settings
- **Chunk Size** (100-2000 chars): Size of text chunks
- **Chunk Overlap** (0-500 chars): Overlap between consecutive chunks
- **Strategy**: `sentences` (preserves sentence boundaries) or `characters`

### Retrieval Settings
- **Top-K** (1-20): Number of chunks to retrieve
- **Min Score** (0.0-1.0): Minimum similarity threshold

### LLM Settings
- **Model**: `gpt-4o`, `gpt-4o-mini`, `gpt-3.5-turbo`
- **Temperature** (0.0-2.0): Creativity/randomness
- **Max Tokens** (50-4000): Maximum response length

## API Endpoints

### Chat
- `POST /api/chat` - Process RAG query

### Datasets
- `GET /api/datasets` - List all datasets
- `POST /api/datasets/upload` - Upload new dataset
- `PATCH /api/datasets/{id}` - Update dataset
- `DELETE /api/datasets/{id}` - Delete dataset

### Configuration
- `GET /api/config` - Get current configuration
- `PATCH /api/config` - Update configuration

### Evaluation
- `POST /api/evaluate` - Submit evaluation
- `GET /api/evaluations` - List evaluations
- `POST /api/evaluate/batch` - Run batch evaluation

### Health
- `GET /health` - Health check

## Learning Objectives

This prototype helps you understand:

1. **Embeddings**: How text is converted to vectors
2. **Vector Search**: How similar documents are retrieved
3. **Prompt Engineering**: How context is incorporated
4. **RAG Trade-offs**: Impact of chunk size, top-k, etc.
5. **Cost Analysis**: Token usage and API costs
6. **Evaluation**: Measuring RAG quality

## Troubleshooting

### Backend won't start
- Ensure Python 3.10+ is installed
- Activate virtual environment
- Check all dependencies are installed
- Verify `.env` file exists with API key

### Frontend won't start
- Ensure Node.js 18+ is installed
- Run `npm install` again
- Check `.env` file exists

### Can't connect to API
- Ensure backend is running on port 8000
- Check CORS settings in `backend/.env`
- Verify `VITE_API_BASE_URL` in `frontend/.env`

### Model loading fails
- First run downloads the embedding model (~100MB)
- Ensure internet connection is available
- Check disk space in `backend/data/`

### Out of memory
- Reduce chunk size
- Process smaller datasets
- Reduce top-k value

## Performance Tips

- Use `gpt-4o-mini` or `gpt-3.5-turbo` for faster/cheaper responses
- Adjust chunk size based on content (smaller for dense text)
- Use sentence-based chunking for better context
- Enable only necessary datasets
- Lower top-k for faster retrieval

## Cost Estimates

Approximate costs (per 1M tokens):
- GPT-4o: $2.50 input / $10 output
- GPT-4o-mini: $0.15 input / $0.60 output
- GPT-3.5-turbo: $0.50 input / $1.50 output

Typical query cost: $0.001 - $0.01

## Future Enhancements

- [ ] Support for more embedding models
- [ ] Conversation memory/history
- [ ] Advanced evaluation metrics (RAGAS)
- [ ] Query reformulation
- [ ] Multi-query retrieval
- [ ] Re-ranking
- [ ] Export functionality
- [ ] Visualization of embeddings (UMAP/t-SNE)

## License

MIT License - Feel free to use for learning and experimentation

## Contributing

This is an educational prototype. Feel free to fork and experiment!

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review API documentation at `/docs`
3. Examine browser console and backend logs

---

**Happy Learning! 🚀**
