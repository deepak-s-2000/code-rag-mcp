# code-rag-mcp

**code-rag-mcp** is a Retrieval Augmented Generation (RAG) MCP server designed for codebases. It uses FastAPI to provide a scalable, context-aware backend for LLM-based coding assistants (such as Copilot), enabling them to search for existing methods and reuse code efficiently when creating new features.

## Features

- **Codebase Parsing**: Automatically parses supported files in a codebase to extract meaningful code chunks (functions/classes) using [tree-sitter](https://tree-sitter.github.io/tree-sitter/).
- **Chunk Storage**: Stores parsed code chunks with metadata in MongoDB for efficient retrieval.
- **Vector Embedding & FAISS Indexing**: Converts code chunks into vector embeddings and stores them in a FAISS index for fast similarity search.
- **API Endpoints**: FastAPI routes to parse codebases, retrieve code chunks, manage vectors, and enable semantic code search.
- **Contextual Code Search**: LLMs can query for similar code chunks to increase reusability and maintainability, improving feature development velocity.

## Architecture Overview

### 1. Codebase Parsing

- **File Types Supported**: `.py`, `.cpp`, `.java`, `.js`, `.csv`, `.json`
- **Parser**: `CodeBaseParser` traverses the codebase directory, using `FileParser` with tree-sitter grammars for supported languages.
- **Chunk Extraction**: AST nodes representing functions or classes are extracted as "chunks," retaining code, type, name, file path, and position.

### 2. Chunk Storage

- **MongoDB**: Chunks are inserted into a MongoDB collection via `TreeSitterChunksDAO`, supporting efficient retrieval and CRUD operations.

### 3. Vector Embedding & FAISS Store

- **Embedding**: Uses a configurable model (default: `all-MiniLM-L6-v2`) to encode code chunks into embeddings.
- **FAISS Index**: `VectorStore` manages a FAISS HNSW index for fast inner product searches on code embeddings. The index is persisted to disk (`app/rag/faiss/data/code_index.faiss`).
- **Batch Processing**: Chunks are embedded and added to FAISS in batches for scalability.

### 4. API Endpoints

- **/parse**: Parses the codebase and stores chunks.
- **/get-chunks-by-filename**: Retrieve all chunks for a specified file.
- **/delete-chunks-by-filename** and **/delete-all-chunks**: Manage chunk storage.
- **/create-vectors**: Create vector embeddings for stored chunks.
- **/search-vectors**: Search for similar code chunks by semantic similarity.
- **/delete-all-vectors**: Reset the FAISS index.

### 5. FastAPI Application

- **Middleware & CORS**: Supports CORS and timing middleware for performance logging.
- **Background Jobs**: Uses APScheduler for periodic tasks (e.g., refresh vectors).
- **Modularity**: All routes are organized with APIRouter for clean integration.

## How It Works

1. **Parse the Codebase**: POST to `/parse` to scan the codebase and extract code chunks.
2. **Create Embeddings**: POST to `/create-vectors` to embed all chunks and index them in FAISS.
3. **Semantic Search**: POST to `/search-vectors` to retrieve existing code similar to a query or feature request.
4. **Reuse Code**: The system surfaces reusable methods/classes, boosting productivity for Copilot and other LLM agents.

## Folder Structure

- `app/core/CodeBaseParser.py`: Codebase traversal and chunk extraction.
- `app/helpers/file_parser.py`: Language-specific parsing and AST chunking.
- `app/db/tree_sitter_chunks_DAO.py`: MongoDB chunk management.
- `app/rag/vector_embedding.py`: Embedding and FAISS index management.
- `app/rag/faiss/vector_store.py`: FAISS vector store implementation.
- `app/api/routes/parse_codebase.py`, `app/api/routes/rag_api.py`: FastAPI endpoints.

## Configuration

- **config.py**: Change application settings, MongoDB URI, accepted file types, embedding model, and FAISS index path.

## Usage

Run the FastAPI server and interact via the documented API endpoints to parse codebases, manage vectors, and enable context-aware code search for LLM agents.

---

**License**: Apache License 2.0 – see [LICENSE](LICENSE) for details.