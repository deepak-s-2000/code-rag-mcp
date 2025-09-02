class RAGConfig:
    def __init__(self):
        
        self.app_name = "RAG Application"
        self.app_version = "1.0.0"
        self.debug = True

        self.api_base_url = "http://127.0.0.1:8000"
        self.mongo_uri = "mongodb://localhost:27017"
        self.db_name = "rag_db"
        self.collection_name = "documents"
        
        self.accepted_file_types = [
            ".py",
            ".cpp",
            ".java",
            ".js",
            ".csv",
            ".json"
        ]
        self.codebase_path = "codebase"

        self.embedding_model = "all-MiniLM-L6-v2"
        self.hnsw_ef_construction = 200
        self.hnsw_ef_search = 100
        self.faiss_filepath = "app/rag/faiss/data/code_index.faiss"