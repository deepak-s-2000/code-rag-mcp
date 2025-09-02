import numpy as np
from app.config import RAGConfig
from app.beans.embedding_model import EmbeddingModelSingleton
from app.rag.faiss.vector_store import VectorStore
from app.db.tree_sitter_chunks_DAO import TreeSitterChunksDAO
import asyncio
import logging
import os
logging.basicConfig(level=logging.INFO)
class VectorEmbedding:
    def __init__(self):
        self.model_name = RAGConfig().embedding_model
        self.model = EmbeddingModelSingleton.get_model(self.model_name)
        self.faiss_index = None
        self.tree_sitter_dao = TreeSitterChunksDAO()

    async def load_faiss_index(self, dimension):
        index_path = RAGConfig().faiss_filepath
        if os.path.exists(index_path):
            self.faiss_index = VectorStore(dimension=dimension)
            await self.faiss_index.load_index()
        else:
            self.faiss_index = VectorStore(dimension=dimension)
    
    async def embed_text(self, text: str) -> list[float]:
        return self.model.encode([text], convert_to_numpy=True)

    async def clear_faiss_index(self):
        index_path = RAGConfig().faiss_filepath
        if os.path.exists(index_path):
            os.remove(index_path)

    async def add_embedding_to_faiss(self, text: str):
        logging.info(f"Adding embedding for text: {text[:30]}...")
        embeddings = await self.embed_text(text)
        await self.load_faiss_index(embeddings.shape[1])
        if self.faiss_index is not None:
            await self.faiss_index.add_vectors(embeddings)
        await self.faiss_index.save_index()
        
    
    async def create_vector_store(self):
        # Load or create index ONCE
        self.faiss_index = VectorStore(dimension=384)
        all_chunks = []
        async for chunk_batch in self.tree_sitter_dao.get_chunks_by_batch(batch_size=100):
            for chunk in chunk_batch:
                logging.info(f"debug chunk: {chunk.vector_id}: {chunk.name}...")
                if chunk.content:
                    all_chunks.append(chunk.content)
        if all_chunks:
            embeddings = self.model.encode(all_chunks, convert_to_numpy=True)
            await self.faiss_index.add_vectors(embeddings)
        await self.faiss_index.save_index()
    
    async def search_embeddings(self, query: str, k: int = 5) -> tuple[np.ndarray, np.ndarray]:
        query_embedding = await self.embed_text(query)
        logging.info(f"Searching for query: {query} with embedding shape: {query_embedding.shape}")
        await self.load_faiss_index(query_embedding.shape[1])
        logging.info(f"FAISS index total vectors: {self.faiss_index.index.ntotal}")
        if self.faiss_index is not None:
            distances, indices = await self.faiss_index.search(query_embedding, k)
            logging.info(f"indices: {indices}, distances: {distances}")
            return distances, indices
        return np.array([]), np.array([])

    async def search(self, query: str, k: int = 5) -> tuple[np.ndarray, np.ndarray]:
        distances, indices = await self.search_embeddings(query, k)
        if indices.size == 0:
            return np.array([]), np.array([])
        op = []
        for i in range(len(indices[0])):
            vector_id = int(indices[0][i])
            if vector_id == -1:
                logging.warning(f"Invalid vector ID: {vector_id} at index {i}, skipping.")
                continue  # skip invalid result
            chunk = await self.tree_sitter_dao.get_chunk_by_vector_id(vector_id)
            if chunk:
                logging.info(f"Found chunk: {chunk.name} in file: {chunk.file_path}")
                op.append((chunk.get_chunk_content(), float(distances[0][i])))
        return op